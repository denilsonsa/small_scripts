#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

# This program is a simple and easy-to-use interface to setxkbmap.
#
# It can set keyboard options for only one keyboard (instead of all connected
# keyboards).
#
# It has some hardcoded layouts, variants and options that are useful for me.
# If you want to use this script and you are not from Brazil, you will probably
# want to change the hardcoded menu items below.
#
# No, I don't want to "bloat" this script adding an external configuration
# file. The script itself *is* the configuration file.
#
#
# Tested with:
#   Python        2.7.1         http://www.python.org/
#   pythondialog  2.7           http://pythondialog.sourceforge.net/
#   dialog        1.1.20100428  http://invisible-island.net/dialog/dialog.html
#   xinput        1.5.3         http://xorg.freedesktop.org/
#   xorg-server   1.10.4        http://xorg.freedesktop.org/
#   xorg-x11      7.4           http://xorg.freedesktop.org/


from __future__ import print_function

import re
import subprocess
import dialog


# Sample 'xinput -list' output:
#⎡ Virtual core pointer                    	id=2	[master pointer  (3)]
#⎜   ↳ Virtual core XTEST pointer              	id=4	[slave  pointer  (2)]
#⎜   ↳ Microsoft  Microsoft Basic Optical Mouse v2.0 	id=10	[slave  pointer  (2)]
#⎜   ↳ SynPS/2 Synaptics TouchPad              	id=13	[slave  pointer  (2)]
#⎜   ↳ Microsoft Microsoft® 2.4GHz Transceiver v8.0	id=14	[slave  pointer  (2)]
#⎜   ↳ Microsoft Microsoft® 2.4GHz Transceiver v8.0	id=15	[slave  pointer  (2)]
#⎣ Virtual core keyboard                   	id=3	[master keyboard (2)]
#    ↳ Virtual core XTEST keyboard             	id=5	[slave  keyboard (3)]
#    ↳ Power Button                            	id=6	[slave  keyboard (3)]
#    ↳ Video Bus                               	id=7	[slave  keyboard (3)]
#    ↳ Sleep Button                            	id=8	[slave  keyboard (3)]
#    ↳ USB2.0 1.3M UVC WebCam                  	id=9	[slave  keyboard (3)]
#    ↳ Asus Laptop extra buttons               	id=11	[slave  keyboard (3)]
#    ↳ AT Translated Set 2 keyboard            	id=12	[slave  keyboard (3)]
#    ↳ Microsoft Microsoft® 2.4GHz Transceiver v8.0	id=16	[slave  keyboard (3)]

RE_XINPUT_LIST = re.compile(ur'''
    ^
    [\u239b-\u23bf]?  # Ignoring the leading "box" char
    \s*
    [\u2190-\u21ff]?  # Ignoring the arrow
    \s*
    (?P<name>.+?)
    \s+
    id=(?P<id>[0-9]+)
    \s+
    (?P<typestring>\[.+?\])
    \s*$
    ''',
    re.VERBOSE
)

RE_XINPUT_DEVICE_TYPE = re.compile(r'''
    ^ \s* \[? \s*
    (?P<typename>[a-zA-Z ]+?)
    \s*
    (?:
        \(
        (?P<attachment>[0-9]+)
        \)
    )?
    \s* \]? \s* $
    ''',
    re.VERBOSE
)

RE_SIMPLE_STRING = re.compile(r'^[-a-zA-Z0-9_/:.,=+]*$')


def arg_to_shell_string(arg):
    '''Receives a string and tries to quote it to be shell-safe.
    Useful when printing what command-line will be run.

    Warning: tab and newline characters are not escaped.
    '''

    if arg == '':
        # If the string is empty, return an empty string surrounded by
        # single-quotes.
        return "''"

    match = RE_SIMPLE_STRING.match(arg)
    if match:
        # If the string is simple enough, there is no need for quotes or
        # escapes.
        return arg

    # Enclose the string into single-quotes.
    # Must also escape single-quotes. Things get ugly, but should work.
    # echo 'aaa'"'"'bbb' => aaa'bbb
    return "'" + arg.replace("'", "'\"'\"'") + "'"


def args_to_cmdstring(args):
    return ' '.join(arg_to_shell_string(arg) for arg in args)


def echo_run(args):
    '''Prints the commandline and then runs it.'''
    cmdstring = args_to_cmdstring(args)
    print(cmdstring)
    subprocess.call(args)


class XInputDeviceType(object):
    def __init__(self, typestring):
        # Default values
        self.is_slave = False
        self.is_master = False
        self.is_pointer = False
        self.is_keyboard = False
        self.attachment = None

        self.typestring = typestring
        match = RE_XINPUT_DEVICE_TYPE.match(typestring)
        if match:
            self.typename = match.group('typename')
            self.attachment = match.group('attachment')

            if 'slave' in self.typename: self.is_slave = True
            if 'master' in self.typename: self.is_master = True
            if 'pointer' in self.typename: self.is_pointer = True
            if 'keyboard' in self.typename: self.is_keyboard = True
        else:
            self.typename = 'unknown'

    def __str__(self):
        return self.typestring

    def __repr__(self):
        return 'XInputDeviceType({0})'.format(
            repr(self.typestring)
        )


