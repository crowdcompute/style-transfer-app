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

api = Flask(__name__)

# API call given the images needed, outputs the result image
# Rerurns a link to image result
@api.route('/style_transfer', methods=['GET', 'POST'])
def upload():
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
                hashed_img_name = hash_filename(image, image_bytes.filename, style)

                # Processing
                style_transfer(style, in_img_path, hashed_img_name)
                image_names.append(hashed_img_name)

    zip_images(image_names)
    print(ZIP_PATH)
    return send_file(ZIP_PATH, mimetype='application/x-rar-compressed')


def get_avail_styles():
    return [f.split('.')[0] for f in os.listdir(MODELS_PATH) if isfile(join(MODELS_PATH, f))]


def style_exists(style):
    style_filepath = join(MODELS_PATH, style + '.ckpt')
    return exists(style_filepath)


def hash_filename(img, filename, style):
    hash = imagehash.average_hash(img)
    ext = splitext(filename)[1][0:].strip().lower()
    hashed_filename = str(hash) + '_' + style + ext
    return hashed_filename


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


def zip_images(image_names):
    zipf = zipfile.ZipFile(ZIP_PATH,'w', zipfile.ZIP_DEFLATED)

    for img_name in image_names:
        filepath = join(RESULTS_DIR, img_name)
        zipf.write(filepath)
    zipf.close()


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