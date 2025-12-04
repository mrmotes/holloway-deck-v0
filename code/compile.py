#!/usr/bin/env python3
"""
Dynamic layer compilation tool for cyberdeck.
Compile from any lower layer to any upper layer.

Usage:
    compile.py                           # Interactive mode
    compile.py [source_layer] [target_layer]  # Direct mode
"""

import os
import shutil
import subprocess
import sys

from helpers import (
    RED, GREEN, BLUE, RESET,
    ARCHIVE_DIR, REMOTE_USER, REMOTE_IP, REMOTE_PATH,
    LAYERS,
    select_items_fzf,
    parse_markdown_yaml,
    write_markdown_file,
    sanitize_filename,
)


def get_available_layers() -> list:
    """Return list of layer names in order."""
    return list(LAYERS.keys())


def validate_layer_transition(source_name: str, target_name: str) -> bool:
    """Validate that source comes before target in the hierarchy."""
    layers = get_available_layers()
    try:
        source_idx = layers.index(source_name)
        target_idx = layers.index(target_name)
        return source_idx < target_idx
    except ValueError:
        return False


def transfer_file_to_holloway(filepath):
    """Transfer a file to remote via SCP."""
    if not (REMOTE_USER and REMOTE_IP and REMOTE_PATH):
        return False
    
    remote_destination = f"{REMOTE_USER}@{REMOTE_IP}:{REMOTE_PATH}/{filepath.name}"
    result = subprocess.call(["scp", "-q", "-B", str(filepath), remote_destination])
    
    if result == 0:
        print(f"    -> {GREEN}SUCCESS:{RESET} file transferred to holloway: {filepath.name}")
    else:
        print(f"    -> {RED}FAILURE:{RESET} scp exit-code: {result}")
        sys.exit(1)


def archive_and_transfer(filepath):
    """Archive file locally and transfer to remote."""
    archive_path = ARCHIVE_DIR / filepath.name

    try:
        shutil.copy2(filepath, archive_path)
        print(f"    -> {GREEN}SUCCESS:{RESET} file archived locally: {archive_path.name}")
        transfer_file_to_holloway(archive_path)
        os.remove(filepath)
        print(f"    -> {GREEN}SUCCESS:{RESET} file deleted locally: {filepath.name}")
    except Exception as e:
        print(f"    -> {RED}ERROR:{RESET} error archiving {filepath.name}: {e}")
        sys.exit(1)


def update_source_metadata(filepath, target_name: str, target_filename: str):
    """Mark source file as consumed and link to target."""
    metadata, body = parse_markdown_yaml(filepath)
    metadata["is_dead"] = True
    link_name = target_filename.replace(".md", "")
    metadata["afterlife"] = f'"[[{link_name}]]"'
    write_markdown_file(filepath, metadata, body)
    print(f"    -> {GREEN}SUCCESS:{RESET} metadata updated: {filepath.name}")


def create_new_target(target_layer, title: str, summaries: list, bodies: list, 
                      total_word_count: int, total_word_count_goal: int) -> tuple:
    """Create a new file in target layer."""
    safe_filename = sanitize_filename(title)
    target_path = target_layer.directory / safe_filename
    
    summary = " ".join(summaries)
    body = "\n\n".join(bodies)
    
    target_layer.create_file_from_body(target_path, body, title=title, summary=summary)
    
    # Update word counts after file creation
    metadata, file_body = parse_markdown_yaml(target_path)
    metadata["word_count_goal"] = total_word_count_goal
    metadata["word_count"] = total_word_count
    write_markdown_file(target_path, metadata, file_body)
    
    return target_path, safe_filename


def append_to_target(target_layer, target_filename: str, summaries: list, bodies: list,
                     total_word_count: int, total_word_count_goal: int) -> tuple:
    """append to existing file in target layer."""
    target_path = target_layer.directory / target_filename
    
    if not target_path.exists():
        print(f"    -> {RED}FAILURE:{RESET} target file {target_filename} not found")
        sys.exit(1)
    
    print(f"    -> {BLUE}INFO:{RESET} parsing existing {target_layer.name}: {target_filename}...")
    metadata, body = parse_markdown_yaml(target_path)
    
    new_word_count = metadata.get("word_count", 0) + total_word_count
    new_word_count_goal = metadata.get("word_count_goal", 0) + total_word_count_goal
    new_summary = f'{metadata.get("summary", "")} {" ".join(summaries)}'
    new_body = f"{body}\n\n{"\n\n".join(bodies)}"
    
    metadata["word_count"] = new_word_count
    metadata["word_count_goal"] = new_word_count_goal
    metadata["summary"] = new_summary.strip()
    
    write_markdown_file(target_path, metadata, new_body)
    return target_path, target_filename


