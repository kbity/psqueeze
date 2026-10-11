from . import huffman
from . import bittools

delim = 144

"""
Squeeze File Header:
76 FF - File Identifier, fixed for all SQ files
uint16le - Checksum, calculated by totaling the value of every byte and using the lowest 16 bits
ASCII String (sample.txt<0x00>) - Null-Terminiated filename. May contain a directory
uint16le - Huffman Tree node count
[huffman tree]
[huffman coded RLE-compressed data]
"""

def serialize(node: huffman.Node, nodes=None):
    parent = False
    if nodes is None:
        parent = True
        nodes = []

    if node.left is None and node.right is None:
        return -(node.symbol + 1)

    index = len(nodes) // 2
    nodes.append(None)
    nodes.append(None)

    left = serialize(node.left, nodes)
    right = serialize(node.right, nodes)
    nodes[index*2] = left
    nodes[index*2+1] = right

    if parent:
        return nodes
    else:
        return index

def serial_to_squeeze_tree(serial: list, nc: int):
    hufftree = bytearray(int(nc-1).to_bytes(2, "little"))
    for val in serial:
        hufftree.extend(val.to_bytes(2, "little", signed=True))
    return hufftree

def huffman_encode(data: bytes, huffman_tree: dict):
    huffbuffer = []
    cdat = bytearray()

    for b in data: # itterate over data and get huffman codes
        huffbuffer.extend(huffman_tree[b])
        while len(huffbuffer) >= 8: # dump huffman codes into octet stream
            cdat.append(bittools.boollist_to_int_var(huffbuffer[0:8][::-1])) # The Format Packs Huffman LSB, not MSB
            huffbuffer = huffbuffer[8:]

    huffbuffer.extend(huffman_tree[256]) # add EOF marker

    while len(huffbuffer) >= 8: # dump huffman codes into octet stream
        cdat.append(bittools.boollist_to_int_var(huffbuffer[0:8][::-1])) # The Format Packs Huffman LSB, not MSB. You needed to see this twice xD
        huffbuffer = huffbuffer[8:]

    if huffbuffer: # flush anything remaining
        while len(huffbuffer) < 8:
            huffbuffer.append(False) # pad
        cdat.append(bittools.boollist_to_int_var(huffbuffer[::-1]))

    return cdat

def compress(raw: bytes, filename: str = "file.bin", log: bool = False):
    # USQ-compatible compressor

    if log:
        print("analyzing, ", end='') # first stage, make checksum and RLE encode

    # generate checksum and run-length encode
    crc = 0 # cumulative value of all bytes, then the lower 2 bytes are stored

    rledata = bytearray()

    seek = 0
    eof=False

    while seek < len(raw): # run length encoder and checksum generator
        b = raw[seek]
        eof = True if seek+2 >= len(raw) else False

        if b == delim:
            rledata.append(b)
            rledata.append(0)
            crc+=b

        elif not eof and b == raw[seek+1] and b == raw[seek+2]: # checks for runs greater than 2
            run=1 # set to 1
            crc+=b

            while seek+1 < len(raw) and raw[seek+1] == b and run <= 254: # ensure the seek doesn't break the 8-bit integer limit
                run+=1
                seek+=1
                crc+=raw[seek]

            rledata.append(b)
            rledata.append(delim)
            rledata.append(run)

        else:
            rledata.append(b)
            crc+=b

        seek+=1

    #print(crc)
    crc = crc%65536

    #open("dump.rle", "wb").write(rledata)

    sq = bytearray(b'v\xff')
    sq.extend(crc.to_bytes(2, 'little')) # SQ is little endian and that's all i know.
    sq.extend(filename.encode("ascii")) # add filename
    sq.append(0) # null terminator

    # compress here
    if log:
        print("squeezing, ", end='') # second stage, make huffman tree, serialize and encode it, and

    if not raw:
        sq.extend(b'\x00\x00')
        return sq # empty file handling

    freq = huffman.freq_eval(rledata, True) # True adds a node for the EOF, which appears exactly once.

    #print(freq) - debug: print frequency table

    root = huffman.build_huffman_tree(freq)
    huffman_codes = huffman.generate_huffman_codes(root)

    nodes = serialize(root)
    hufftree = serial_to_squeeze_tree(nodes, len(huffman_codes))

    #print(huffman_codes) - debug: print huffman codes

    #for n in huffman_codes: - debug: print huffman code lengths
    #    print(len(huffman_codes[n]))

    #print(nodes) - debug: print serialized huffman tree

    #print(hufftree) - debug: print encoded serialized huffman tree

    sq.extend(hufftree) # add tree. perfectly devoid of any codes unused

    cdat = huffman_encode(rledata, huffman_codes) # finally, encode the data with our tree
    sq.extend(cdat) # add compressed data to the thingy

    if log:
        print("done.")

    return sq # finally, give output

