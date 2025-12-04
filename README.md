# CYBERDECK LAYER SYSTEM GUIDE

The cyberdeck system now supports dynamic layers. You can compile from any lower layer to any upper layer in the hierarchy.

## QUICK START

Compile scenes to chapters:
```bash
python compile.py scenes chapters
```

Interactive mode (choose layers dynamically):
```bash
python compile.py
```

## ADDING NEW LAYERS

To add a new layer (e.g., "parts", "books", "series"), edit `helpers.py`:

Simply add a new entry to the `LAYERS` dict in `helpers.py`:

```python
LAYERS = {
    "drafts": LayerConfig("drafts", "~/writing/drafts"),
    "scenes": LayerConfig("scenes", "~/writing/scenes"),
    "chapters": LayerConfig("chapters", "~/writing/chapters"),
    "parts": LayerConfig("parts", "~/writing/parts"),  # new layer
}
```

That's it! No template files needed. The YAML structure is generated programmatically.

## LAYER HIERARCHY

Layers are ordered. You can only compile FROM a lower layer TO a higher layer:

```
drafts → scenes → chapters → (etc.)
```

Each layer can reference its parent using the "afterlife" field in YAML frontmatter:
```yaml
afterlife: "[[parent_item_name]]"
```

## METADATA FIELDS

Each layer file uses a standardized YAML structure. All files have the same fields:
- `aliases`: list (alternative names for the file)
- `afterlife`: string (links to parent layer via `[[parent_name]]`)
- `is_dead`: boolean (marks as consumed/archived)
- `type`: list (singular layer name, e.g., `[draft]`, `[scene]`, `[chapter]`)
- `summary`: string (short description)
- `word_count_goal`: integer (target word count)
- `word_count`: integer (auto-calculated from body)

### Example YAML Structure

```yaml
---
aliases:
  - Alternative Title
afterlife: "[[parent-layer-item]]"
is_dead: false
type:
  - draft
summary: A brief description of this item
word_count_goal: 500
word_count: 235
---
```

The `type` field is automatically set to the layer name when creating new files.

## EXAMPLE: Creating a "parts" layer

1. Edit `helpers.py` and add to the `LAYERS` dict:
```python
"parts": LayerConfig("parts", "~/writing/parts"),
```

2. Use it:
```bash
python compile.py chapters parts
```

That's all! When you create a new part by compiling chapters into it, the YAML will be automatically generated with `type: [part]` and all required fields.

## UNARCHIVE SYSTEM

The `unarchive.py` script works with any layer:
- Groups archived items by their "afterlife" field
- Can restore items back to their source layer
- Automatically marks them as "alive" again

## FILES

- `compile.py` - Main compilation script (dynamic, layer-agnostic)
- `writing_draft.py` - Create new draft files
- `draft.py` - Legacy alternative for creating drafts
- `unarchive.py` - Decompile and restore archived items
- `helpers.py` - Shared utilities, layer definitions, and YAML structure
