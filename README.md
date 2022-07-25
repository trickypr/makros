<div align="center">

# Makros

Extend the Python language with (relative) ese

</div>

> **Warning**
>
> This is an early experiment. Use at your own risk

This program converts custom python files with a custom syntax to regular python files. The overall goals of this project are:

1. To include some of the features that I feel are missing from the python programming language
2. Provide a method for others to use this functionality without needing to contribute to this repo

## Installation

> Note: This will only work after the completion of [#8](https://github.com/trickypr/makros/issues/8)

```bash
pip install makros
```

## Usage

To use this simply create a file with the `.mpy` extension, like the following:

```python
macro import namespace

namespace greet:
    name = "World"

    export def set_name(new_name):
        name = new_name

    export def say_hello():
        print("Hello, " + name)

greet.say_hello()
greet.set_name("trickypr")
greet.say_hello()
```

Then just run it with makros:

```bash
makros my_file.mpy
```

For more info, please read our docs.

**TODO:** Host docs online
