#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4

from __future__ import with_statement  # This isn't required in Python 2.6

import sys
import os.path
import quopri
from getopt import getopt, GetoptError


def print_help():
    print """
Usage: %s [files]

This script will convert the vNote text files received from mobile phones
via bluetooth. These files are simple plain-text at the phone, but are
received at the computer with many headers and encoded by quoted-printable.

If no parameters are passed, it will convert stdin, else, the passed files
are converted. In both cases, the output is printed at stdout.
""".strip() % (MYNAME,)
# Extra documentation:
# I receive these files at the computer using 'gnome-obex-server', part of
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
    # print repr(decoded["BODY"])
    print decoded["BODY"].decode("latin-1").encode("utf-8")


############################################################
# Parsing arguments
MYNAME = os.path.basename(sys.argv[0])

try:
    opts, args = getopt(sys.argv[1:], "h", "help".split())
except GetoptError, e:
    print str(e)
    print "Try '%s --help' for more information." % (MYNAME,)
    sys.exit(2)

for option, value in opts:
    if option in ("-h", "--help"):
        print_help()
        sys.exit()

sys.argv = sys.argv[0:1] + args

############################################################
# Doing the job

if len(args) == 0:
    args = ["-"]

for f in args:
    if f == "-":
        decode_vnote(sys.stdin.read())
    else:
        with open(f) as file:
            decode_vnote(file.read())
