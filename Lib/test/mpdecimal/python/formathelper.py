#
# Copyright (c) 2008-2010 Stefan Krah. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#


import os, sys, locale, random
import platform, subprocess
from randdec import *
from decimal import *


windows_lang_strings = [
  "chinese", "chinese-simplified", "chinese-traditional", "czech", "danish",
  "dutch", "belgian", "english", "australian", "canadian", "english-nz",
  "english-uk", "english-us", "finnish", "french", "french-belgian",
  "french-canadian", "french-swiss", "german", "german-austrian",
  "german-swiss", "greek", "hungarian", "icelandic", "italian", "italian-swiss",
  "japanese", "korean", "norwegian", "norwegian-bokmal", "norwegian-nynorsk",
  "polish", "portuguese", "portuguese-brazil", "russian", "slovak", "spanish",
  "spanish-mexican", "spanish-modern", "swedish", "turkish",
]

preferred_encoding = {
  'cs_CZ': 'ISO8859-2',
  'cs_CZ.iso88592': 'ISO8859-2',
  'czech': 'ISO8859-2',
  'eesti': 'ISO8859-1',
  'estonian': 'ISO8859-1',
  'et_EE': 'ISO8859-15',
  'et_EE.ISO-8859-15': 'ISO8859-15',
  'et_EE.iso885915': 'ISO8859-15',
  'et_EE.iso88591': 'ISO8859-1',
  'fi_FI.iso88591': 'ISO8859-1',
  'fi_FI': 'ISO8859-15',
  'fi_FI@euro': 'ISO8859-15',
  'fi_FI.iso885915@euro': 'ISO8859-15',
  'finnish': 'ISO8859-1',
  'lv_LV': 'ISO8859-13',
  'lv_LV.iso885913': 'ISO8859-13',
  'nb_NO': 'ISO8859-1',
  'nb_NO.iso88591': 'ISO8859-1',
  'bokmal': 'ISO8859-1',
  'nn_NO': 'ISO8859-1',
  'nn_NO.iso88591': 'ISO8859-1',
  'no_NO': 'ISO8859-1',
  'norwegian': 'ISO8859-1',
  'nynorsk': 'ISO8859-1',
  'ru_RU': 'ISO8859-5',
  'ru_RU.iso88595': 'ISO8859-5',
  'russian': 'ISO8859-5',
  'ru_RU.KOI8-R': 'KOI8-R',
  'ru_RU.koi8r': 'KOI8-R',
  'ru_RU.CP1251': 'CP1251',
  'ru_RU.cp1251': 'CP1251',
  'sk_SK': 'ISO8859-2',
  'sk_SK.iso88592': 'ISO8859-2',
  'slovak': 'ISO8859-2',
  'sv_FI': 'ISO8859-1',
  'sv_FI.iso88591': 'ISO8859-1',
  'sv_FI@euro': 'ISO8859-15',
  'sv_FI.iso885915@euro': 'ISO8859-15',
  'uk_UA': 'KOI8-U',
  'uk_UA.koi8u': 'KOI8-U'
}

integers = [
  "",
  "1",
  "12",
  "123",
  "1234",
  "12345",
  "123456",
  "1234567",
  "12345678",
  "123456789",
  "1234567890",
  "12345678901",
  "123456789012",
  "1234567890123",
  "12345678901234",
  "123456789012345",
  "1234567890123456",
  "12345678901234567",
  "123456789012345678",
  "1234567890123456789",
  "12345678901234567890",
  "123456789012345678901",
  "1234567890123456789012",
]

numbers = [
  "0", "-0", "+0",
  "0.0", "-0.0", "+0.0",
  "0e0", "-0e0", "+0e0",
  ".0", "-.0",
  ".1", "-.1",
  "1.1", "-1.1",
  "1e1", "-1e1"
]

py_major = sys.version_info[0]

if platform.system() == 'Windows':
    locale_list = windows_lang_strings
else:
    try:
        # On Ubuntu, `locale -a` gives the wrong case for some locales,
        # so we get the correct names directly:
        f = open("/var/lib/locales/supported.d/local")
        locale_list = [loc.split()[0] for loc in f.readlines()]
    except:
        locale_list = subprocess.Popen(["locale", "-a"],
                          stdout=subprocess.PIPE).communicate()[0]
        if py_major == 3:
            locale_list = locale_list.decode()
        locale_list = locale_list.split('\n')


if py_major < 3:
    # issue7327 (min_width and multibyte separators): wont_fix
    save_loc = locale.setlocale(locale.LC_NUMERIC)
    for loc in locale_list[:]:
        try:
            locale.setlocale(locale.LC_NUMERIC, loc)
        except locale.Error:
            locale_list.remove(loc)
            continue
        d = locale.localeconv()
        if len(d['thousands_sep']) > 1 or len(d['decimal_point']) > 1:
            locale_list.remove(loc)
    locale.setlocale(locale.LC_NUMERIC, save_loc)

try:
    locale_list.remove('')
except ValueError:
    pass

# Debian
if os.path.isfile("/etc/locale.alias"):
    with open("/etc/locale.alias") as f:
        while 1:
            try:
                line = f.readline()
            except UnicodeDecodeError:
                continue
            if line == "":
                break
            if line.startswith('#'):
                continue
            x = line.split()
            if len(x) == 2:
                if x[0] in locale_list:
                    locale_list.remove(x[0])

if platform.system() == 'FreeBSD':
    # http://www.freebsd.org/cgi/query-pr.cgi?pr=142173
    # en_GB.US-ASCII has 163 as the currency symbol.
    for loc in ['it_CH.ISO8859-1', 'it_CH.ISO8859-15', 'it_CH.UTF-8', 'it_IT.ISO8859-1',
                'it_IT.ISO8859-15', 'it_IT.UTF-8', 'sl_SI.ISO8859-2', 'sl_SI.UTF-8',
                'en_GB.US-ASCII']:
        try:
            locale_list.remove(loc)
        except ValueError:
            pass


def get_preferred_encoding():
    loc = locale.setlocale(locale.LC_CTYPE)
    if loc in preferred_encoding:
        return preferred_encoding[loc]
    else:
        return locale.getpreferredencoding()

if py_major < 3:
    def printit(testno, s, fmt, encoding=None):
        if not encoding:
            encoding = get_preferred_encoding()
        try:
            result = format(Decimal(s), fmt)
            if isinstance(fmt, unicode):
                fmt = repr(fmt.encode(encoding))[1:-1]
            if isinstance(result, unicode):
                result = repr(result.encode(encoding))[1:-1]
            if "'" in result:
                sys.stdout.write("xfmt%d  format  %s  '%s'  ->  \"%s\"\n"
                                 % (testno, s, fmt, result))
            else:
                sys.stdout.write("xfmt%d  format  %s  '%s'  ->  '%s'\n"
                                 % (testno, s, fmt, result))
        except Exception as err:
            sys.stderr.write("%s  %s  %s\n" % (err, s, fmt))
else:
    def printit(testno, s, fmt, encoding=None):
        if not encoding:
            encoding = get_preferred_encoding()
        try:
            result = format(Decimal(s), fmt)
            fmt = str(fmt.encode(encoding))[2:-1]
            result = str(result.encode(encoding))[2:-1]
            if "'" in result:
                sys.stdout.write("xfmt%d  format  %s  '%s'  ->  \"%s\"\n"
                                 % (testno, s, fmt, result))
            else:
                sys.stdout.write("xfmt%d  format  %s  '%s'  ->  '%s'\n"
                                 % (testno, s, fmt, result))
        except Exception as err:
            sys.stderr.write("%s  %s  %s\n" % (err, s, fmt))
