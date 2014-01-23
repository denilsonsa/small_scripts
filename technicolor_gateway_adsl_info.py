#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

import pyparsing
import requests
import sys

# These pages use an embedded script to load the actual status.
# http://192.168.1.1/atm_main.htm
# http://192.168.1.1/atm_dsl.htm?ov=1

# There are two possible script URLs:
#
# http://192.168.1.1/cgi/cgi_adsl_info.cgi
#
# adsl_status=[7,1,568,11289,28,12,16,32,4150,0,71804,0,0x0000,0x0004,184122,2887817468,1634140344,12,17,"---","---",0,2144,0,12339,0,341051522,43088557];
#
# var ADSLMode={
# 0x0001:"T1.413 Issue 2" 		,	//ADSL_DRV_MODE_T1413_ISSUE2
# 0x0002:"G.lite" 				, //ADSL_DRV_MODE_992_2AB
# 0x0004:"G.992.1"			,	//ADSL_DRV_MODE_992_1A*/
# 0x0008:"G992_1_B"			, //ADSL_DRV_MODE_992_1B
#
# 0x0100:"G.992.3"			, //ADSL_DRV_MODE_992_3A
# 0x0200:"G992_3_B"			, //ADSL_DRV_MODE_992_3B
#
# 0x0400:"G992_3_I"			, //ADSL_DRV_MODE_992_3I
# 0x0800:"G992_3_J"			, //ADSL_DRV_MODE_992_3J
#
# 0x1000:"G.992.3 Annex-L"			, //ADSL_DRV_MODE_992_3L
# 0x2000:"G.992.3 Annex-M"			, //ADSL_DRV_MODE_992_3M
# 0x4000:"G992_5_B"			, //ADSL_DRV_MODE_992_5B
# 0x8000:"G.992.5"			, //ADSL_DRV_MODE_992_5A
# 0x0000:"Unknown Mode"
# };
#
# var ADSLMode_ext={
# 0x0001:"G992_5_I"			, //ADSL_DRV_MODE_992_5I
# 0x0002:"G992_5_J"			, //ADSL_DRV_MODE_992_5J
# 0x0004:"G.992.5 Annex-M"			, //ADSL_DRV_MODE_992_5M
# 0x0008:"Automatic"			, //AUTO
# 0x0000:"Unknown Mode"
# }
#
# http://192.168.1.1/cgi/cgi_atm_info.cgi
#
# var ADSL_VC_MAX=8;
# var ATM_STATE=[["PVC0",33,0,1,4,"189.12.218.15","255.255.0.0","200.217.90.90",1,0,1,"8.8.8.8","8.8.4.4",184121,13849147,2887817156,8357111,1634142502],["PVC1",0,0,1,0,"0.0.0.0","0.0.0.0","0.0.0.0",1,0,0,"8.8.8.8","8.8.4.4",184121,0,0,0,0],["PVC2",0,0,0,0,"0.0.0.0","0.0.0.0","0.0.0.0",1,0,0,"8.8.8.8","8.8.4.4",184121,0,0,0,0],["PVC3",0,0,0,0,"0.0.0.0","0.0.0.0","0.0.0.0",1,0,0,"8.8.8.8","8.8.4.4",184121,0,0,0,0],["PVC4",0,0,0,0,"0.0.0.0","0.0.0.0","0.0.0.0",1,0,0,"8.8.8.8","8.8.4.4",184121,0,0,0,0],["PVC5",0,0,0,0,"0.0.0.0","0.0.0.0","0.0.0.0",1,0,0,"8.8.8.8","8.8.4.4",184121,0,0,0,0],["PVC6",0,0,0,0,"0.0.0.0","0.0.0.0","0.0.0.0",1,0,0,"8.8.8.8","8.8.4.4",184121,0,0,0,0],["PVC7",0,0,0,0,"0.0.0.0","0.0.0.0","0.0.0.0",1,0,0,"8.8.8.8","8.8.4.4",184121,0,0,0,0],[null]];
# adsl_status=[7,1,568,11289,28,12,16,32,4150,0,71804,0,0x0000,0x0004,184122,2887817468,1634142614,12,17,"---","---",0,2144,0,12339,0,341051522,43088557];
# var uptime=184165;
#
# defualt_route_num=3;
# addCfg("LANIP",999,"192.168.1.1");
# addCfg("LANMASK",888,"255.255.255.0");
# addCfg("ATM_PVC1",1,"PVC0|4|0|33|1|1|4000|4000|10|1|0.0.0.0|0.0.0.0|0.0.0.0|0|1|0|20|velox@oi.com.br|12345|1492|0|1");
# addCfg("ATM_PVC2",2,"PVC1|0|0|0|1|2|3000|3000|10|1||||0|1|0|20|||1492|0|0");
# addCfg("ATM_PVC3",3,"PVC2|0|0|0|0|1|4000|4000|10|1||||0|1|0|20|||1492|0|0");
# addCfg("ATM_PVC4",4,"PVC3|0|0|0|0|1|4000|4000|10|1||||0|1|0|20|||1492|0|0");
# addCfg("ATM_PVC5",5,"PVC4|0|0|0|0|1|4000|4000|10|1||||0|1|0|20|||1492|0|0");
# addCfg("ATM_PVC6",6,"PVC5|0|0|0|0|1|4000|4000|10|1||||0|1|0|20|||1492|0|0");
# addCfg("ATM_PVC7",7,"PVC6|0|0|0|0|1|4000|4000|10|1||||0|1|0|20|||1492|0|0");
# addCfg("ATM_PVC8",8,"PVC7|0|0|0|0|1|4000|4000|10|1||||0|1|0|20|||1492|0|0");
# addCfg("LAN_DHCPD_EN",111,"1");
# addCfg("NAT_VC_LIST",10,"0|0|0|0|0|0|0|0");
# addCfg("dns1",0x34,"8.8.8.8");
# addCfg("dns2",0x35,"8.8.4.4");
# var curr_user="admin";

