#!/usr/bin/env python3

import sys
import os
import subprocess
import shutil
import pathlib

# Help
def usage():
    print(f"usage: python {sys.argv[0]} <input file list> <output directory>")

def lineCount(file):
    return int(subprocess.check_output(["/usr/bin/wc", "-l", f"{file}"]).split()[0])

# Main guts
def main():
    try:
        if not os.path.isfile(sys.argv[1]):
            print(f'{sys.argv[1]} is not a valid file.\n')
            sys.exit()
        if not os.path.isdir(sys.argv[2]):
            create_directory = input(f'{sys.argv[2]} is not a directory. Do you want to create it? (Y or N)')
            if create_directory.upper() == 'Y':
                try:
                    pathlib.Path(sys.argv[2]).mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    print('You do not have the correct permissions to receate the directory. Please try a different path or create manually')
                    sys.exit()
            else:
                print('Please specify a valid directory and try again')
                sys.exit()
        input_list = open(sys.argv[1], "r")
        destination = sys.argv[2]
    except IndexError:
        usage()
        sys.exit()

    if sys.platform == 'darwin':
        splitlen_bin = "hashcat-utils/bin/splitlen.app"
        rli_bin = "hashcat-utils/bin/rli.app"
    else:
        splitlen_bin = "hashcat-utils/bin/splitlen.bin"
        rli_bin = "hashcat-utils/bin/rli.bin"

    # Get list of wordlists from <input file list> argument
    for wordlist in input_list:
        wordlist = wordlist.strip()
        print(wordlist)

        # Parse wordlists by password length into "optimized" <output directory>
        if len(os.listdir(destination)) == 0:
            splitlenProcess = subprocess.Popen(f"{splitlen_bin} {destination} < {wordlist}", shell=True).wait()
        else:
            if not os.path.isdir("my_splits/splitlen"):
                os.mkdir("my_splits/splitlen")
            splitlenProcess = subprocess.Popen(f"{splitlen_bin} my_splits/splitlen < {wordlist}", shell=True).wait()

            # Copy unique passwords into "optimized" <output directory>
            for f in os.listdir("my_splits/splitlen"):
                if not os.path.isfile(f"{destination}/{f}"):
                    shutil.copyfile(f"my_splits/splitlen/{f}", f"{destination}/{f}")
                else:
                    rliProcess = subprocess.Popen([rli_bin, f"my_splits/splitlen/{f}", "my_splits/splitlen.out", f"{destination}/{f}"]).wait()
                    if lineCount("my_splits/splitlen.out") > 0:
                        with open("my_splits/splitlen.out", "r", errors="replace") as splitlen_file, open(f"{destination}/{f}", "a") as destination_file:
                            for line in splitlen_file.read().splitlines():
                                destination_file.write(f"{line.strip()}\n")

    # Clean Up
    if os.path.isdir("my_splits/splitlen"):
        shutil.rmtree('my_splits/splitlen')
    if os.path.isfile("my_splits/splitlen.out"):
        os.remove("my_splits/splitlen.out")


# Standard boilerplate to call the main() function
if __name__ == '__main__':
    main()
