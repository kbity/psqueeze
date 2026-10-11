#!/usr/bin/env python3
import sys
import squeeze

def main():
    print("File squeezer version 1.0   10/10/26 (original author: R. Greenlaw, Python clone by Mari Kepler)\n")

    interactive_mode = True
    fno = False
    for arg in sys.argv[1:]:
        if arg.startswith("--filename="):
            fno = True
            fn = arg.replace("--filename=", "")
        else:
            interactive_mode = False
            if not fno:
                fn = arg
            try:
                with open(arg, "rb") as i:
                    with open(arg+".SQ", "wb") as o:
                        print(f"{arg} -> {arg}.SQ: ", end='')
                        o.write(squeeze.compress(i.read(), fn, log=True))
            except FileNotFoundError:
                print(f"{arg} -> {arg}.SQ: Can't open {arg} for input")

    if interactive_mode:
        print("Enter file names, one line at a time, or type <RETURN> to quit.")
    while interactive_mode:
        fn = input("*")
        if fn == "":
            interactive_mode = False
        else:
            try:
                with open(fn, "rb") as i:
                    with open(fn+".SQ", "wb") as o:
                        o.write(squeeze.compress(i.read(), fn.strip(), log=True))
            except FileNotFoundError:
                print(f"{fn} -> {fn}.SQ: Can't open {fn} for input")