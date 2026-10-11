import heapq

class Node:
    def __init__(self, symbol=None, frequency=None, left=None, right=None):
        self.symbol = symbol
        self.frequency = frequency
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.frequency < other.frequency

def freq_eval(dat: bytes, eof: bool = False):
    # generate frequency table for huffman coding
    freqtable = []
    for _ in range(256):
        freqtable.append(0)

    if eof:
        freqtable.append(1) # this adds a node with value 256, which marks the end of the squeeze file

    for b in dat:
        freqtable[b]+=1
    return freqtable

def build_huffman_tree(freq_table):
    # Create a priority queue of nodes
    priority_queue = []
    for b, o in enumerate(freq_table):
        if o: # filter entries with zero occurences
            priority_queue.append(Node(b, o))

    heapq.heapify(priority_queue)

    # Build the Huffman tree
    while len(priority_queue) > 1:
        left_child = heapq.heappop(priority_queue)
        right_child = heapq.heappop(priority_queue)
        merged_node = Node(frequency=left_child.frequency + right_child.frequency)
        merged_node.left = left_child
        merged_node.right = right_child
        heapq.heappush(priority_queue, merged_node)

    return priority_queue[0]

def generate_huffman_codes(node, code=[], huffman_codes=None):
    # recursively generate the huffman table
    if huffman_codes is None:
        huffman_codes = {}

    if node is not None:
        if node.symbol is not None:
            huffman_codes[node.symbol] = code

        generate_huffman_codes(node.left, code+[False], huffman_codes)
        generate_huffman_codes(node.right, code+[True], huffman_codes)

    return huffman_codes

# Given example
#chars = ['a', 'b', 'c', 'd', 'e', 'f']
#freq = [4, 7, 15, 17, 22, 42]

# Build the Huffman tree
#root = build_huffman_tree(chars, freq)

# Generate Huffman codes
#huffman_codes = generate_huffman_codes(root)

# Print Huffman codes
#for char, code in huffman_codes.items():
#    print(f"Character: {char}, Code: {code}")

# code taken from https://www.geeksforgeeks.org/dsa/huffman-coding-in-python/
# Modified to use a frequency table instead