# Documentation:
# adsl_status (each index):
# 0: If == 7, then check if any ATM_STATE[i][10] == 1. If yes, then the connection is okay.
#    If != 7, then the link status is at ATMStatus_Msg[0] and ADSL_mode is Unknown.
# 1: Unknown, unused?
# 2: ActualDataRateUpstream (Bandwidth, kbps).
# 3: ActualDataRateDownstream (Bandwidth, kbps).
# 4: NoiseMarginUpstream (Signal to Noise Margin, dB).
# 5: NoiseMarginDownstream (Signal to Noise Margin, dB).
# 6: AttenuationUpstream (Line Attenuation, dB).
# 7: AttenuationDownstream (Line Attenuation, dB).
# 8: CRCErrorNearEndIndicator (CRC Errors Up).
# 9: CRCErrorFarEndIndicator (CRC Errors Down).
# 10: HECErrorNearEndIndicator (HEC Errors Up).
# 11: HECErrorFarEndIndicator (HEC Errors Down).
# 12: If != 0, it is the index of ADSLMode[adsl_status[12]].
# 13: If [12] == 0, it is the index of ADSLMode_ext[adsl_status[13]].
# 14: ADSLUptime (seconds).
# 15: ActualReceiveData (Data Transferred, bytes).
# 16: ActualSentData (Data Transferred, bytes).
# 17: OutputPowerUP (dBm).
# 18: OutputPowerDN (dBm).
# 19: VendorIDLC (Vendor ID Local).
# 20: VendorIDRE (Vendor ID Remote).
# 21: LossofLinkRE (Loss of Link (Remote)).
# 22: ErrorSecondsLC (Error Seconds Local).
# 23: ErrorSecondsRE (Error Seconds Local).
# 24: FECErrorsUP (FEC Errors Up).
# 25: FECErrorsDN (FEC Errors Down).
# 26: cellcountLC (CELL Count Local).
# 27: cellcountRE (CELL Count Remote).
#
# See also: http://www.dslreports.com/faq/16220


def fetch_modem_status(hostname='dsldevice.lan', username='', password=''):
    url = 'http://{0}/cgi/cgi_adsl_info.cgi'.format(hostname)
    # Explicit auth is not required, because the library can already read from
    # ~/.netrc.
    auth = (username, password) if username or password else None
    r = requests.get(
        url,
        cookies={'language_flag': '0'},  # To force English language.
        auth=auth
    )
    r.raise_for_status()
    return r.text


