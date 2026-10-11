# psqueeze
Pure Python implementation of Richard Greenlaw's Squeeze compression format

## Usage
```
import squeeze

squeeze.compress(bytes, filename = "file.bin", log = False)
# bytes is required, it is an uncompressed bytes object
# fn is the filename to be written to the squeeze archive
# log enables/disables the compressor's internal status logging

squeeze.uncompress(bytes, returnfilename = False, log = False)
# bytes is required, it is an uncompressed bytes object
# fn is the filename to be written to the squeeze archive
# log enables/disables the decompressor's internal status logging
```

## CLI
```
$ psq
# compresses a file or multiple, supports bulk operations and an interactive mode.
# filename is written to current path + .SQ
# --filename=NAME can be added before every file to change the output path of extraction

$ pusq
# decompresses a file or multiple, supports bulk operations and an interactive mode.
# filename is written to the path specified in the header, unless a --filename=NAME is put before the path
```
