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

1. Create the directory constant (or let it use the default `~/writing/LAYER_NAME`)
2. Add to the `LAYERS` dict in `helpers.py`:

```python
LAYERS = {
    "drafts": LayerConfig("drafts", "~/writing/drafts", "~/.local/templates/draft_template.md"),
    "scenes": LayerConfig("scenes", "~/writing/scenes", "~/.local/templates/scene_template.md"),
    "chapters": LayerConfig("chapters", "~/writing/chapters", "~/.local/templates/chapter_template.md"),
    "LAYER_NAME": LayerConfig("LAYER_NAME", "~/writing/LAYER_NAME", "~/.local/templates/LAYER_NAME_template.md")
}
```

3. Create the template file at `~/.local/templates/LAYER_NAME_template.md`

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

Each layer file uses these YAML fields:
- `aliases`: list (alternative names for the file)
- `afterlife`: "[[parent_name]]" (links to parent)
- `is_dead`: true/false (marks as consumed)
- `type`: list (draft, scene, chapter, etc.)
- `summary`: string (short description)
- `word_count_goal`: integer (target word count)
- `word_count`: integer (auto-updated after editing)

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
# In LAYERS dict:
"parts": LayerConfig("parts", "~/writing/parts", "~/.local/templates/part_template.md"),
```

2. Create `~/.local/templates/part_template.md`:
```markdown
---
aliases: 
afterlife: ""
is_dead: false
type:
  - part
summary: {SUMMARY}
word_count_goal: {WORD_COUNT_GOAL}
word_count: {WORD_COUNT}
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
- `draft.py` - Create new draft files
- `unarchive.py` - Decompile and restore archived items
- `helpers.py` - Shared utilities and layer definitions
