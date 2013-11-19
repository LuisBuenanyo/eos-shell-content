#!/usr/bin/python

# This script requires installing ImageMagick
# (sudo apt-get install imagemagick)
# for the 'convert' command

# To use this script, first log into eoscms.parafernalia.net.br
# Under "App Store", click on "Generate Package"
# There should be no warnings
# Click on "Click here to download files in zip format"
# Save the downloaded file in this folder as appstore.zip
# Run this script
# Add and commit any changes to git
# Proceed with the normal build process

import os
import shutil
import sys
import zipfile

ZIP_FILENAME = 'appstore.zip'
UNZIP_DIR = 'unzipped'
CONTENT_DIR = 'content/Default'
IGNORE_ERRORS = True
JPEG_QUALITY = 90

# Run the ImageMagick 'convert' application from the command line,
# with specified JPEG quality and all metadata stripped
def convert(source, target, command):
    os.system('convert ' + source + ' ' + command +
              ' -quality ' + str(JPEG_QUALITY) + ' -strip ' + target)

# Remove the existing unzipped and content directories, if they exist
shutil.rmtree(UNZIP_DIR, IGNORE_ERRORS)
shutil.rmtree(CONTENT_DIR, IGNORE_ERRORS)

# Note: the unzipped directory does not currently match
# the requirements of the app store, so we first unzip
# into a staging area, and then copy individual files/folders
# to the app store content directory

# Unzip the file
zfile = zipfile.ZipFile(ZIP_FILENAME)
zfile.extractall(UNZIP_DIR)

# For now, we need to convert specific locales to general languages
# (with 'C' as the fallback for English) and personalities,
# until the CMS is reworked
locales = ['en-us', 'es-gt', 'pt-br']
languages = ['C', 'es', 'pt']
personalities = ['default', 'Guatemala', 'Brazil']

# Copy the app json to the content folder
# with tweaks to the json content
source = os.path.join(UNZIP_DIR, 'apps', 'content.json')
target_dir = os.path.join(CONTENT_DIR, 'apps')
target = os.path.join(target_dir, 'content.json')
os.makedirs(target_dir)
infile = open(source, 'r')
outfile = open(target, 'w')
for line in infile:
    for i in range(0, len(locales)):
        from_string = '"' + locales[i] + '"'
        to_string = '"' + languages[i] + '"'
        line = line.replace(from_string, to_string)
    outfile.write(line)
infile.close()
outfile.close()

# Copy the thumbnail images to the content folder
# with tweaked compression
source_dir = os.path.join(UNZIP_DIR, 'apps', 'thumbs')
target_dir = os.path.join(CONTENT_DIR, 'apps', 'resources', 'thumbnails')
os.makedirs(target_dir)
for source in os.listdir(source_dir):
    target = source
    source_file = os.path.join(source_dir, source)
    target_file = os.path.join(target_dir, target)
    convert(source_file, target_file, '')

# Copy the featured images to the content folder
# with tweaked compression
# (Note: if the featured image is square, we just use the thumbnail)
source_dir = os.path.join(UNZIP_DIR, 'apps', 'featured')
target_dir = os.path.join(CONTENT_DIR, 'apps', 'resources', 'images')
os.makedirs(target_dir)
for source in os.listdir(source_dir):
    target = source
    source_file = os.path.join(source_dir, source)
    target_file = os.path.join(target_dir, target)
    convert(source_file, target_file, '')

# Copy the screenshot images to the content folder
# resized to a width of 480 pixels
# (Note: if the featured image is square, we just use the thumbnail)
for i in range(0, len(locales)):
    # For now, we need to replace the CMS locale with generic language
    # in the folder names
    source_dir = os.path.join(UNZIP_DIR, 'apps', 'screenshots', locales[i])
    target_dir = os.path.join(CONTENT_DIR, 'apps', 'resources', 'screenshots',
                              languages[i])
    os.makedirs(target_dir)
    for source in os.listdir(source_dir):
        target = source
        source_file = os.path.join(source_dir, source)
        target_file = os.path.join(target_dir, target)
        # Resize to a width of 480, allowing an arbitrary height
        convert(source_file, target_file,
                '-resize 480x480')

# Copy the splash screen images to the content folder
# with tweaked compression
source_dir = os.path.join(UNZIP_DIR, 'apps', 'splash')
target_dir = os.path.join(CONTENT_DIR, 'apps', 'resources', 'splash')
os.makedirs(target_dir)
for source in os.listdir(source_dir):
    target = source
    source_file = os.path.join(source_dir, source)
    target_file = os.path.join(target_dir, target)
    convert(source_file, target_file, '')

# Copy and rename the links json to the content folder
# We currently support only one version of the content,
# so we use the es-gt and ignore en-us and pt-br
source_dir = os.path.join(UNZIP_DIR, 'links')
target_dir = os.path.join(CONTENT_DIR, 'links')
os.makedirs(target_dir)
for i in range(0, len(locales)):
    # For now, we need to replace the CMS locale with personality
    # in the file names
    # Note: eventually, we will replace this with a single JSON
    # file that has all the links with a personality field for each link,
    # but for now let's minimize the changes to the CMS content files
    source = os.path.join(source_dir, locales[i] + '.json')
    target = os.path.join(target_dir, personalities[i] + '.json')
    shutil.copy(source, target)

# Copy the link images to the content folder
# resized/cropped to 90x90
source_dir = os.path.join(UNZIP_DIR, 'links', 'images')
target_dir = os.path.join(CONTENT_DIR, 'links', 'images')
os.makedirs(target_dir)
for source in os.listdir(source_dir):
    target = source
    source_file = os.path.join(source_dir, source)
    target_file = os.path.join(target_dir, target)
    # In case the image is rectangular,
    # first resize so that the smallest dimension is 90 pixels,
    # then crop from the center to exactly 90x90
    convert(source_file, target_file,
            '-resize 90x90^ -gravity center -crop 90x90+0+0')

# Note: we are not yet handling the app and link icons

# Note: we currently ignore the folder icons in the icons folder
# They are .png files, where we currently need .svg files
