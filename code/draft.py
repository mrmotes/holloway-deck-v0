#!/usr/bin/env python3

import sys
import argparse
import subprocess
import datetime

from helpers import (
    FAILURE, INFO,
    LAYERS,
    parse_metadata_header,
    sanitize_filename,
    write_markdown_file,
)

EDITOR = "nvim"


def main():
    parser = argparse.ArgumentParser(
        prog="draft",
        description="create a new draft file or open an existing one",
        add_help=True
    )
    parser.add_argument(
        "filename",
        nargs="?",
        default=None,
        help="filename for the draft (default: today's date is ISO format 'yyyy-mm-dd.md')"
    )
    parser.add_argument(
        "word_count_goal",
        nargs="?",
        type=int,
        default=500,
        help="the word count goal for the file (default: 500)"
    )
    parser.add_argument(
        "-s", "--select",
        action="store_true",
        help="open fzf to select and edit a live draft"
    )

    parsed_args = parser.parse_args()

    # ensure directory exists
    drafts_layer = LAYERS["drafts"]
    drafts_layer.ensure_exists()

    # --select mode: open fzf to pick a draft
    if parsed_args.select:
        selected = drafts_layer.select_file(multi=False)
        if not selected:
            print(f"    -> {INFO} no draft selected")
            sys.exit(0)
        file_path = drafts_layer.directory / selected[0]
        print(f"    -> {INFO} opening draft: {file_path.name}")
        try:
            subprocess.call([EDITOR, str(file_path)])
        except FileNotFoundError:
            print(f"    -> {FAILURE} editor not found: {EDITOR}")
            sys.exit(1)
        update_word_count(file_path)
        sys.exit(0)

    # default values
    #TODO - update this so that it always prefixes the filename with the date
    # today = datetime.date.today().isoformat()
    # filename_str = today + parsed_args.filename if parsed_args.filename else today

    filename_str = parsed_args.filename or datetime.date.today().isoformat()
    sanitized_filename, requires_alias = sanitize_filename(filename_str)
    
    word_count_goal = parsed_args.word_count_goal

    file_path = drafts_layer.directory / sanitized_filename

    # file creation
    if not file_path.exists() or file_path.stat().st_size == 0:
        print(f"    -> {INFO} creating draft: {file_path.name}")

        try:
            metadata = {
                "aliases": [filename_str] if requires_alias else [],
                "afterlife": None,
                "is_dead": False,
                "type": ["draft"],
                "summary": None,
                "word_count_goal": word_count_goal,
                "word_count": 0,
            }
            write_markdown_file(file_path, metadata, "")
        except IOError as e:
            print(f"    -> {FAILURE} could not create draft: {e}")
            sys.exit(1)
    else:
        print(f"    -> {INFO} opening draft: {file_path.name}")



    # open editor
    try:
        subprocess.call([EDITOR, str(file_path)])
    except FileNotFoundError:
        print(f"    -> {FAILURE} editor not found: {EDITOR}")
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
        
        print(f"    -> {INFO} word count: {word_count}")

    except Exception as e:
        print(f"    -> {FAILURE} could not update word count: {e}")
        print(f"    -> {FAILURE} issue updating word_count: {e}")


if __name__ == "__main__":
    main()