def parse_javascript_vars(data):
    '''Receives a string of JavaScript-like data and tries to parse it.

    Returns a dict with each var.

    Several assumptions are made:
    - Only the assignment operator '=' is supported.
    - The script is composed of one or more assignments, and nothing else.
    - The "var " prefix before an assignment is optional.
    - No variable is assigned more than once.
    - Comments should be correctly ignored, as well as whitespace.
    - Values can be numbers, strings, arrays or dictionaries.
    - Arrays and dictionaries can only contain number and strings.
    - Dictionary keys can be numbers, strings, or an identifier.

    Sample input for this grammar:
      var i = 0;  // Optional var, optional semicolon.
      j = 0x10  // 16
      k = -010  // -8
      f = 1.0
      g = +.9   // Optional leading 0, optional signal.
      s = 'single quoted'
      t = "double quoted"
      a = []
      b = [0, 1, 'string', "double", 3.14]
      c = {}
      d = {
        foo: 'without quotes',
        'bar': "as a string",
        3: 'as a number'
      }

    This code can parse cgi_adsl_info.cgi, but it can't parse cgi_atm_info.cgi.
    '''
    from pyparsing import Combine, Dict, Group, Keyword, LineEnd, OneOrMore, \
        Optional, StringEnd, Suppress, White, Word, alphanums, alphas, \
        cppStyleComment, dblQuotedString, dblSlashComment, delimitedList, \
        hexnums, nums, removeQuotes, sglQuotedString

    # AKA identifier.
    varname = Word(alphas + '_$', alphanums + '_$')

    # This Optional(Suppress(White)) is required to because of the firstOf
    # operator when defining number.
    number_signal = Optional(Word('-+', exact=1)) + Optional(Suppress(White()))
    decimal_number = number_signal + Word('123456789', nums)
    # Scientific notation is not supported.
    float_number = number_signal + Optional(Word(nums)) + '.' + Word(nums)
    # For convenience, zero is considered an octal number.
    octal_number = number_signal + Word('0', '01234567')
    hex_number = number_signal + '0x' + Word(hexnums)
    number = Combine(float_number | decimal_number | hex_number | octal_number)

    def convert_number(toks):
        s = toks[0]
        signal = s[0] if s[0] in '+-' else ''
        number = s[1:] if signal else s

        if '.' in s:
            return float(s)
        elif number.startswith('0x'):
            return int(signal + number[2:], base=16)
        elif number.startswith('0'):
            return int(s, base=8)
        else:
            return int(s, base=10)

    number.setParseAction(convert_number)

    string = (dblQuotedString.setParseAction(removeQuotes) |
              sglQuotedString.setParseAction(removeQuotes))

    # Nested arrays/dicts are not supported.
    array_list = Group(Suppress('[') +
                       Optional(delimitedList(number | string)) +
                       Suppress(']'))

    array_associative = Group(Dict(Suppress('{') +
                                   Optional(delimitedList(Group(
                                       (number | string | varname) +
                                       Suppress(':') +
                                       (number | string)
                                   ))) +
                                   Suppress('}')))

    value = number | string | array_list | array_associative

    assignment = Group(Optional(Suppress(Keyword('var'))) +
                       varname +
                       Suppress('=') +
                       value +
                       Suppress(';' | LineEnd()))

    parser = Dict(OneOrMore(assignment)) + StringEnd()
    parser.ignore(dblSlashComment)
    parser.ignore(cppStyleComment)

    tree = parser.parseString(data)

    # Converting the pyparsing.ParseResults tree into a simple Python dict.
    ret = {}
    for var, subtree in tree.asDict().items():
        if isinstance(subtree, pyparsing.ParseResults):
            try:
                # Using .asDict() converts all integer keys to strings.
                # ret[var] = subtree.asDict()
                # Using .asList() retains numbers as numbers.
                ret[var] = dict(subtree.asList())
            except TypeError:
                ret[var] = subtree.asList()
        else:
            # Most likely already a number or string.
            ret[var] = subtree

    return ret


def _human_readable_prefix(num, unit, base, prefixes):
    if num < 1000:
        return '{0} {1}'.format(num, unit)

    i = 0
    while i + 1 < len(prefixes) and num >= base:
        num /= base
        i += 1

    precision = 0
    if round(num, 2) < 10:
        precision = 2
    elif round(num, 1) < 100:
        precision = 1
    elif round(num, 0) >= 1000 and i + 1 < len(prefixes):
        precision = 2
        num /= base
        i += 1

    return '{0:.{1}f} {2}{3}'.format(num, precision, prefixes[i], unit)


