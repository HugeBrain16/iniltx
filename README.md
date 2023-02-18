# INILTX

An INI/LTX config parser

## Example

```ltx
# config.ini

[config]
token = asdf123
```

```ltx
# main.ltx
#include config.ini

version = 1.0.0

# define a section that inherits 'config' section
[main]:config
name = iniltx-v%version%
```

```py
import iniltx

tokens = iniltx._tokenize(open("main.ltx").read())
config = iniltx.parse(tokens)

print(config)
```
