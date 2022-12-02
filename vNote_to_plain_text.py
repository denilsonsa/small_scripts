#!/usr/bin/env python
# vi:ts=4 sw=4

import argparse
import sys
import quopri


# Extra documentation:
# I receive these files at the computer using `gnome-obex-server`, part of
# gnome-bluetooth package. Then, at the mobile phone, I just choose the note
# and select Send Via Bluetooth.


def decode_vnote(vnote_as_str):
    # Sample input string:
    #
    # BEGIN:VNOTE
    # VERSION:1.1
    # BODY;ENCODING=QUOTED-PRINTABLE:Sexta=0A12.10 almo=E7o=0A4.30 salgados + ref=
    # resco=0ADomingo=0A2.00=0A13.00 na press=E3o=0A3.50 sorvete=0A2.00=0ASegunda=
    # =0A9.40=0A3.90 sorvete=0AQuarta=0A12.10=0A6.80 shampoo=0A10.90 pizza patron=
    # i=0AQuinta=0A1.50=0A10.90=0A34.80=0A1.90
    # DCREATED:20081024T110847Z
    # LAST-MODIFIED:20081030T232034Z
    # CLASS:PUBLIC
    # X-IRMC-LUID:0000000100A9
    # END:VNOTE
    decoded = vnote_as_str.strip()
    decoded = decoded.replace("=\r\n", "")
    decoded = decoded.splitlines()
    # decoded = [x.split(":",1) for x in decoded]
    decoded = [list(x.partition(":")[::2]) for x in decoded]  # "a:b" -> ["a","b"]
    for x in decoded:
        x[0] = x[0].partition(";")[0]  # "a;b" -> "a"
    decoded = dict(decoded)
    decoded["BODY"] = quopri.decodestring(decoded["BODY"])
    # print(repr(decoded["BODY"]))
    return decoded["BODY"].decode("latin-1")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="""
            This script will convert the vNote text files received from mobile phones
            via bluetooth. These files are simple plain-text at the phone, but are
            received at the computer with many headers and encoded by quoted-printable.
        """,
        epilog="""
            If no parameters are passed, it will convert stdin, else, the passed files
            are converted. In both cases, the output is printed at stdout.
        """,
    )
    parser.add_argument(
        "files",
        nargs="*",
        type=argparse.FileType("r"),
        default=[sys.stdin],
        help="vNote files (or stdin)",
    )
    return parser.parse_args()


def main():
    options = parse_arguments()
    for f in options.files:
        print(decode_vnote(f.read()))


if __name__ == "__main__":
    main()
