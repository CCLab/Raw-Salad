# -*- coding: utf-8 -*-

import os
import csv
import sys
from string import Template



def make_translation_dict(translation_file_name, lang):
    field_nr = None
    translation_dict = {}

    try:
        file = open(translation_file_name, 'rb')
        reader = csv.reader(file, delimiter=';', quotechar='"')
    except Exception as e:
        exit('Problem with file: %s, %s' % (translation_file_name, e))

    for i, row in enumerate(reader):
        if i == 0:
            for j, row_lang in enumerate(row):
                if row_lang == lang:
                    field_nr = j
                    break
            if not field_nr:
                raise RuntimeError('Language %s not find in translation file' % lang)
        else:
            template_key = row[0]
            replacement = row[field_nr]
            translation_dict[template_key] = replacement
    
    return translation_dict


def translate_file(input_path, output_dir, translation_file_name, lang):
    try:
        file = open(input_path, 'rb')
    except IOError:
        exit('Error: unable to open file to translate. Exiting now.')
    
    content = file.read()
    file.close()

    translation = make_translation_dict(translation_file_name, lang)
    template = Template(content)
    translated_content = template.substitute(translation)

    input_file_name = os.path.basename(input_path)
    new_file_name = input_file_name.replace('_template', '')
    new_file_path = os.path.join(output_dir, new_file_name)
    
    try:
        new_file = open(new_file_path, 'wb')
        new_file.write(translated_content)
        new_file.close()
    except IOError:
        exit('Error: unable to save translated file. Exiting now.')



translation_file = 'translation.csv'
highest_level_dir = os.path.dirname(os.path.dirname(os.getcwd()))
templates_dir = os.path.join(highest_level_dir, 'src', 'rawsalad', 'databrowser', 'templates')

html_file_names = [
    '404_template.html',
    '500_template.html',
    'app_template.html',
    'old_browser_template.html'
]

lang = 'polish'
if len(sys.argv) == 2:
    if sys.argv[1] in ['english', 'polish', 'czech']:
        lang = sys.argv[1]
        print 'Using language: ', lang
    else:
        print 'Unexpected language: ', sys.argv[1]
        print 'Using', lang, 'instead'
else:
    print 'Using default language:', lang

for name in html_file_names:
    print 'Translating file', name, '...',
    full_path = os.path.join('templates', name)
    translate_file(full_path, templates_dir, translation_file, lang)
    print 'done'

print 'All files are done.'