def huffman_decode(tree: bytes):
    serial = []
    for p in range(0, len(tree), 2):
        serial.append(int.from_bytes(tree[p:p+2], "little", signed=True)) # unpack huffman tree from bitstream

    #print(serial) - debug: print out serialized tree
    return serial

def dehuffman(huffdat: bytes, huffman_points: list):
    buffer_floor = 64 # keep at least 64 bits of data loaded into the buffer. This gives the decoder a max code length of 64. smaller size = faster, but less compatible with SQ files.
    decode_buffer = []
    seek = 0 # start at index 0
    output = bytearray()

    while True: # continue forever until a break is called

        while len(decode_buffer) < buffer_floor and seek < len(huffdat): # refill buffer if its possible
            decode_buffer.extend(bittools.byte_to_boollist(huffdat[seek])[::-1])
            seek+=1

        codelen = 0 # length of code, index position in decode_buffer
        pointed_index = 0 # points to the location in huffman points

        while True:
            if huffman_points[(pointed_index*2)+int(decode_buffer[codelen])] < 0:
                val = -(huffman_points[(pointed_index*2)+int(decode_buffer[codelen])]+1)
                if val == 256: # EOF
                    return output # exit function
                output.append(val)
                decode_buffer = decode_buffer[codelen+1:] # consume bytes
                break
            else:
                pointed_index = huffman_points[(pointed_index*2)+int(decode_buffer[codelen])]
            codelen+=1

def unrle(rledat: bytes):
    seek = 0
    crc = 0
    raw = bytearray()

    while seek < len(rledat):

        b = rledat[seek]
        if b == delim:

            if rledat[seek+1] == 0: # handle literals
                raw.append(b)
                crc+=b
                seek+=1

            else:
                rpt = rledat[seek+1]-1 # repeats, subtracted by one since it was already emmited once
                rsb = rledat[seek-1] # run subpect
                crc+=rpt*rsb
                dbo = bytearray([rsb])*rpt # duplicated bytes object
                raw.extend(dbo)
                seek+=1

        else:
            raw.append(b)
            crc+=b

        seek+=1

    return raw, crc%65536

def getfilename(sq: bytes):
    if not sq.startswith(b'v\xff'):
        raise ValueError("Not a Squeeze Archive!")
    chksum = sq[2]+sq[3]*256
    fn = ""
    seek = 4

    while seek < len(sq): # extract filename
        b = sq[seek]
        if b:
            fn+=chr(b)
            seek+=1
        else:
            seek+=1
            break
    return fn

def uncompress(sq: bytes, returnfilename: bool = False, log: bool = False):
    if not sq:
        raise ValueError("Expected Squeeze Archive, got empty file!")
    if not sq.startswith(b'v\xff'):
        raise ValueError(f"Not a Squeeze Archive! 0x76 0xFF expected, but got {hex(sq[0])} {hex(sq[1])}")
    chksum = sq[2]+sq[3]*256
    fn = ""
    seek = 4

    while seek < len(sq): # extract filename
        b = sq[seek]
        if b:
            fn+=chr(b)
            seek+=1
        else:
            seek+=1
            break
    # after this, seek should be on the huffman tree count node
    huffsize = sq[seek]+sq[seek+1]*256 # little endian, huh?

    if log:
        print("unsqueezing, ", end='') # echo log

    seek+=2 # align to start of tree

    if huffsize == 0: # if the tree size is 0, QUIT!
        if returnfilename:
            return b'', fn
        else:
            return b''
    else:
        hufftree = sq[seek:seek+(huffsize*4)]

    seek+=(huffsize*4)

    huffman_points = huffman_decode(hufftree)

    #print(fn, huffsize)

    #print(hufftree)

    #print(huffman_points)

    rledata = dehuffman(sq[seek:], huffman_points)

    raw, crc = unrle(rledata)
    if crc != chksum:
        print("Error: checksum does not match!")

    if log:
        print("done.") # echo log done.

    if returnfilename:
        return bytes(raw), fn
    else:
        return bytes(raw)
