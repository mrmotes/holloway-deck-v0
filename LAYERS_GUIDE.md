# CYBERDECK LAYER SYSTEM GUIDE

The cyberdeck system now supports dynamic layers. You can compile from any lower layer to any upper layer in the hierarchy.

## QUICK START

Compile drafts to scenes (original behavior):
```bash
python scene_compile.py
# OR
python compile.py drafts scenes
```

Compile scenes to chapters (new):
```bash
python compile.py scenes chapters
```

Interactive mode (choose layers dynamically):
```bash
python compile.py
```

## ADDING NEW LAYERS

To add a new layer (e.g., "parts", "books", "series"), edit `helpers.py`:

1. Create the directory constant (or let it use the default `~/writing/LAYER_NAME`)
2. Add to the `LAYERS` dict in `helpers.py`:

```python
LAYERS = {
    "drafts": LayerConfig("drafts", DRAFTS_DIR, DRAFT_TEMPLATE_PATH),
    "scenes": LayerConfig("scenes", SCENES_DIR, TEMPLATE_PATH),
    "chapters": LayerConfig("chapters", CHAPTERS_DIR, Path(os.path.expanduser("~/.local/templates/chapter_template.md"))),
    "parts": LayerConfig("parts", Path(os.path.expanduser("~/writing/parts")), Path(os.path.expanduser("~/.local/templates/part_template.md"))),
}
```

3. Create the template file at `~/.local/templates/part_template.md`

## LAYER HIERARCHY

Layers are ordered. You can only compile FROM a lower layer TO a higher layer:

```
drafts → scenes → chapters → parts → books → series
```

Each layer can reference its parent using the "afterlife" field in YAML frontmatter:
```yaml
afterlife: "[[parent_item_name]]"
```

## METADATA FIELDS

Each layer file uses these YAML fields:
- `is_dead`: true/false (marks as consumed)
- `afterlife`: "[[parent_name]]" (links to parent)
- `word_count`: integer (auto-updated after editing)
- `word_count_goal`: integer (target word count)
- `summary`: string (short description)

## TEMPLATE VARIABLES

Templates support these replacement variables (customize per template):
- `{LAYER_TITLE}` - the title (e.g., `{CHAPTER_TITLE}`)
- `{SUMMARY}` - aggregated summary from child items
- `{WORD_COUNT}` - aggregated word count
- `{WORD_COUNT_GOAL}` - aggregated word count goal
- `{LAYER_BODY}` - aggregated body content (e.g., `{CHAPTER_BODY}`)

The system provides fallback names:
- `{TITLE}` - same as `{LAYER_TITLE}`
- `{BODY}` - same as `{LAYER_BODY}`

## EXAMPLE: Creating a "parts" layer

1. Edit `helpers.py` and add:
```python
PARTS_DIR = Path(os.path.expanduser("~/writing/parts"))

# In LAYERS dict:
"parts": LayerConfig("parts", PARTS_DIR, Path(os.path.expanduser("~/.local/templates/part_template.md"))),
```

2. Create `~/.local/templates/part_template.md`:
```markdown
---
title: {PART_TITLE}
summary: {SUMMARY}
word_count: {WORD_COUNT}
word_count_goal: {WORD_COUNT_GOAL}
is_dead: false
afterlife: ""
---

# {PART_TITLE}

{PART_BODY}
```

3. Use it:
```bash
python compile.py chapters parts
```

## UNARCHIVE SYSTEM

The `unarchive.py` script works with any layer:
- Groups archived items by their "afterlife" field
- Can restore items back to their source layer
- Automatically marks them as "alive" again

## FILES

- `compile.py` - Main compilation script (dynamic, layer-agnostic)
- `scene_compile.py` - Legacy wrapper for drafts→scenes (backward compatible)
- `writing_draft.py` - Create new draft files
- `unarchive.py` - Restore archived items
- `helpers.py` - Shared utilities and layer definitions
