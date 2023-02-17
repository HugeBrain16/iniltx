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

[main]:config
name = iniltx
```

```py
import iniltx

tokens = iniltx._tokenize(open("main.ltx").read())
config = iniltx.parse(tokens)

print(config)
```