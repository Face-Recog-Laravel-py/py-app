from deepface import DeepFace
import os
from PIL import Image
from io import BytesIO
from flask import Flask, request, redirect, jsonify
from werkzeug.utils import secure_filename
import base64
from flask_cors import CORS
import numpy as np

IMAGES_FOLDER = 'images'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MAX_FILES = 6

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app, withCredentials=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/test', methods=['GET', 'POST'])
def upload_file2():
    data = ""
    if request.method == 'POST':
        print(request.form)
        data = ""
    else:
        with open('camera.html', 'r') as file:
            data = file.read()
    return data

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        base64_data = request.form['image']
        if base64_data.startswith('data:image'):
            img = Image.open(BytesIO(base64.b64decode(bytes(base64_data.split(',')[1], "utf-8"))))
            img.save('uploads/output_image.png', quality=100, subsampling=0)
        try:
            dfs = DeepFace.find(
                img_path="uploads/output_image.png",
                db_path="images/",
                model_name="Facenet512"
            )
            if dfs:
                result_path = str(dfs[0].identity[0])
                relative_path = os.path.relpath(result_path, IMAGES_FOLDER)
                folder_name = os.path.dirname(relative_path).split(os.path.sep)[-1]
                return jsonify({"status": "success", "name": folder_name})
            else:
                return jsonify({"status": "error", "message": "No matches found"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

if __name__ == "__main__":
    app.run(debug=True)
