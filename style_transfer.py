# Copyright 2019 The crowdcompute:style-transfer-app Authors
# This file is part of the crowdcompute:style-transfer-app library.
#
# The crowdcompute:style-transfer-app library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The crowdcompute:style-transfer-app library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with the crowdcompute:style-transfer-app library. If not, see <http://www.gnu.org/licenses/>.

import os
import imagehash
import hashlib
import zipfile
import numpy as np
from PIL import Image
from werkzeug.utils import secure_filename
from os.path import isfile, join, splitext, isdir, exists
from flask import Flask, abort, request, jsonify, send_from_directory, send_file

APP_ROOT = "/style-transfer-app"
ZIP_PATH = join(APP_ROOT, "results.zip")

MODELS_PATH = join(APP_ROOT, "checkpoint")
UPLOADS_PATH = join(APP_ROOT, "images")
if not isdir(UPLOADS_PATH):
    os.mkdir(UPLOADS_PATH)
RESULTS_DIR = join(APP_ROOT, "results")
if not isdir(RESULTS_DIR):
    os.mkdir(RESULTS_DIR)
MAX_WIDTH = 1500
MAX_HEIGHT = 1500
BUF_SIZE = 65536

api = Flask(__name__)

# API call to download images
@api.route('/download/<path:filename>')
def download_file(filename):
    """Download a file."""
    return send_from_directory(RESULTS_DIR, filename, as_attachment=True)

# API call to run style transfer 
# Rerurns a links to image results
@api.route('/style_transfer', methods=['GET', 'POST'])
def upload():
    json_urls = {}
    image_names = []
    if request.method == 'POST':
        styles = request.form.get('styles')
        print("Styles selected: ")
        print(styles)

        for style in styles.split(','):
            if not style_exists(style):
                error_msg =  'Style "{}" is not supported... Available styles are: {}'.format(style, get_avail_styles())
                print(error_msg)
                return error_msg

            for image_bytes in request.files.getlist('images'):
                if not file_check(image_bytes):
                    error_msg =  'Uploaded file "{}" is not supported...'.format(image_bytes.filename)
                    print(error_msg)
                    return error_msg
                image = Image.open(image_bytes)
                # Resize image. Style transfer can't handle huge images 
                image.thumbnail([MAX_WIDTH, MAX_HEIGHT], Image.ANTIALIAS)
                print('Image resized...')

                # Save the uploaded image locally & get its hash
                in_img_path = join(UPLOADS_PATH, image_bytes.filename)
                image.save(in_img_path)
                # hash image
                # hash = imagehash.average_hash(image)
                # hashed_img_name = style + str(hash) + get_ext(image_bytes.filename)
                hashed_img_name = get_hashed_filename(in_img_path, get_ext(image_bytes.filename), style)

                # Processing
                style_transfer(style, in_img_path, hashed_img_name)
                image_names.append(hashed_img_name)
                json_urls[style+'_'+image_bytes.filename] = get_img_url(hashed_img_name)

    hashed_zip_name = zip_images(image_names)
    json_urls[hashed_zip_name] = get_img_url(hashed_zip_name)
    return jsonify(json_urls)

def get_avail_styles():
    return [f.split('.')[0] for f in os.listdir(MODELS_PATH) if isfile(join(MODELS_PATH, f))]

def get_img_url(img_name):
    return '{0}download/{1}'.format(request.url_root, img_name)

# Returns extension with the dot (.)
def get_ext(filename):
    return splitext(filename)[1][0:].strip().lower()

def style_exists(style):
    style_filepath = join(MODELS_PATH, style + '.ckpt')
    return exists(style_filepath)

def get_hashed_filename(file, ext, name_extra=''):
    md5 = hashlib.md5()
    with open(file, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)

    hash = md5.hexdigest()
    return name_extra + '_' + str(hash) + ext

def zip_images(image_names):
    zip_full_path = join(RESULTS_DIR, 'zip_name.zip')
    zipf = zipfile.ZipFile(zip_full_path,'w', zipfile.ZIP_DEFLATED)

    for img_name in image_names:
        filepath = join(RESULTS_DIR, img_name)
        zipf.write(filepath)

    zipf.close()
    hashed_zip_name = get_hashed_filename(zip_full_path, '.zip', 'results')
    zip_hashed_full_path = join(RESULTS_DIR, hashed_zip_name)
    os.rename(zip_full_path, zip_hashed_full_path)
    return hashed_zip_name

def file_check(img):
    filename = img.filename
    # Secure a filename before storing it
    filename = secure_filename(filename)
    # Verify file is supported
    ext = splitext(filename)[1][1:].strip().lower()
    if ext in set(['jpg', 'jpeg', 'png']):
        print('File supported moving on...')
        return True
    else:
        return False

# Style transfer
def style_transfer(style, in_img_path, hashed_img_name):
    try:
        out_path = join(RESULTS_DIR, hashed_img_name)
        os.system('python evaluate.py --checkpoint checkpoint/{} --in-path {} --out-path {}'.format(style + '.ckpt', in_img_path, out_path))
    except:
        print('An error running the command occured.')
    return None

if __name__ == "__main__":
    api.run(host="0.0.0.0", port=3000)