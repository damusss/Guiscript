[<- Back to guide](./guide.md)
# The Base Element
The following features are available to all elements that inherit it (NOT the root), even custom ones made by the user.<br>
Not all methods and properties will be covered, only the concepts. Use your IDE linting to check them all

## Important Notes
Editing most of the properties won't change the element's state and might result in bugs. Always use methods that will correctly modify them<br>
The components can't be extended.

## Basic Properties
- The manager the element is bound to<br>
- The element's parent<br>
- The element's surface where the children and components are drawn to
- The absolute rect, contaning the position relative to the root
- The relative rect, containing the position relative to the parent
- The static rect, that follows the other rect's size but has zero position
- The element's children that renders into it
- The element's style and style group. Read a bit below for more

You can manage children, destroy the element, edit size and position with the appropriate methods

## Context Manager
You can pass the parent to the element's init but you can also make an element the default parent for the next one. To do this you need to use the element's context manager.
```py
# letters are in place for elements
with A:
    # A is default parent 
    with B: # B parent is A
        # B is default parent
        C() # C parent is B
        D() # D parent is B
    # default parent back to A
    with E: # E parent is A
        # E is default parent
        F() # F parent is E
        G() # G parent is E
    # default parent back to A
# A is no longer default parent
```

## DNA Properties
This properties are also used to choose the styling of the element. Read more on [the help strings](./helpstrings.md)
- `object_id` The python memory address of the object
- `element_id` Custom id for the element
- `style_id` Set of style ids separated by semicolons `"example1;example2;example3"`
- `element_types` Tuple of element types like (element, stack, vstack)

The element types tree of builtin elements can be learned in [the help strings](./helpstrings.md)

## Components
The components are objects responsible of rendering different kind of UI interfaces. The are
- `bg`
- `image`
- `shape`
- `text`
- `icon`
- `outline`

Their name is self explainatory and each one of them can have utility methods and methods to update them like to set the text or the surface. They use the style object with their name to choose the render settings.

## Style Object Structure
The element has a style group, an object created using the DNA properties.
That object has three main attributes:
- `style` The default style object when no interaction is present
- `hover_style` The style object used when the element is hovered
- `press_style` The style object used when the element is pressed

Each style object has properties that have the same names as the components, plus an extra `stack` style that defines styling for spacing, padding etc

Each component of the style object has its own style properties. Learn them on [the help strings](./helpstrings.md)

## How to receive events

Since most elements don't need pygame events, to save performance they will not be given them. If your element class needs events, you need to set to True a special class attribute `need_event` at the top of the class (not in the init) and every instance of your element will receive events

## Events, Callbacks, Buffers
Every time something happens on the element (it gets clicked, it gets overed etc) a pygame element AND a callback are fired, so you can choose how to handle them.<br>
All elements have the default element events and callbacks but each element class can add their own.<br>
Buffers are just objects that the user provide that the element will feed a value when it changes and they are stored in the `buffers` object.<br>
All three of this things can be learned reading [the help strings](./helpstrings.md) that will also list additional events, callbacks, buffers for other builtin elements

## Status and sound overriding
`Status` is an object bound to the element that
- Hold information about it being pressed, hovered etc
- Hold information about visibility and activity
- Hold hover/press timings
- Hold settings for enabling/disabling keyboard navigation and the drag flag
- Hold, register and invoke callbacks

The `sounds` object keeps a dictionary with custom sounds that will be played instead of the defaults. If the string `"nosound"` is passed, the specified sound won't be played at all

## Dirty/Destroy/Drag, Visible, Active
All this flags are inside the status object<br>
- The `dirty` flag will tell the element when it needs to re-render and will inform the parent chain aswell. When nothing changes, the element will save performance. Can be set with the `set_dirty` method<br>
- The `can_drag` flag will allow the element to automatically be dragged around by the mouse<br>
- The `can_destroy` flag will stop the element from being destroyed when the `destroy` method is called, unless `force` is passed as `True`<br>
- The `visible` flag will stop the element from being rendered and from being considered by stacks and interaction. An invisible element effectively 'doesn't exist' but can be made visible again<br>
- The `active` flag is only useful for stopping the style from changing when the element is interacted. Events, callbacks etc will still be fire<br>

Visible and active flags can be modified with the element's methods `hide`, `show`, `deactivate`, `activate`

## Animating
For styling animations like changes in color you must use the animation syntax inside the style script. To do that, check [the help strings](./helpstrings.md)<br>
You can also animate
- position
- size
- render offset

To do that check the numerous `animate_*` methods that will create property animations objects and update them<br>
If the method name ends in 'to' it means the increase amount will be calcluated based on the final amount and the starting amount

## Ignore Flags, Offsets & More

There are three ignore flags:
- `ignore_stack` The element won't be positioned when inside a stack object
- `ignore_scroll` The element won't scroll when the stack is scrolled
- `ignore_raycast` The element will be invisible when interacting

All this flags can be set with the `set_ignore` method

The `scroll_offset` will be used by the elements to scroll while the `render_offset` will be an offset that moves where the element is rendered but not the real position

With the `*_attr[s]` methods you can set and get some custom attributes in a dict. Every builtin made inner element will have the 'builtin' attr set to `True`

The `z_index` property will specify an index within the parent that decides the order of rendering, updating and organizing of elements. Higher values will be rendered last

## Ghost
If a ghost element is set using the appropriate method, The current element will be ignored by the stack and its center will follow the ghost center. This is useful for sizing animations to avoid other elements needing to resize when this element animates.

## Anchors
You can use the appropriate methods to set, check and remove anchors. When an anchor is set, one of the element's side will follow the target's target side. The element will so change position and size when needed while trying to respect the anchors

## Resizers
With the appropriate methods small resizer elements on the specified element positions will be created and when they are pressed the element will resize. Useful for things like windows or textboxes. To allow a change in cursor the custom attr `resizer_name` is set

## Subclassing
When subclassing, remember to call the appropriate parent class's `__init__` method. Avoid using the 'private' attributes unless it's absolutely necessary. Methods like `init`, `on_logic`, `on_render`, `on_destroy`, `on_event`, `_refresh_stack` (implemented by stacks), `size_changed`, `style_changed`, `position_changed`, `build` have a default empty implementation and are supposed to be overridden whenever you need.