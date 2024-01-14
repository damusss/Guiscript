# GUIDE

## Important Notes
Inside the guiscript module are all the variables, functions and classes available.<br>
Each function and class have linting and docstrings to understand their usage. Always read them before using them. This guide will only give general orientation and list features and elements<br>
There are several help_* functions. Use them to read their specific features. The same strings can be found using the link below.<br>
Variables ending with "Type" are meant to be used with linting and not instanciating. Doing that will result in bugs.<br>
All variables, functions and classes starting with an underscore should never be modified or called by the user, doing that will probably break the library. Nothing is hidden so there is surely a different, 'official' method of doing the same thing.<br>
It is suggested to only inherit the Element class when creating custom elements, the other objects don't need to be subclassed<br>
I suggest to shorten the import name to `guis` and not to `import *` from it as it will flood your module namespace.<br>
When i'll say 'properties' i'll actually mean attributes, meaning they are free of access and modification. In the whole library there are no properties so use the attributes when reading and call the appropriate function if direct modification is not suggested.<br>
Every method that doesn't return some information will return the object itself, this way you can concatenate function calls `object.meth1().meth2().meth3()`<br>
An extensive use of enums is done in the library, they are preferred over strings as you are sure they will work but the result is the same.

# [Help Strings](./helpstrings.md)

# [Getting Started](./setup.md)

# [The Manager](./manager.md)

# [The Base Element](./element.md)

# [The Element Classes](./elements.md)

# [Utilities](./utility.md)