def human_readable_decimal_prefix(num, unit=''):
    '''
    >>> human_readable_decimal_prefix(1)
    '1 '
    >>> human_readable_decimal_prefix(10)
    '10 '
    >>> human_readable_decimal_prefix(100)
    '100 '
    >>> human_readable_decimal_prefix(123)
    '123 '
    >>> human_readable_decimal_prefix(999)
    '999 '
    >>> human_readable_decimal_prefix(1000)
    '1.00 k'
    >>> human_readable_decimal_prefix(1234)
    '1.23 k'
    >>> human_readable_decimal_prefix(9876)
    '9.88 k'
    >>> human_readable_decimal_prefix(9999)
    '10.0 k'
    >>> human_readable_decimal_prefix(10000)
    '10.0 k'
    >>> human_readable_decimal_prefix(12345)
    '12.3 k'
    >>> human_readable_decimal_prefix(98765)
    '98.8 k'
    >>> human_readable_decimal_prefix(99999)
    '100 k'
    >>> human_readable_decimal_prefix(100000)
    '100 k'
    >>> human_readable_decimal_prefix(123456)
    '123 k'
    >>> human_readable_decimal_prefix(987654)
    '988 k'
    >>> human_readable_decimal_prefix(999999)
    '1.00 M'
    >>> human_readable_decimal_prefix(1000000)
    '1.00 M'
    >>> human_readable_decimal_prefix(1234567)
    '1.23 M'
    >>> human_readable_decimal_prefix(9876543)
    '9.88 M'
    >>> human_readable_decimal_prefix(9999999)
    '10.0 M'
    >>> human_readable_decimal_prefix(10000000)
    '10.0 M'
    >>> human_readable_decimal_prefix(12345678)
    '12.3 M'
    >>> human_readable_decimal_prefix(98765432)
    '98.8 M'
    >>> human_readable_decimal_prefix(99999999)
    '100 M'
    >>> human_readable_decimal_prefix(100000000)
    '100 M'
    >>> human_readable_decimal_prefix(123456789)
    '123 M'
    >>> human_readable_decimal_prefix(987654321)
    '988 M'
    >>> human_readable_decimal_prefix(999999999)
    '1.00 G'
    >>> human_readable_decimal_prefix(1000000000)
    '1.00 G'
    >>> human_readable_decimal_prefix(1234567890)
    '1.23 G'
    >>> human_readable_decimal_prefix(9876543210)
    '9.88 G'
    >>> human_readable_decimal_prefix(9999999999)
    '10.0 G'
    >>> human_readable_decimal_prefix(10000000000)
    '10.0 G'
    >>> human_readable_decimal_prefix(12345678900)
    '12.3 G'
    >>> human_readable_decimal_prefix(98765432100)
    '98.8 G'
    >>> human_readable_decimal_prefix(99999999999)
    '100 G'
    >>> human_readable_decimal_prefix(100000000000)
    '100 G'
    >>> human_readable_decimal_prefix(123456789000)
    '123 G'
    >>> human_readable_decimal_prefix(987654321000)
    '988 G'
    >>> human_readable_decimal_prefix(999999999999)
    '1.00 T'
    >>> human_readable_decimal_prefix(1000000000000)
    '1.00 T'
    >>> human_readable_decimal_prefix(1234567890000)
    '1.23 T'
    >>> human_readable_decimal_prefix(9876543210000)
    '9.88 T'
    >>> human_readable_decimal_prefix(9999999999999)
    '10.0 T'
    >>> human_readable_decimal_prefix(10000000000000)
    '10.0 T'
    >>> human_readable_decimal_prefix(12345678900000)
    '12.3 T'
    >>> human_readable_decimal_prefix(98765432100000)
    '98.8 T'
    >>> human_readable_decimal_prefix(99999999999999)
    '100 T'
    >>> human_readable_decimal_prefix(100000000000000)
    '100 T'
    >>> human_readable_decimal_prefix(123456789000000)
    '123 T'
    >>> human_readable_decimal_prefix(987654321000000)
    '988 T'
    >>> human_readable_decimal_prefix(999999999999999)
    '1.00 P'
    >>> human_readable_decimal_prefix(1000000000000000)
    '1.00 P'
    >>> human_readable_decimal_prefix(1234567890000000)
    '1.23 P'
    >>> human_readable_decimal_prefix(9876543210000000)
    '9.88 P'
    >>> human_readable_decimal_prefix(9999999999999999)
    '10.0 P'
    >>> human_readable_decimal_prefix(10000000000000000)
    '10.0 P'
    >>> human_readable_decimal_prefix(12345678900000000)
    '12.3 P'
    >>> human_readable_decimal_prefix(98765432100000000)
    '98.8 P'
    >>> human_readable_decimal_prefix(99999999999999999)
    '100 P'
    >>> human_readable_decimal_prefix(100000000000000000)
    '100 P'
    >>> human_readable_decimal_prefix(123456789000000000)
    '123 P'
    >>> human_readable_decimal_prefix(987654321000000000)
    '988 P'
    >>> human_readable_decimal_prefix(999999999999999999)
    '1.00 E'
    >>> human_readable_decimal_prefix(1000000000000000000)
    '1.00 E'
    >>> human_readable_decimal_prefix(1234567890000000000)
    '1.23 E'
    >>> human_readable_decimal_prefix(9876543210000000000)
    '9.88 E'
    >>> human_readable_decimal_prefix(9999999999999999999)
    '10.0 E'
    >>> human_readable_decimal_prefix(10000000000000000000)
    '10.0 E'
    >>> human_readable_decimal_prefix(12345678900000000000)
    '12.3 E'
    >>> human_readable_decimal_prefix(98765432100000000000)
    '98.8 E'
    >>> human_readable_decimal_prefix(99999999999999999999)
    '100 E'
    >>> human_readable_decimal_prefix(100000000000000000000)
    '100 E'
    >>> human_readable_decimal_prefix(123456789000000000000)
    '123 E'
    >>> human_readable_decimal_prefix(987654321000000000000)
    '988 E'
    >>> human_readable_decimal_prefix(999999999999999999999)
    '1.00 Z'
    >>> human_readable_decimal_prefix(1000000000000000000000)
    '1.00 Z'
    >>> human_readable_decimal_prefix(1234567890000000000000)
    '1.23 Z'
    >>> human_readable_decimal_prefix(9876543210000000000000)
    '9.88 Z'
    >>> human_readable_decimal_prefix(9999999999999999999999)
    '10.0 Z'
    >>> human_readable_decimal_prefix(10000000000000000000000)
    '10.0 Z'
    >>> human_readable_decimal_prefix(12345678900000000000000)
    '12.3 Z'
    >>> human_readable_decimal_prefix(98765432100000000000000)
    '98.8 Z'
    >>> human_readable_decimal_prefix(99999999999999999999999)
    '100 Z'
    >>> human_readable_decimal_prefix(100000000000000000000000)
    '100 Z'
    >>> human_readable_decimal_prefix(123456789000000000000000)
    '123 Z'
    >>> human_readable_decimal_prefix(987654321000000000000000)
    '988 Z'
    >>> human_readable_decimal_prefix(999999999999999999999999)
    '1.00 Y'
    >>> human_readable_decimal_prefix(1000000000000000000000000)
    '1.00 Y'
    >>> human_readable_decimal_prefix(1234567890000000000000000)
    '1.23 Y'
    >>> human_readable_decimal_prefix(9876543210000000000000000)
    '9.88 Y'
    >>> human_readable_decimal_prefix(9999999999999999999999999)
    '10.0 Y'
    >>> human_readable_decimal_prefix(10000000000000000000000000)
    '10.0 Y'
    >>> human_readable_decimal_prefix(12345678900000000000000000)
    '12.3 Y'
    >>> human_readable_decimal_prefix(98765432100000000000000000)
    '98.8 Y'
    >>> human_readable_decimal_prefix(99999999999999999999999999)
    '100 Y'
    >>> human_readable_decimal_prefix(100000000000000000000000000)
    '100 Y'
    >>> human_readable_decimal_prefix(123456789000000000000000000)
    '123 Y'
    >>> human_readable_decimal_prefix(987654321000000000000000000)
    '988 Y'
    >>> human_readable_decimal_prefix(999999999999999999999999999)
    '1000 Y'
    >>> human_readable_decimal_prefix(1000000000000000000000000000)
    '1000 Y'
    >>>
    '''
    short_prefixes = ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
    # long_prefixes = ['', 'kilo', 'mega', 'giga', 'tera', 'peta', 'exa', 'zetta', 'yotta']
    return _human_readable_prefix(num, unit, 1000, short_prefixes)


