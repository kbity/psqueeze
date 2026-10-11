#!/usr/bin/env python3
import sys
from . import squeeze

def main():
    print("File unsqueezer version 1.0   10/10/26 (original author: R. Greenlaw, Python clone by Mari Kepler)\n")

    interactive_mode = True
    fno = False
    for arg in sys.argv[1:]:
        if arg.startswith("--filename="):
            fno = True
            ofn = arg.replace("--filename=", "")
        interactive_mode = False
        try:
            with open(arg, "rb") as i:
                dat = i.read()
                if not fno:
                    ofn = squeeze.getfilename(dat)
                with open(ofn, "wb") as o:
                    print(f"{arg} -> {ofn}: ", end='')
                    o.write(squeeze.decompress(dat, log=True))
        except FileNotFoundError:
            print(f"Can't open {arg}")

    if interactive_mode:
        print("Enter file names, one line at a time, or type <RETURN> to quit.")
    while interactive_mode:
        fn = input("*")
        if fn == "":
            interactive_mode = False
        else:
            try:
                with open(fn, "rb") as i:
                    dat = i.read()
                    ofn = squeeze.getfilename(dat)
                    with open(ofn, "wb") as o:
                        o.write(squeeze.decompress(dat, log=True))
            except FileNotFoundError:
                print(f"Can't open {fn}")