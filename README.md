# Holloway Deck
Holloway is a writerdeck inspired by a science-fiction novel I am writing. It is not _just_ a distraction-free writing machine; it's a means of bringing the world of my novel to me. One of the core themes of the book is the decentralization of data as an act of revolution against a technocratic monarchy. What does an uprising look like when castles become data centers? Thus this project. It does only a few things specific to my needs, but perhaps this is something someone else might be interested in.

> [!warning] Caveats
> 1. This is made for me and my particular set up on my Raspberry Pi 4 running DietPi. As such, it is highly opinionated to this set up.
> 2. I am a creative first and an engineer second (or third or fourth... you get the idea), so forgive me.
> 3. Per the previous caveats, much of this will likely not work for _you_ right out of the box without significant configuration.

## Philosophy
Here are the core prinicples of this project:
- A no-desktop machine dedicated to creative writing and nothing else
- Automated processes for creating hierarchical writing _chunks_
- A focus on current, in-progress work (i.e., the ability to "ship" completed files to my home PC via SCP)
- Writing should feel good and be fun

## Files
This project contains the following files:
- `compile.py` - Main compilation script (dynamic, layer-agnostic)
- `draft.py` - Create new draft files
- `unarchive.py` - Decompile and restore archived items
- `helpers.py` - Shared utilities, layer definitions, and YAML structure

## Layers 
### Hierarchy
Layers are simply a hierarchical structure for my longform writing. They are ordered. You can only compile **FROM** a lower layer **TO** a higher layer:

```
drafts → scenes → chapters → (etc.)
```

Each layer can reference its parent using the "afterlife" field in YAML frontmatter:
```yaml
afterlife: "[[parent_item_name]]"
```
^ can you tell I use Obsidian? ;)
### Structure
Each layer file uses a standardized YAML structure. All files have the same fields:
- `aliases`: list (alternative names for the file)
- `afterlife`: string (links to parent layer via `[[parent_name]]`)
- `is_dead`: boolean (marks as consumed/archived)
- `type`: list (singular layer name, e.g., `[draft]`, `[scene]`, `[chapter]`)
- `summary`: string (short description)
- `word_count_goal`: integer (target word count)
- `word_count`: integer (auto-calculated from body)

Here's an example of this YAML structure:
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
### Adding New Layers
This system assumes the following layer structure for longform writing: drafts -> scenes -> chapters. However, this design is extensible. To add a new layer (e.g., "parts", "books", "series"), simply add a new entry to the `LAYERS` dict in `helpers.py`.

```python
LAYERS = {
    "drafts": LayerConfig("drafts", "~/writing/drafts"),
    "scenes": LayerConfig("scenes", "~/writing/scenes"),
    "chapters": LayerConfig("chapters", "~/writing/chapters")
}
```
Here's an example of adding a "parts" layer:

1. Edit `helpers.py` and add the new layer to the `LAYERS` dict:
```python
LAYERS = {
    "drafts": LayerConfig("drafts", "~/writing/drafts"),
    "scenes": LayerConfig("scenes", "~/writing/scenes"),
    "chapters": LayerConfig("chapters", "~/writing/chapters"),
    "parts": LayerConfig("parts", "~/writing/parts") # new parts layer
}
```
2. Use it:
```bash
python compile.py chapters parts
```
That's it! When you create a new part by compiling chapters into it, the YAML will be automatically generated with `type: [part]` and all required fields.

## Draft
```python
#TODO - Write out what the `draft.py` file does
```
## Compile
```python
#TODO - Write out what the `compile.py` file does
```
## Unarchive
The `unarchive.py` script works with any layer:
- Groups archived items by their "afterlife" field
- Can restore items back to their source layer
- Automatically marks them as "alive" again

This is mainly used to allow me to quickly undo a compile as I test and build out these functions. Once this gets to a stable place, this is not something I plan to incorporate into my regular writing workflow.

# Open Questions/Problems
- What happens if you add a new layer in between existing layers? / Probably breaks? / NEEDS TESTING
- 