def human_readable_binary_prefix(num, unit='B'):
    '''
    >>> human_readable_binary_prefix(1)
    '1 B'
    >>> human_readable_binary_prefix(10)
    '10 B'
    >>> human_readable_binary_prefix(100)
    '100 B'
    >>> human_readable_binary_prefix(123)
    '123 B'
    >>> human_readable_binary_prefix(999)
    '999 B'
    >>> human_readable_binary_prefix(1000)
    '0.98 KiB'
    >>> human_readable_binary_prefix(2**10 - 1)
    '1.00 KiB'
    >>> human_readable_binary_prefix(2**10)
    '1.00 KiB'
    >>> human_readable_binary_prefix(2**12)
    '4.00 KiB'
    >>> human_readable_binary_prefix(2**14)
    '16.0 KiB'
    >>> human_readable_binary_prefix(2**16)
    '64.0 KiB'
    >>> human_readable_binary_prefix(2**18)
    '256 KiB'
    >>> human_readable_binary_prefix(2**19)
    '512 KiB'
    >>> human_readable_binary_prefix(2**20 - 1)
    '1.00 MiB'
    >>> human_readable_binary_prefix(2**20)
    '1.00 MiB'
    >>> human_readable_binary_prefix(2**22)
    '4.00 MiB'
    >>> human_readable_binary_prefix(2**24)
    '16.0 MiB'
    >>> human_readable_binary_prefix(2**26)
    '64.0 MiB'
    >>> human_readable_binary_prefix(2**28)
    '256 MiB'
    >>> human_readable_binary_prefix(2**29)
    '512 MiB'
    >>> human_readable_binary_prefix(2**30 - 1)
    '1.00 GiB'
    >>> human_readable_binary_prefix(2**30)
    '1.00 GiB'
    >>> human_readable_binary_prefix(2**32)
    '4.00 GiB'
    >>> human_readable_binary_prefix(2**34)
    '16.0 GiB'
    >>> human_readable_binary_prefix(2**36)
    '64.0 GiB'
    >>> human_readable_binary_prefix(2**38)
    '256 GiB'
    >>> human_readable_binary_prefix(2**39)
    '512 GiB'
    >>> human_readable_binary_prefix(2**40 - 1)
    '1.00 TiB'
    >>> human_readable_binary_prefix(2**40)
    '1.00 TiB'
    >>> human_readable_binary_prefix(2**42)
    '4.00 TiB'
    >>> human_readable_binary_prefix(2**44)
    '16.0 TiB'
    >>> human_readable_binary_prefix(2**46)
    '64.0 TiB'
    >>> human_readable_binary_prefix(2**48)
    '256 TiB'
    >>> human_readable_binary_prefix(2**49)
    '512 TiB'
    >>> human_readable_binary_prefix(2**50 - 1)
    '1.00 PiB'
    >>> human_readable_binary_prefix(2**50)
    '1.00 PiB'
    >>> human_readable_binary_prefix(2**52)
    '4.00 PiB'
    >>> human_readable_binary_prefix(2**54)
    '16.0 PiB'
    >>> human_readable_binary_prefix(2**56)
    '64.0 PiB'
    >>> human_readable_binary_prefix(2**58)
    '256 PiB'
    >>> human_readable_binary_prefix(2**59)
    '512 PiB'
    >>> human_readable_binary_prefix(2**60 - 1)
    '1.00 EiB'
    >>> human_readable_binary_prefix(2**60)
    '1.00 EiB'
    >>> human_readable_binary_prefix(2**62)
    '4.00 EiB'
    >>> human_readable_binary_prefix(2**64)
    '16.0 EiB'
    >>> human_readable_binary_prefix(2**66)
    '64.0 EiB'
    >>> human_readable_binary_prefix(2**68)
    '256 EiB'
    >>> human_readable_binary_prefix(2**69)
    '512 EiB'
    >>> human_readable_binary_prefix(2**70 - 1)
    '1.00 ZiB'
    >>> human_readable_binary_prefix(2**70)
    '1.00 ZiB'
    >>> human_readable_binary_prefix(2**72)
    '4.00 ZiB'
    >>> human_readable_binary_prefix(2**74)
    '16.0 ZiB'
    >>> human_readable_binary_prefix(2**76)
    '64.0 ZiB'
    >>> human_readable_binary_prefix(2**78)
    '256 ZiB'
    >>> human_readable_binary_prefix(2**79)
    '512 ZiB'
    >>> human_readable_binary_prefix(2**80 - 1)
    '1.00 YiB'
    >>> human_readable_binary_prefix(2**80)
    '1.00 YiB'
    >>> human_readable_binary_prefix(2**82)
    '4.00 YiB'
    >>> human_readable_binary_prefix(2**84)
    '16.0 YiB'
    >>> human_readable_binary_prefix(2**86)
    '64.0 YiB'
    >>> human_readable_binary_prefix(2**88)
    '256 YiB'
    >>> human_readable_binary_prefix(2**89)
    '512 YiB'
    >>> human_readable_binary_prefix(2**90 - 1)
    '1024 YiB'
    >>> human_readable_binary_prefix(2**90)
    '1024 YiB'
    >>> human_readable_binary_prefix(2**92)
    '4096 YiB'
    >>> human_readable_binary_prefix(2**94)
    '16384 YiB'
    >>>
    '''
    # Source: http://en.wikipedia.org/wiki/Binary_prefix
    short_prefixes = ['',   'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi']
    # long_prefixes = ['', 'kibi', 'mebi', 'gibi', 'tebi', 'pebi', 'exbi', 'zebi', 'yobi']
    return _human_readable_prefix(num, unit, 1024, short_prefixes)


