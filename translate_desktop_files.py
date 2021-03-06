#!/usr/bin/env python3

# This script accepts a directory of desktop.in files, and outputs desktop files
# with localized strings for every localestring key/value pair. Requires polib

import os
import argparse
import polib
import re

PO_DIR = 'po'
LINGUAS_FILE = os.path.join(PO_DIR, 'LINGUAS')
KEY_TO_CONTEXT_APPS = {
    'Name': 'title',
    'Comment': 'subtitle'
}
KEY_TO_CONTEXT_LINKS = {
}
KEY_TO_CONTEXT_FOLDERS = {
    'Name': 'folderName'
}

def is_localized_entry(line):
    # if the line starts with an underscore, it's to be localized
    return line[0] == '_'

def translate(po_dict, string, lang, ctx):
    translation = po_dict[lang][(string, ctx)]

    # if a translation is empty, that's just as bad as not having it!
    if translation == '':
        raise KeyError
    return translation

def all_entries(po_dict, string, lang):
    # Return all entries in lang's po file, regardless of context
    return [msg for idx, msg in po_dict[lang].items() if idx[0] == string]

def build_strings_dict(langs):
    strings_dict = {}
    # Index translations first by language, then by (msgid, msgctxt) tuples
    # This way, "Photo Editor" the title can be distinguished from "Photo Editor" the subtitle
    for lang in langs:
        po = polib.pofile(os.path.join(PO_DIR, lang + '.po'))
        strings_dict[lang] = {(entry.msgid, entry.msgctxt): entry.msgstr for entry in po}

    return strings_dict

def translate_dir(in_dir):
    with open(LINGUAS_FILE) as linguas:
        langs = linguas.read().splitlines()

    strings_dict = build_strings_dict(langs)

    # Iterate through only desktop.in and directory.in files,
    # and output them verbatim unless a key is prefixed with an underscore.
    # In that case, see if we have a translation (based on the correct word
    # context), and if so, output that key with a localized string.
    desktop_in_files = [filename for filename in os.listdir(in_dir)
                        if 'desktop.in' in filename
                        or 'directory.in' in filename]

    locale_regex = re.compile('^com\.endlessm\..+\.[a-z]{2,3}_?[A-Z]{0,2}.desktop$')
    
    for desktop_in_file in desktop_in_files:

        # don't translate already-localized content
        if locale_regex.match(desktop_in_file):
            continue

        in_path = os.path.join(in_dir, desktop_in_file)
        in_file = open(in_path, 'r')
        in_file_lines = in_file.read().splitlines()

        # trim off the '.in' suffix
        out_filename = desktop_in_file[:-3]
        out_path = os.path.join(in_dir, out_filename)
        out_file = open(out_path, 'w')

        for line in in_file_lines:
            if is_localized_entry(line):
                # remove the underscore and split the line into its components
                stripped_line = line[1:]
                [key, localestring] = stripped_line.split('=')

                # first print the default string
                out_file.write(stripped_line + '\n')

                for lang in langs:
                    try:
                        if 'directory.in' in desktop_in_file:
                            msgctxt = KEY_TO_CONTEXT_FOLDERS[key]
                        elif desktop_in_file.startswith('eos-link-'):
                            msgctxt = KEY_TO_CONTEXT_LINKS[key]
                        else:
                            msgctxt = KEY_TO_CONTEXT_APPS[key]
                        translation = translate(strings_dict, localestring, lang, msgctxt)
                        localized_line = "%s[%s]=%s" % (key, lang, translation)
                        out_file.write(localized_line + '\n')
                    except KeyError:
                        pass
            else:
                out_file.write(line + '\n')

        # finally, remove this .in file
        in_file.close()
        os.remove(in_path)