class XInputDevice(object):
    def __init__(self, name, id, typestring):
        self.name = name   # XIDeviceInfo->name
        self.id = int(id)  # XIDeviceInfo->deviceid
        self.type = XInputDeviceType(typestring)

    def __str__(self):
        return '{0:2} {1} {2}'.format(
            self.id,
            self.name,
            self.type
        )

    def __repr__(self):
        return 'XInputDevice({0}, {1}, {2})'.format(
            repr(self.name),
            repr(self.id),
            repr(self.type),
        )


def list_devices_from_xinput():
    '''Returns a list of devices.'''

    devices = []
    output = subprocess.check_output(['xinput', '-list'])
    output = output.decode('utf8')
    for line in output.splitlines():
        match = RE_XINPUT_LIST.match(line)
        if match:
            dev = XInputDevice(**match.groupdict())
            devices.append(dev)
        else:
            # else, ignoring unknown lines
            pass
    return devices


class Program(object):
    def __init__(self):
        self.d = dialog.Dialog(dialog='dialog')
        self.d.add_persistent_args([
            '--tab-correct',
            '--backtitle', 'setxkbmap interactive dialog',
        ])

    def setxkbmap_main_menu(self):
        choices = [
            ('-query', ''),
            ('-print', ''),
            ('Change settings', ''),
        ]

        (returncode, tag) = self.d.menu(
            'Select an action',
            title='setxkbmap',
            choices=choices,
            height=0, width=0, menu_height=0
        )
        if returncode == 0:
            # -verbose 10
            if tag == '-query':
                echo_run(['setxkbmap', '-query'])
            elif tag == '-print':
                echo_run(['setxkbmap', '-print'])
            elif tag == 'Change settings':
                self.setxkbmap_change_settings()
        else:
            return None

    def select_keyboard_dialog(self):
        '''Opens a dialog and returns the keyboard id selected by the user.
        Returns None if the user cancels.
        '''

        choices = [
            (
                str(dev.id),
                u'{0} {1}'.format(dev.name, dev.type.typestring)
            )
            for dev in list_devices_from_xinput()
            if dev.type.is_keyboard
        ]
        choices.insert(0, ('all', '-all-'))

        (returncode, tag) = self.d.menu(
            'Select a keyboard:',
            title='X Input keyboards',
            choices=choices,
            height=0, width=0, menu_height=0
        )
        if returncode == 0:
            if tag == 'all':
                return tag
            else:
                return int(tag)
        else:
            return None

    def select_layout_variant_dialog(self):
        '''Opens a dialog and returns a tuple (layout, variant).
        Returns None if the user cancels.
        '''

        choices = [
            ('_',                  'don\'t change'),
            ('br_abnt2',           'Portuguese (Brazil)'),
            ('br_dvorak',          'Portuguese (Brazil, Dvorak)'),
            ('us_basic',           'English (US)'),
            ('us_intl',            'English (US, international with dead keys)'),
            ('us_alt-intl',        'English (US, alternative international)'),
            ('us_dvorak',          'English (Dvorak)'),
            ('us_dvorak-intl',     'English (Dvorak international with dead keys)'),
            ('us_dvorak-alt-intl', 'English (Dvorak alternative international no dead keys)'),
            ('us_dvorak-l',        'English (left handed Dvorak)'),
            ('us_dvorak-r',        'English (right handed Dvorak)'),
            ('us_dvorak-classic',  'English (classic Dvorak)'),
            ('us_dvp',             'English (programmer Dvorak)'),
            ('us_mac',             'English (Macintosh)'),
            ('us_altgr-intl',      'English (international AltGr dead keys)'),
            ('us_unicode',         'English (US, international AltGr Unicode combining)'),
        ]

        (returncode, tag) = self.d.menu(
            'Select a keyboard layout+variant:',
            title='Keyboard layouts and variants',
            choices=choices,
            height=0, width=0, menu_height=0
        )
        if returncode == 0:
            tmp = tag.partition('_')
            return (tmp[0], tmp[2])
        else:
            return None

    def select_options_dialog(self):
        '''Opens a dialog and returns a list of selected options.
        Returns None if the user cancels.
        '''

        choices = [
            ('CLEAR',                   'Clear all previously set options', 1),

            ('>> keypad',               'Numeric keypad layout selection', 0),
            ('keypad:legacy',           'Legacy', 0),
            ('keypad:oss',              'Unicode additions (arrows and math operators)', 0),
            ('keypad:hex',              'Hexadecimal', 0),
            ('keypad:atm',              'ATM/phone-style', 0),

            ('>> caps',                 'Caps Lock key behavior', 0),
            ('caps:escape',             'Make Caps Lock an additional ESC', 1),
            ('caps:backspace',          'Make Caps Lock an additional Backspace', 0),
            ('caps:super',              'Make Caps Lock an additional Super', 0),
            ('caps:hyper',              'Make Caps Lock an additional Hyper', 0),
            ('caps:shiftlock',          'Caps Lock toggles Shift so all keys are affected', 0),
            ('caps:none',               'Caps Lock is disabled', 0),

            ('>> compat',               'Miscellaneous compatibility options', 0),
            ('numpad:pc',               'Default numeric keypad keys', 0),
            ('numpad:mac',              'Numeric keypad keys work as with Macintosh', 0),
            ('numpad:microsoft',        'Shift with numeric keypad keys works as in MS Windows', 1),
            ('numpad:shift3',           'Shift does not cancel Num Lock, chooses 3rd level instead', 0),
            ('apple:alupckeys',         'Apple Aluminium Keyboard: emulate PC keys (Print, Scroll Lock, Pause, Num Lock)', 0),

            ('>> terminate',            'Key sequence to kill the X server', 0),
            ('terminate:ctrl_alt_bksp', 'Control + Alt + Backspace', 0),

            ('>> altwin',               'Alt/Win key behavior', 0),
            ('altwin:menu',             'Add the standard behavior to Menu key', 0),
            ('altwin:meta_alt',         'Alt and Meta are on Alt keys', 0),
            ('altwin:ctrl_win',         'Control is mapped to Win keys (and the usual Ctrl keys)', 0),
            ('altwin:ctrl_alt_win',     'Control is mapped to Alt keys, Alt is mapped to Win keys', 0),
            ('altwin:meta_win',         'Meta is mapped to Win keys', 0),
            ('altwin:left_meta_win',    'Meta is mapped to Left Win', 0),
            ('altwin:hyper_win',        'Hyper is mapped to Win-keys', 0),
            ('altwin:alt_super_win',    'Alt is mapped to Right Win, Super to Menu', 0),
            ('altwin:swap_lalt_lwin',   'Left Alt is swapped with Left Win', 0),
            # This one is now default, no need to explicitly set it.
            # https://bugs.freedesktop.org/show_bug.cgi?id=19500
            # http://cgit.freedesktop.org/xkeyboard-config/commit/symbols/altwin?id=5de02aa07a8d4bbe1957af3a38212c3507f2436f
            #('altwin:super_win',        '', 1),

            ('>> Compose key',          'Compose key position', 0),
            ('compose:ralt',            'Right Alt', 0),
            ('compose:lwin',            'Left Win', 0),
            ('compose:rwin',            'Right Win', 0),
            ('compose:menu',            'Menu', 1),
            ('compose:lctrl',           'Left Ctrl', 0),
            ('compose:rctrl',           'Right Ctrl', 0),
            ('compose:caps',            'Caps Lock', 0),
            ('compose:102',             '<Less/Greater>', 0),
            ('compose:paus',            'Pause', 0),
            ('compose:prsc',            'PrtSc', 0),
            ('compose:sclk',            'Scroll Lock', 0),
        ]

        (returncode, tags) = self.d.checklist(
            'Select the desired options:',
            title='Keyboard options',
            choices=choices,
            height=0, width=0, list_height=0
        )
        if returncode == 0:
            tags = [tag for tag in tags if not tag.startswith('>>')]
            if tags[0] == 'CLEAR':
                tags[0] = ''
            return tags
        else:
            return None

    def confirm_run_command(self, command):
        returncode = self.d.yesno(
            'About to run the following command:\n'
            '\n'
            '{0}'
            '\n'
            '\n'
            'Confirm?'.format(command),
            title='Confirm command',
            height=0, width=0
        )
        if returncode == 0:
            return True
        elif returncode == 1:
            return False
        else:
            return None

    def setxkbmap_change_settings(self):
        setxkbmap_cmdline = ['setxkbmap']

        # Selecting a keyboard
        kbd = self.select_keyboard_dialog()
        if kbd is None:
            return
        else:
            if kbd == 'all':
                pass
            else:
                setxkbmap_cmdline.extend(['-device', str(kbd)])

        # Choosing a layout
        lv = self.select_layout_variant_dialog()
        if lv is None:
            return
        else:
            layout, variant = lv
            if layout:
                setxkbmap_cmdline.extend(['-layout', layout])
            if variant:
                setxkbmap_cmdline.extend(['-variant', variant])

        # Choosing options
        opts = self.select_options_dialog()
        if opts is None:
            return
        else:
            for opt in opts:
                setxkbmap_cmdline.extend(['-option', opt])

        # Final confirmation
        cmdstring = args_to_cmdstring(setxkbmap_cmdline)
        confirm = self.confirm_run_command(cmdstring)
        #if confirm is None:
        #    return
        if confirm:
            echo_run(setxkbmap_cmdline)

    def run(self):
        self.setxkbmap_main_menu()


if __name__ == '__main__':
    p = Program()
    p.run()
