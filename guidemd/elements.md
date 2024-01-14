[<- Back to guide](./guide.md)
# The Element Classes
Each builtin element will be listed and the key features explained<br>
All builtin elements have default styling and some have custom settings with default values. A settings object exist for every element requiring settings<br>
NOTE: most element's settings will only work in the init and the few that don't won't rebuild the element once changed<br>
Each settings object also have a default instance created and imported

# Miscellanic

### Text
Deactivated, Have shortcuts to set and get the text
### Icon
Deactivated, Have shortcuts to set and get the icon
### Image
Deactivated, Have shortcuts to set and get the surface
### Button
Activated (shortcut for selectable), Have shortcuts to get and set and get the text
### ImageButton
Activated (shortcut for selectable), Have shortcuts to get and setand get the surface
### IconButton
Activated (shortcut for selectable), Have shortcuts to get and set and get the icon
### Checkbox
Activated with shape on-off default styling with shortcuts to get and set the state
### GIF
Display a sequence of frames with playback methods
### Slider
A slider the user can move with methods to set and get the value. Uses settings of type `SliderSettings`
### ProgressBar
A bar showing progress with a shape with methods to get and set the value. Uses settings of type `ProgressBarSettings`
### Slideshow
A list of surfaces with two buttons and methods to move between them. Uses settings of type `SlideshowSettings`

# Stacks

### VStack
Organizes children with `ignore_stack=False` using stack styles vertically. Also creates an horizontal and vertical scrollbar toggled by the stack styles
### HStack
Organizes children with `ignore_stack=False` using stack styles horizontally. Also creates an horizontal and vertical scrollbar toggled by the stack styles
### Box
A VStack that keeps a reference and have methods to manage an element which is the only user element it should contain even though it's not enforced

# Menus

### DropMenu
A dropdown or dropup menu with a menu with options and a button + arrow displaying the current one with methods to manage the options, the selected option and the menu visibility. Uses settings of type `DropMenuSettings`
### SelectionList
A vertical stack of options the user can select (one or more depending on the settings) with methods to manage them. Uses settings of type `SelectionListSettings`

# Input

### Entry
Let the user input text on a single line with common operations + paste, with methods to manage the selection, the content and the focus status. Uses settings of type `EntrySettings`
### Textbox
An extended entry that let the input be on multiple lines. Uses settings of type `TextboxSettings`

# Windows

### Window
A closable (optional), collapsable (optional), draggable (optional) window-like element. A window stack makes sure when a window title is clicked it will go to the front. To add elements to the window use the `content` property or use the `enter()` method on the context manager. Uses settings of type `WindowSettings`
### ModalContainer
When opened covers all the screen (default styling have a black fade over the below elements) and displays a single element like a modal would. Uses settings of type `ModalSettings`

# Players

### SoundPlayer
Enable the user to edit the playback and volume of a sound track with methods to do the same via code. Uses settings of type `SoundPlayerSettings`

### VideoPlayer
The same as the sound player but also show video frames. Uses settings of type `VideoPlayerSettings`