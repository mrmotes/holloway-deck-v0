#!/usr/bin/env python3

import os
import re
import shutil
import subprocess
import sys

from helpers import (
    FAILURE, INFO, SUCCESS,
    ARCHIVE_DIR, LAYERS,
    parse_metadata_header,
    parse_markdown_yaml,
    write_markdown_file,
)


# --- FUNCTIONS ---
def get_grouped_archives():
    # scans archives and groups drafts by their 'afterlife' tag
    # returns: dict { 'scene_name': [list_of_draft_paths], 'ORPHANS': [...] }
    if not ARCHIVE_DIR.exists():
        print(f"    -> {FAILURE} archive dir does not exist at {ARCHIVE_DIR}")
        sys.exit(1)

    grouped_data = {}

    for filepath in sorted(ARCHIVE_DIR.glob("*.md")):
        metadata, _ = parse_metadata_header(filepath)
        afterlife = metadata.get('afterlife', '')
        
        # extract scene name from "[[scene_name]]"
        match = re.search(r'\[\[(.*?)\]\]', str(afterlife))
        
        if match:
            scene_key = match.group(1)
        else:
            scene_key = "ORPHANS (No Scene Link)"

        if scene_key not in grouped_data:
            grouped_data[scene_key] = []
        
        grouped_data[scene_key].append(filepath)

    return grouped_data


def select_scenes_fzf(grouped_data):
    if not grouped_data:
        print(f"    -> {FAILURE} no archived items found")
        sys.exit(0)

    # format list for FZF: "scene_name (X drafts)"
    display_list = []
    for scene, drafts in grouped_data.items():
        display_list.append(f"{scene} ({len(drafts)} drafts)")

    args = ["fzf", "-m", "--prompt=select scenes to decompile > ", "--height=40%", "--reverse"]

    fzf = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )

    input_str = "\n".join(display_list)
    stdout, _ = fzf.communicate(input=input_str)
    
    if fzf.returncode != 0 or not stdout.strip():
        print(f"    -> {FAILURE} no selection made")
        sys.exit(0)
    
    # parse selection back to keys
    # "scene_name (3 drafts)" -> "scene_name"
    selected_keys = []
    for line in stdout.split('\n'):
        if line:
            # split by last space to separate name from count
            key = line.rsplit(' (', 1)[0]
            selected_keys.append(key)
            
    return selected_keys


def revive_metadata(filepath):
    # updates metadata to make the file "alive" again
    metadata, body = parse_markdown_yaml(filepath)

    if not metadata:
        metadata = {}

    # reset attributes to "alive" state
    metadata["is_dead"] = False
    metadata["afterlife"] = "" 

    write_markdown_file(filepath, metadata, body)

    print(f"    -> {SUCCESS} file revived: {filepath.name}")


def unarchive_drafts(draft_paths):
    drafts_layer = LAYERS["drafts"]
    for source_path in draft_paths:
        destination_path = drafts_layer.directory / source_path.name

        if destination_path.exists():
            print(f"    -> {INFO} file already exists in drafts: {source_path.name}")
            continue

        try:
            shutil.move(source_path, destination_path)
            revive_metadata(destination_path)
        except Exception as e:
            print(f"    -> {FAILURE} error moving {source_path.name}: {e}")


def prompt_delete_scene(scene_name):
    # Don't try to delete the "ORPHANS" category placeholder
    if "ORPHANS" in scene_name:
        return

    scenes_layer = LAYERS["scenes"]
    scene_path = scenes_layer.directory / f"{scene_name}.md"
    
    if not scene_path.exists():
        print(f"    -> {INFO} scene file '{scene_name}.md' not found (already deleted?)")
        return

    response = input(f"    -> delete compiled scene '{scene_name}.md'? [y/N]: ").lower()
    
    if response == 'y':
        try:
            os.remove(scene_path)
            print(f"    -> {INFO} deleted file: {scene_path.name}")
        except Exception as e:
            print(f"    -> {FAILURE} could not delete scene: {e}")
    else:
        print(f"    -> {INFO} file not deleted: {scene_path.name}")


def main():
    drafts_layer = LAYERS["drafts"]
    drafts_layer.ensure_exists()
    
    # 1. group archives
    grouped_data = get_grouped_archives()
    
    # 2. select scenes
    selected_scenes = select_scenes_fzf(grouped_data)

    print(f"\ndecompiling {len(selected_scenes)} scenes...")
    print("-" * 30)

    # 3. process
    for scene_key in selected_scenes:
        print(f"\nprocessing group: {scene_key}")
        
        # move drafts back
        drafts = grouped_data.get(scene_key, [])
        unarchive_drafts(drafts)
        
        # offer to delete scene
        prompt_delete_scene(scene_key)


if __name__ == "__main__":
    main()