def human_readable_time(seconds, precision=3):
    '''
    >>> human_readable_time(1)
    '1 second'
    >>> human_readable_time(2)
    '2 seconds'
    >>> human_readable_time(59)
    '59 seconds'
    >>> human_readable_time(60)
    '1 minute'
    >>> human_readable_time(61)
    '1 minute, 1 second'
    >>> human_readable_time(62)
    '1 minute, 2 seconds'
    >>> human_readable_time(119)
    '1 minute, 59 seconds'
    >>> human_readable_time(120)
    '2 minutes'
    >>> human_readable_time(121)
    '2 minutes, 1 second'
    >>> human_readable_time(122)
    '2 minutes, 2 seconds'
    >>> human_readable_time(3599)
    '59 minutes, 59 seconds'
    >>> human_readable_time(3600)
    '1 hour'
    >>> human_readable_time(3601)
    '1 hour, 1 second'
    >>> human_readable_time(3602)
    '1 hour, 2 seconds'
    >>> human_readable_time(3659)
    '1 hour, 59 seconds'
    >>> human_readable_time(3660)
    '1 hour, 1 minute'
    >>> human_readable_time(3661)
    '1 hour, 1 minute, 1 second'
    >>> human_readable_time(3662)
    '1 hour, 1 minute, 2 seconds'
    >>> human_readable_time(3719)
    '1 hour, 1 minute, 59 seconds'
    >>> human_readable_time(3720)
    '1 hour, 2 minutes'
    >>> human_readable_time(3721)
    '1 hour, 2 minutes, 1 second'
    >>> human_readable_time(3722)
    '1 hour, 2 minutes, 2 seconds'
    >>> human_readable_time(7199)
    '1 hour, 59 minutes, 59 seconds'
    >>> human_readable_time(7200)
    '2 hours'
    >>> human_readable_time(7201)
    '2 hours, 1 second'
    >>> human_readable_time(7202)
    '2 hours, 2 seconds'
    >>> human_readable_time(7259)
    '2 hours, 59 seconds'
    >>> human_readable_time(7260)
    '2 hours, 1 minute'
    >>> human_readable_time(7261)
    '2 hours, 1 minute, 1 second'
    >>> human_readable_time(7262)
    '2 hours, 1 minute, 2 seconds'
    >>> human_readable_time(7319)
    '2 hours, 1 minute, 59 seconds'
    >>> human_readable_time(7320)
    '2 hours, 2 minutes'
    >>> human_readable_time(7321)
    '2 hours, 2 minutes, 1 second'
    >>> human_readable_time(7322)
    '2 hours, 2 minutes, 2 seconds'
    >>> human_readable_time(60*60*24 - 1)
    '23 hours, 59 minutes, 59 seconds'
    >>> human_readable_time(60*60*24)
    '1 day'
    >>> human_readable_time(60*60*24 + 1)
    '1 day'
    >>> human_readable_time(60*60*24 + 1, precision=4)
    '1 day, 1 second'
    >>> human_readable_time(60*60*24 + 60)
    '1 day, 1 minute'
    >>> human_readable_time(60*60*24*2 - 1)
    '1 day, 23 hours, 59 minutes'
    >>> human_readable_time(60*60*24*2 - 1, precision=4)
    '1 day, 23 hours, 59 minutes, 59 seconds'
    >>> human_readable_time(60*60*24*2)
    '2 days'
    >>> human_readable_time(60*60*24*7 - 1)
    '6 days, 23 hours, 59 minutes'
    >>> human_readable_time(60*60*24*7 - 1, precision=4)
    '6 days, 23 hours, 59 minutes, 59 seconds'
    >>> human_readable_time(60*60*24*7)
    '1 week'
    >>> human_readable_time(60*60*24*7*2 - 1)
    '1 week, 6 days, 23 hours'
    >>> human_readable_time(60*60*24*7*2 - 1, precision=4)
    '1 week, 6 days, 23 hours, 59 minutes'
    >>> human_readable_time(60*60*24*7*2 - 1, precision=5)
    '1 week, 6 days, 23 hours, 59 minutes, 59 seconds'
    >>> human_readable_time(60*60*24*7*2)
    '2 weeks'
    >>> human_readable_time(60*60*24*7*2 + 1)
    '2 weeks'
    >>> human_readable_time(60*60*24*7*2 + 1, precision=4)
    '2 weeks'
    >>> human_readable_time(60*60*24*7*2 + 1, precision=5)
    '2 weeks, 1 second'
    '''
    # Inspiration: http://stackoverflow.com/q/6574329
    units = [
        (60, 'seconds'),
        (60, 'minutes'),
        (24, 'hours'),
        (7, 'days'),
        (None, 'weeks'),
    ]
    output = []
    quo, rem = seconds, 0
    for divisor, unit in units:
        if divisor is not None:
            quo, rem = divmod(quo, divisor)
        else:
            rem = quo
        output.append((rem, unit))
        if quo == 0:
            break

    output = reversed(output[-precision:])
    return ', '.join(
        '{0} {1}'.format(
            value, unit if value > 1 else unit[:-1]
        ) for value, unit in output
        if value > 0
    )