def compile_layers(source_layer, target_layer):
    """Compile from source layer to target layer."""
    # Validate transition
    if not validate_layer_transition(source_layer.name, target_layer.name):
        print(f"    -> {RED}FAILURE:{RESET} invalid layer transition: {source_layer.name} -> {target_layer.name}")
        print(f"    -> {BLUE}INFO:{RESET} available layers in order: {', '.join(get_available_layers())}")
        sys.exit(1)
    
    # Ensure directories exist
    source_layer.ensure_exists()
    target_layer.ensure_exists()
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Select source files
    source_files = source_layer.get_files()
    selected_source_files = select_items_fzf(source_files, multi=True, 
                                             prompt=f"select {source_layer.name} to compile -> ")
    
    if not selected_source_files:
        sys.exit(0)
    
    selected_source_files.sort()
    print(f"\n{len(selected_source_files)} files selected")
    
    # Select target
    target_files = target_layer.get_files()
    target_selection_list = [f"[CREATE NEW {target_layer.name.upper()}]"] + target_files
    
    selected_target_files = select_items_fzf(target_selection_list, multi=False, 
                                             prompt=f"select {target_layer.name} to append to -> ")
    
    if not selected_target_files:
        print(f"    -> {BLUE}INFO:{RESET} ABORTING: no target selected")
        sys.exit(0)
    
    selected_target_file = selected_target_files[0]
    
    # Aggregate data from source files
    total_word_count_goal = 0
    total_word_count = 0
    summaries = []
    bodies = []
    
    for filename in selected_source_files:
        path = source_layer.directory / filename
        metadata, body = parse_markdown_yaml(path)
        
        try:
            total_word_count_goal += int(metadata.get("word_count_goal", 0))
        except (ValueError, TypeError):
            pass
        try:
            total_word_count += int(metadata.get("word_count", 0))
        except (ValueError, TypeError):
            pass
        summary = metadata.get("summary", "")
        if summary:
            summaries.append(summary)
        bodies.append(body)
    
    # Create or append to target
    if selected_target_file.startswith("[CREATE NEW"):
        try:
            target_title = input(f"enter NEW {target_layer.name} title: ").strip()
        except KeyboardInterrupt:
            sys.exit(0)
        
        if not target_title:
            print(f"    -> {RED}FAILURE:{RESET} {target_layer.name} title is required for NEW {target_layer.name}")
            sys.exit(1)
        
        final_path, final_filename = create_new_target(target_layer, target_title, summaries, 
                                                       bodies, total_word_count, total_word_count_goal)
        print(f"    -> {GREEN}SUCCESS:{RESET} created NEW {target_layer.name}: {final_filename}")
    else:
        final_path, final_filename = append_to_target(target_layer, selected_target_file, summaries,
                                                      bodies, total_word_count, total_word_count_goal)
        print(f"    -> {GREEN}SUCCESS:{RESET} appended to {target_layer.name}: {final_filename}")
    
    print("-" * 30)
    
    # Process source files
    for filename in selected_source_files:
        source_path = source_layer.directory / filename
        update_source_metadata(source_path, target_layer.name, final_filename)
        archive_and_transfer(source_path)
    
    # Open result
    print("-" * 30)
    try:
        open_target = input(f"open {final_filename}? [y/N]: ")
    except KeyboardInterrupt:
        sys.exit(0)
    
    if open_target == "y" or open_target == "Y":
        print(f"opening {final_filename} in nvim...")
        subprocess.call(["nvim", str(final_path)])
    else:
        print(f"{BLUE}INFO:{RESET} {target_layer.name} compile complete!")


def main():
    if len(sys.argv) == 3:
        # Direct mode: compile.py source target
        source_name = sys.argv[1]
        target_name = sys.argv[2]
        
        if source_name not in LAYERS or target_name not in LAYERS:
            print(f"    -> {RED}FAILURE:{RESET} unknown layer")
            print(f"    -> {BLUE}INFO:{RESET} available layers: {', '.join(get_available_layers())}")
            sys.exit(1)
        
        source_layer = LAYERS[source_name]
        target_layer = LAYERS[target_name]
    elif len(sys.argv) == 1:
        # Interactive mode
        layers = get_available_layers()
        print(f"Available layers: {', '.join(layers)}")
        
        try:
            source_name = input("source layer: ").strip().lower()
            target_name = input("target layer: ").strip().lower()
        except KeyboardInterrupt:
            sys.exit(0)
        
        if source_name not in LAYERS or target_name not in LAYERS:
            print(f"    -> {RED}FAILURE:{RESET} unknown layer")
            sys.exit(1)
        
        source_layer = LAYERS[source_name]
        target_layer = LAYERS[target_name]
    else:
        print(__doc__)
        sys.exit(0)
    
    compile_layers(source_layer, target_layer)


if __name__ == "__main__":
    main()
