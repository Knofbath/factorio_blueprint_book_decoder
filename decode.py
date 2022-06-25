#!/usr/bin/env python3

import json
import sys
import io
import argparse

import os
import shutil
import zlib
import base64


def verbose(*args):
    if not opt.silent:
        print(*args, file=sys.stderr, flush=True)


def decode(string):
    return json.loads(zlib.decompress(
        base64.b64decode(string[1:])).decode('utf8'))


def encode(dict):
    return '0' + base64.b64encode(zlib.compress(bytes(json.dumps(dict), 'utf8'))).decode('utf8')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description="Convert a factorio blueprint book to json")

    parser.add_argument("-s", "--silent", action="store_true", dest="silent",
                        help="Stop verbose output on STDERR", default=False),

    parser.add_argument("-i", "--input", nargs="?", dest="input",
                        help="Blueprint book file path", default="./example_blueprint_books/general")

    parser.add_argument("-o", "--output", nargs="?", dest="output",
                        help="Folder output for the json", default="blueprint_book_json")

    parser.add_argument("-f", "--force", action="store_true", dest="force",
                        help="Force overwrite of existing output folder", default=False)

    opt = parser.parse_args()

    # Check if the input file exists
    if not os.path.exists(opt.input):
        print(f"Input file '{opt.input}' does not exist")
        sys.exit(1)

    # Add trailing slash to output folder if not present
    if not opt.output.endswith("/"):
        opt.output += "/"

    # Check if the output folder exists
    if os.path.exists(opt.output):
        if not opt.force:
            print(f"Output folder '{opt.output}' already exists")
            print("Use --force or -f to overwrite it")
            sys.exit(1)
        else:
            shutil.rmtree(opt.output)
            os.mkdir(opt.output)
    else:
        os.mkdir(opt.output)

    verbose(f"file: {opt.input}")

    # ==== Decoding ====

    # import the blueprint book:
    with open(opt.input, 'r') as f:
        original_bp_string = f.read()

    # decode the blueprint book:
    bp_json = decode(original_bp_string)
    verbose("file decoded successfully")

    # ==== Writing ====

    # Writing the json file:
    with open(f'{opt.output}book.json', 'w') as f:
        json.dump(bp_json, f)
        verbose(f'Saved book.json at {opt.output}')


    bp_json = bp_json["blueprint_book"]

    if "blueprints" not in bp_json:
        print("Invalid blueprint book, no 'blueprint_book.blueprints' key found")
        sys.exit(1)

    blueprints = bp_json["blueprints"]

    if not len(blueprints):
        print("No blueprints found in the blueprint book")
        sys.exit(1)

    # Display the blueprints:

    if not opt.silent:
        verbose(f"\nThe book has {len(blueprints)} blueprints:\n")
        for bp in blueprints:
            blueprint = bp["blueprint"]
            verbose(" - " + blueprint["label"])
        verbose("")

    # Save each blueprint:
    os.mkdir(f'{opt.output}blueprints')
    for bp in blueprints:
        blueprint = bp["blueprint"]
        blueprint_file_name = "".join(c for c in blueprint["label"] if c.isalnum() or c in "-_")
        with open(f'{opt.output}blueprints/{blueprint_file_name}.json', 'w') as f:
            json.dump(bp, f)
        with open(f'{opt.output}blueprints/{blueprint_file_name}', 'w') as f:
            f.write(encode(bp))

    verbose(f"Saved blueprints at {opt.output}blueprints")
