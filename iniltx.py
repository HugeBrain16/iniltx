import io
import os
import re

import iniparser

_RE_DIRECTIVE = re.compile(r"^\#(?P<name>[a-zA-Z_]+)\s+(?P<value>.+)$")
_RE_INHERIT = re.compile(
    r"^\[(?P<section>[a-zA-Z0-9_\-]+)\]\:(?P<instance>[a-zA-Z0-9_\-,]+)$"
)
_RE_INTERP = re.compile(r"\%([a-zA-Z0-9_\-:]+)\%")


def _parse_directive(string: str):
    dirv = _RE_DIRECTIVE.match(string)

    if dirv:
        return dirv.groups()


def _parse_inherit(string: str):
    inh = _RE_INHERIT.match(string)

    if inh:
        return inh.groups()


def _tokenize(string: str | io.StringIO):
    result = []

    if isinstance(string, str):
        string = io.StringIO(string).readlines()
    elif isinstance(string, io.StringIO):
        string = string.readlines()

    for lineno, line in enumerate(string):
        lineno += 1
        line = line.strip()

        if not line:
            continue

        if not _parse_directive(line) and not _parse_inherit(line):
            result.append(["ini", line, lineno])
        else:
            result.append(["ltx", line, lineno])

    return result


def _get_itpsec(string: str):
    result = [None, None]
    tokens = string.split(":", 1)

    if len(tokens) == 2:
        result[0] = tokens[0]
        result[1] = tokens[1]
    else:
        result[0] = tokens[0]

    return result


def _parse_interps(config: dict):
    def assign_value(option: str, section: str = None):
        for itp in _RE_INTERP.findall(
            config[section][option] if section else config[option]
        ):
            tokens = _get_itpsec(itp)

            if tokens[1]:
                if not isinstance(config.get(tokens[0]), dict):
                    raise ValueError("Section doesn't exist: " + tokens[0])

                if tokens[1] not in config[tokens[0]]:
                    raise ValueError(
                        f"Option '{tokens[1]}' doesn't exist in section '{tokens[0]}'"
                    )
                elif config[tokens[0]].get(tokens[1]) is None:
                    raise ValueError("referencing a value only option: " + itp)

                if section:
                    config[section][option] = config[section][option].replace(
                        f"%{itp}%", config[tokens[0]][tokens[1]]
                    )
                else:
                    config[option] = config[option].replace(
                        f"%{itp}%", config[tokens[0]][tokens[1]]
                    )
            else:
                if tokens[0] not in config:
                    raise ValueError(f"Option doesn't exist: " + tokens[0])
                elif isinstance(config[tokens[0]], dict):
                    raise ValueError(f"referencing a section: " + itp)
                elif config.get(tokens[0]) is None:
                    raise ValueError("referencing a value only option: " + itp)

                if section:
                    config[section][option] = config[section][option].replace(
                        f"%{itp}%", config[tokens[0]]
                    )
                else:
                    config[option] = config[option].replace(
                        f"%{itp}%", config[tokens[0]]
                    )

    for opt in config:
        if isinstance(config[opt], dict):
            for sopt in config[opt]:
                if config[opt][sopt] is not None:
                    assign_value(sopt, opt)
        else:
            if config[opt] is not None:
                assign_value(opt)


def parse(tokens: list[list[str]]):
    result = {}
    segment = ""
    last_type = None
    inherit = None
    inherit_segment = ""

    for token in tokens:
        if token[0] == "ltx":
            if last_type == "ini":
                result.update(iniparser.read(segment))
                segment = ""

            dirv = _parse_directive(token[1])

            if dirv:
                if dirv[0] == "include":
                    if os.path.isfile(dirv[1]):
                        tokens = _tokenize(open(dirv[1]).read())
                        result.update(parse(tokens))
                    else:
                        raise iniparser.ParsingError(
                            "File not found: " + dirv[1], token[2], token[1]
                        )

            inh = _parse_inherit(token[1])

            if inh:
                if inherit:
                    result[inherit].update(iniparser.read(inherit_segment))
                    inherit_segment = ""

                instances = inh[1].split(",")
                result[inh[0]] = {}
                inherit = inh[0]

                for instance in instances:
                    instance = instance.strip()

                    if not instance:
                        continue

                    if not isinstance(result.get(instance), dict):
                        raise iniparser.ParsingError(
                            "Couldn't find section: " + instance, token[2], token[1]
                        )

                    result[inherit].update(result[instance])

        elif token[0] == "ini":
            if inherit:
                section = iniparser._parse_section(token[1])

                if section:
                    result[inherit].update(iniparser.read(inherit_segment))
                    inherit = None
                    inherit_segment = ""
                else:
                    inherit_segment += f"{token[1]}\n"
                    last_type = "ltx"
                    continue

            if token[0] == "ini":
                segment += f"{token[1]}\n"
        last_type = token[0]

    if segment:
        result.update(iniparser.read(segment))

    if inherit and inherit_segment:
        result[inherit].update(iniparser.read(inherit_segment))

    _parse_interps(result)
    return result
