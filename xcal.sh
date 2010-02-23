#!/bin/sh
#
# Written by Denilson Figueiredo de Sa <denilsonsa@gmail.com>
# 2008-01-16 - Added These comments. And, even almost 5 years later, I still
#              use this script. :) I've configured to run it whenever I click
#              on the little clock on my dock/taskbar.
# 2003-10-20 - This script was born! One of my first scripts.

cal -y | xmessage -buttons Close -default Close -nearmouse -file -
