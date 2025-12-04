#!/usr/bin/env python3

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from ruamel.yaml import YAML

# --- COLORS ---
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BLUE = "\033[94m"

# --- CONFIGURATION (LOGS) ---
FAILURE = f"{RED}FAILURE:{RESET}"
INFO = f"{BLUE}INFO:{RESET}"
SUCCESS = f"{GREEN}SUCCESS:{RESET}"
WARNING = f"{YELLOW}WARNING:{RESET}"

# --- CONFIGURATION (PATHS & ENV) ---
# repo root (parent of code/ directory where helpers.py lives)
REPO_ROOT = Path(__file__).resolve().parent.parent

# XDG / config locations
XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
CONFIG_DIR = Path(os.environ.get("HOLLOWAY_CONFIG_DIR", os.path.join(XDG_CONFIG_HOME, "holloway-deck")))
SECRETS_PATH = CONFIG_DIR / "secrets.json"

# XDG / data locations (for writing files, archives, etc.)
XDG_DATA_HOME = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
DATA_DIR = Path(os.environ.get("HOLLOWAY_DATA_HOME", os.path.join(XDG_DATA_HOME, "holloway-deck")))

# Base install/location for writing data. Prefer environment override, otherwise use XDG data dir.
HOLLOWAY_HOME = Path(os.environ.get("HOLLOWAY_HOME", str(DATA_DIR)))

# Archive location (under the holloway home by default)
ARCHIVE_DIR = Path(HOLLOWAY_HOME) / "writing" / "archives"

# --- CONFIGURATION (YAML) ---
yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.default_flow_style = False

# --- CONFIGURATION (REMOTE) ---
REMOTE_USER = ""
REMOTE_IP = ""
REMOTE_PATH = ""

if SECRETS_PATH.exists():
    try:
        with open(SECRETS_PATH, "r") as file:
            secrets = json.load(file)
            REMOTE_USER = secrets.get("REMOTE_USER", "")
            REMOTE_IP = secrets.get("REMOTE_IP", "")
            REMOTE_PATH = secrets.get("REMOTE_PATH", "")
    except Exception as e:
        print(f"    -> {FAILURE} could not load secrets file: {e}")
        sys.exit(1)
else:
    print(f"    -> {FAILURE} no secrets file found at {SECRETS_PATH}")
    sys.exit(1)


# --- LAYER SYSTEM ---
class LayerConfig:
    """configuration for a writing layer (drafts, scenes, chapters, etc.)"""
    
    def __init__(self, name: str, directory: str):
        self.name = name
        self.directory = self._expand_path(directory)
        # metadata field that links to the parent layer
        self.parent_field = "afterlife"
    
    @staticmethod
    def _expand_path(path_str: str) -> Path:
        """Convert a path string to a Path object, expanding ~ notation."""
        return Path(os.path.expanduser(path_str))
    
    def ensure_exists(self):
        """create directory if it doesn't exist"""
        self.directory.mkdir(parents=True, exist_ok=True)
    
    def get_files(self, exclude_dead: bool = True) -> list:
        """get list of files in this layer"""
        if not self.directory.exists():
            print(f"    -> {FAILURE} {self.name} dir does not exist at {self.directory}")
            sys.exit(1)
        
        files = sorted(self.directory.glob("*.md"))
        if exclude_dead:
            files = [f for f in files if is_not_dead(f)]
        return [f.name for f in files]
    
    def create_file_from_body(self, filepath: Path, body: str, title: str = "", summary: str = "") -> None:
        """Create a markdown file with standard YAML structure for this layer."""
        metadata = {
            "aliases": [title] if title else [],
            "afterlife": None,
            "is_dead": False,
            "type": [self.name],
            "summary": summary if summary else None,
            "word_count_goal": 0,
            "word_count": len(body.split()) if body else 0,
        }
        write_markdown_file(filepath, metadata, body)
    
    def select_file(self, multi: bool = False, prompt: str = None) -> list:
        """fzf-based selection of live files in this layer."""
        from helpers import select_items_fzf  # absolute import for script usage
        files = self.get_files(exclude_dead=True)
        if not files:
            print(f"    -> {WARNING} no live {self.name} files found")
            return []
        prompt_str = prompt or f"select {self.name} to edit > "
        return select_items_fzf(files, multi=multi, prompt=prompt_str)


# Define available layers (order matters: lower index = lower in hierarchy)
_writing_base = Path(HOLLOWAY_HOME) / "writing"

LAYERS = {
    "drafts": LayerConfig("drafts", str(_writing_base / "drafts")),
    "scenes": LayerConfig("scenes", str(_writing_base / "scenes")),
    "chapters": LayerConfig("chapters", str(_writing_base / "chapters")),
}


# --- UTILITY FUNCTIONS ---

def sanitize_filename(text: str) -> str:
    """Convert text to a safe markdown filename."""
    safe = re.sub(r'[^a-z0-9]', '-', text.lower()).strip('-')
    safe = re.sub(r'-+', '-', safe)
    return safe + ".md"


def is_not_dead(file: Path) -> bool:
    """Check if a markdown file is not marked as dead."""
    try:
        with open(file, "r") as f:
            head = f.read(1000)
        return "is_dead: true" not in head
    except (OSError, IOError, UnicodeDecodeError):
        return False


def select_items_fzf(items: list, multi: bool = False, prompt: str = "select > ") -> list:
    """Interactive selection using fzf."""
    if not items:
        print(f"    -> {WARNING} no items available...")
        sys.exit(0)

    args = ["fzf", "--prompt", prompt, "--height=40%", "--reverse"]

    if multi:
        args.append("-m")

    fzf = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )

    input_str = "\n".join(items)
    stdout, _ = fzf.communicate(input=input_str)
    
    if fzf.returncode != 0 or not stdout.strip():
        print(f"    -> {INFO} ABORTING: no files selected...")
        sys.exit(0)
        
    return [x for x in stdout.split('\n') if x]


def parse_metadata_header(filepath: Path) -> tuple:
    """Extract YAML metadata and body from markdown file."""
    try:
        with open(filepath, "r") as file:
            content = file.read()
        
        parts = re.split(r'^---$', content, flags=re.MULTILINE)
        if len(parts) >= 3:
            metadata = yaml.load(parts[1])
            body = parts[2].strip()
            return metadata, body
    except Exception:
        pass
    return {}, ""


def parse_markdown_yaml(filepath: Path) -> tuple:
    """Parse markdown file and return (metadata, body)."""
    with open(filepath, "r") as file:
        file_content = file.read()
    
    file_parts = re.split(r'^---$', file_content, flags=re.MULTILINE)
    
    if not len(file_parts) == 3:
        print(f"    -> {FAILURE} too many or too few instances of '---' in file content: {filepath.name}")
        sys.exit(1)
    
    frontmatter = file_parts[1]
    body = file_parts[2]
    metadata = yaml.load(frontmatter)

    if not metadata:
        print(f"    -> {FAILURE} issue loading yaml: {frontmatter}")
        sys.exit(1)

    return metadata, body.strip()


def write_markdown_file(filepath: Path, metadata: dict, body: str) -> None:
    """Write metadata and body to markdown file."""
    with open(filepath, "w") as file:
        file.write("---\n")
        yaml.dump(metadata, file)
        file.write("---\n\n")
        file.write(body)
