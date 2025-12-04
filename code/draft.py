#!/usr/bin/env python3

import sys
import subprocess
import datetime

from helpers import (
    FAILURE, INFO,
    LAYERS,
    parse_metadata_header,
    write_markdown_file,
)

EDITOR = "nvim"


def main():
    # ensure directory exists
    drafts_layer = LAYERS["drafts"]
    drafts_layer.ensure_exists()

    # default values
    filename_str = datetime.date.today().isoformat()
    word_count_goal = "500"
    
    # argument parsing
    args = sys.argv[1:]
    
    if args:
        first_arg = args[0]

        # CASE 1: word count goal
        if first_arg.isdigit():
            word_count_goal = first_arg

        # CASE 2: filename
        else:
            filename_str = first_arg

            if len(args) > 1 and args[1].isdigit():
                word_count_goal = args[1]

    if not filename_str.endswith(".md"):
        filename_str += ".md"

    file_path = drafts_layer.directory / filename_str

    # file creation
    if not file_path.exists() or file_path.stat().st_size == 0:
        print(f"    -> {INFO} draft: {file_path.name}")

        try:
            metadata = {
                "aliases": [],
                "afterlife": "",
                "is_dead": False,
                "type": ["draft"],
                "summary": "",
                "word_count_goal": int(word_count_goal),
                "word_count": 0,
            }
            write_markdown_file(file_path, metadata, "")
        except IOError as e:
            print(f"    -> {FAILURE} issue creating file: {e}")
            sys.exit(1)
    else:
        print(f"    -> {INFO} draft: ++{file_path.name}")


    # open editor
    try:
        subprocess.call([EDITOR, str(file_path)])
    except FileNotFoundError:
        print(f"    -> {FAILURE} could not find editor: '{EDITOR}'.")
        sys.exit(1)

    # post processing
    update_word_count(file_path)


def update_word_count(file_path):
    if not file_path.exists():
        return

    try:
        metadata, body = parse_metadata_header(file_path)
        if not metadata:
            metadata = {}

        word_count = len(body.split())
        metadata["word_count"] = word_count
        
        write_markdown_file(file_path, metadata, body)
        
        print(f"    -> {INFO} words: {word_count}")

    except Exception as e:
        print(f"    -> {FAILURE} issue updating word_count: {e}")


if __name__ == "__main__":
    main()