def human_readable_status(status_dict):
    adsl_status = status_dict['adsl_status']
    ADSLMode = status_dict['ADSLMode']
    ADSLMode_ext = status_dict['ADSLMode_ext']

    # Messages for adsl_status[0].
    ADSLStatusCurrent_Msg=['Reset', 'Ready', 'Fail', 'Idle', 'Quiet', 'GHS',
        'Full Initialization', 'Show Time', 'Re-Train', 'Diagnostic Mode',
        'Short Initialization']

    lines = []

    if adsl_status[0] == 7:
        lines.append('Line Status                   : ✓ Connected')
    else:
        lines.append('Line Status                   : ✗ Disconnected ({0})'.format(
            ADSLStatusCurrent_Msg.get(adsl_status[0], 'Unknown')))

    # TODO: Improve the layout. And also this code.
    lines.extend([
        'ADSL mode                     : {0}'.format(
            ADSLMode.get(adsl_status[12], 'Unknown')
            if adsl_status[12] > 0 else
            ADSLMode_ext.get(adsl_status[13], 'Unknown')
        ),
        'Uptime                        : {0}'.format(
            human_readable_time(adsl_status[14])),
        'Data Transferred              : ↑ {1} / ↓ {0}'.format(
            *[human_readable_binary_prefix(x) for x in adsl_status[15:17]]),
        'Bandwidth                     : ↑ {0} kbps / ↓ {1} kbps'.format(*adsl_status[2:4]),
        'Output Power                  : ↑ {0} dBm / ↓ {1} dBm'.format(*adsl_status[17:19]),
        'Line Attenuation              : ↑ {0} dB / ↓ {1} dB'.format(*adsl_status[6:8]),
        'Signal to Noise Margin        : ↑ {0} dB / ↓ {1} dB'.format(*adsl_status[4:6]),
        'CRC Errors                    : ↑ {0} / ↓ {1}'.format(*adsl_status[8:10]),
        'HEC Errors                    : ↑ {0} / ↓ {1}'.format(*adsl_status[10:12]),
        'FEC Errors                    : ↑ {0} / ↓ {1}'.format(*adsl_status[24:26]),
        'Error Seconds (Local / Remote): {0} / {1}'.format(*adsl_status[22:24]),
        'Loss of Link (Remote)         : {0}'.format(adsl_status[21]),
        'CELL Count (Local / Remote)   : {0} / {1}'.format(
            *[human_readable_decimal_prefix(x, '') for x in adsl_status[26:28]]),
        'Vendor ID (Local / Remote)    : {0} / {1}'.format(*adsl_status[19:21]),
    ])

    return '\n'.join(lines)


def main():
    # TODO: Add command-line arguments for hostname, username, password.
    # TODO: Add command-line argument to run the doctests.
    try:
        print(
            human_readable_status(
                parse_javascript_vars(
                    fetch_modem_status()
                )
            )
        )
    except requests.exceptions.HTTPError as e:
        print(e.response.url)
        print(e)

def run_doctests():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    main()
