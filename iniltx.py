import io
import os
import re

import iniparser

_RE_MACRO = re.compile(r"^\#(?P<name>[a-zA-Z_]+)\s+(?P<value>.+)$")
_RE_INHERIT = re.compile(
    r"^\[(?P<section>[a-zA-Z0-9_-]+)\]\:(?P<instance>[a-zA-Z0-9_-]+)$"
)


def _parse_macro(string: str):
    macro = _RE_MACRO.match(string)

    if macro:
        return macro.groups()


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

        if not _parse_macro(line) and not _parse_inherit(line):
            result.append(["ini", line, lineno])
        else:
            result.append(["ltx", line, lineno])

    return result


def parse(tokens: list[list[str]]):
    result = {}
    segment = ""
    last_type = None
    inherit = None
    inherit_segment = ""

    for token in tokens:
        if token[0] == "ltx":
            if last_type == "ini":
                result.update(iniparser.getall(segment))
                segment = ""

            macro = _parse_macro(token[1])

            if macro:
                if macro[0] == "include":
                    if os.path.isfile(macro[1]):
                        tokens = _tokenize(open(macro[1]).read())
                        result.update(parse(tokens))
                    else:
                        raise iniparser.ParsingError(
                            "File not found: " + macro[1], token[2], token[1]
                        )

            inh = _parse_inherit(token[1])

            if inh:
                if not isinstance(result.get(inh[1]), dict):
                    raise iniparser.ParsingError(
                        "Couldn't find section: " + inh[1], token[2], token[1]
                    )

                if inherit:
                    result[inherit].update(iniparser.getall(inherit_segment))
                    inherit_segment = ""

                result[inh[0]] = {}
                result[inh[0]].update(result[inh[1]])
                inherit = inh[0]

        elif token[0] == "ini":
            if inherit:
                section = iniparser._parse_section(token[1])

                if section:
                    result[inherit].update(iniparser.getall(inherit_segment))
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
        result.update(iniparser.getall(segment))

    if inherit and inherit_segment:
        result[inherit].update(iniparser.getall(inherit_segment))

    return result
