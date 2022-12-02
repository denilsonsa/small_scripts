#!/usr/bin/env python
# vi:ts=4 sw=4 et

import re
import sys


def embedScriptsAndStyles(fin, fout):
    """Reads an HTML file and tries to embed the scripts and stylesheets.

    Only one script or stylesheet per input line is supported. The entire line
    is discarded, so there should be no other markup in there. Any attribute
    (such as language or type) is also discarded.

    fin:  File-like input object for reading.
    fout: File-like output object for writing.
    """
    re_script = re.compile(
        r"""
            \s* <script \s [^>]* (?:
                src="([^">]+)"  |
                src='([^'>]+)'  |
                src=([^\s>'"]+)
            ) [^>]* > \s* </script>
        """,
        re.I | re.VERBOSE,
    )
    re_style = re.compile(
        r"""
            \s*
            <link \s [^>]* rel=['"]?stylesheet['"]? \s [^>]*  (?:
                href="([^">]+)"  |
                href='([^'>]+)'  |
                href=([^\s>'"]+)
            ) [^>]* >
            |
            \s*
            <link \s [^>]* (?:
                href="([^">]+)"  |
                href='([^'>]+)'  |
                href=([^\s>'"]+)
            ) \s [^>]* rel=['"]?stylesheet['"]? [^>]* >
        """,
        re.VERBOSE,
    )

    for line in fin:
        prefix = ""
        external_file = None
        suffix = ""

        match = re_script.match(line)
        if match:
            prefix = "<script>\n"
            external_file = [g for g in match.groups() if g][0]
            suffix = "\n</script>\n"
        else:
            match = re_style.match(line)
            if match:
                prefix = "<style>\n"
                external_file = [g for g in match.groups() if g][0]
                suffix = "\n</style>\n"

        if external_file:
            fout.write(prefix)
            fout.writelines(open(external_file))
            fout.write(suffix)
        else:
            fout.write(line)


def main():
    if len(sys.argv) == 1:
        embedScriptsAndStyles(sys.stdin, sys.stdout)
    elif len(sys.argv) == 2:
        embedScriptsAndStyles(open(sys.argv[1]), sys.stdout)
    else:
        print("Wrong arguments.")


if __name__ == "__main__":
    main()
