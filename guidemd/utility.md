[<- Back to guide](./guide.md)
# Utilities

## Docking
`guiscript.static_dock` will provide simple but effective static docking as seen in the `docking_demo.py` demo

## Icons Async Downloading
The Icons class will provide useful functions to set and download icons even async

## Shortcuts Elements
`invis_element`, `row`, `column`, `hline`, `vline` are all functions to make some elements more easy

## Custom Scrollbars
If you don't want the default scrollbar positioning and sizing use the `custom_[v/h]scrollbar` function and bind it to the stack

## Rects
Shortcuts for zero, size-only and position-only rects:
- `ZeroRect`/`ZeroR` -> `pygame.Rect(0, 0, 0, 0)`
- `SizeRect`/`SizeR` -> `pygame.Rect(0, 0, w, h)`
- `PosRect`/`PosR` -> `pygame.Rect(x, y, 0, 0)`

## Options-like Selection
`bind_one_selected_only` will bind liteners to make sure only one of the specified elements is selected at once

## Default Style ID
Just like you can with managers, you can set a default style id used in addition by the next elements. You can use a combination of function and context manager class (`set_default_style_id`, `DefaultStyleID`)

## Quick Style
Parse a style source replacing 'ID' with a new random id and return it to assign to an element. If no variables are provided the current manager ones will be used