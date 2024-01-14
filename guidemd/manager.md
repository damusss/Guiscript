[<- Back to guide](./guide.md)
# The Manager
The manager contains all elements that belong to it and other objects and is the one responsible for updating and rendering them.<br>
Multiple ones are possible, but you should only have one manager getting updated/rendered at once.<br>

## What is a 'current manager'
When you pass `is_current=True` to the Manager's init or when you call set_current, the manager becomes the current.
This mean that when you create any element, and pass None (default) as the manager parameter, the manager set to current will be used.

Whenever you need to change scene and use a different manager, call manager.`set_current()` before creating the next elements and remember to destroy the previous one to release the memory hold by the previous elements. For simple applications with a single scene, you won't ever need to do this.

Other then updating and rendering you can also restart/destroy it, filter elements by their properties, change the screen surface (for example when the window is resized) and parse style scripts/sources. Read all about the style script in [the help strings](./helpstrings.md)

## Root
Each manager has a `root`. It's the most top parent of the element tree. NOTE: the root is NOT an element. It is a very simplified version of an element that relies on no other parent. All functions and property are the ones strictly needed by the children. Most features of elements are not available, and some of the methods are empty, just there for compatibility.

## Cursors
An object bound to the manager that keeps the cursors the user want to have when interacting with the elements. This feature can be easily disabled within the object.

## Navigation
An object bound to the manager that allows and manager keyboard navigation. It's also customizable and you can learn how to keyboard navigate in [the help strings](./helpstrings.md)

## Interact
The most important object bound to the manager. Allows things like hovering, pressing, text selecting, copy/pasting, sound playing, event firing and updating the cursor.

With it you can also raycast at a position, change the default sounds (each element can override them) and get information on what elements are interacted (hovered, pressed, right pressed...)