from flask import Flask, request, send_file
from datetime import datetime
from core import Steganography
import os
import shutil

CONTAINER = 'CONTAINER'
DATA = 'DATA'
MESSAGE = 'MESSAGE'
IMAGE = 'IMAGE'

def init_dirs():
    containers_dir = os.path.join(os.getcwd(), 'containers/')
    data_dir = os.path.join(os.getcwd(), 'data/')
    encoded_dir = os.path.join(os.getcwd(), 'encoded/')
    decoded_dir = os.path.join(os.getcwd(), 'decoded/')
    dirs = [containers_dir, data_dir, encoded_dir, decoded_dir]
    for dir in dirs:
        shutil.rmtree(dir)
        os.mkdir(dir)
    return dirs


def save(type_of_data, content, filename, path):
    """
    Using for storage image or text
    :param type_of_data: IMAGE or MESSAGE - text.
    :param content: data. if IMAGE must be FILE_STORAGE class
    :param filename: name of file
    :return: None
    """
    if type_of_data == MESSAGE:
        f = open(os.path.join(path, filename), "w")
        f.write(content)
        f.close()
    elif type_of_data == IMAGE:
        try:
            content.save(os.path.join(path, filename))
        except:
            raise Exception("SAVE FAULT!")



app = Flask(__name__)


@app.route('/', methods=['GET'])
def html():
    f = open(os.path.join(os.getcwd(), 'web/index.html'))
    data = f.read()
    return data


@app.route('/home', methods=['POST', 'GET'])
def index():
    t = {"message": "WELCOME TO Steggy !"}
    return t, 200


@app.route('/<string:file_name>', methods=['GET'])
def ele(file_name):
    return send_file(os.path.join(os.getcwd(), f"web/{file_name}"), as_attachment=True), 200


@app.route('/encode', methods=['post'])
def do_encode_stuff():
    if request.files:
        option_type = request.form.get('type')
        # Save container image
        ts = str(int(datetime.timestamp(datetime.now())))
        container = request.files["container"]
        save(IMAGE, container, f"{ts}.png", containers_dir)
        container_path = os.path.join(containers_dir, f"{ts}.png")

        # save data, it depends on it's type (IMAGE or MESSAGE)
        data = None
        if option_type == IMAGE:
            data = request.files["data"]
            save(IMAGE, data, f"{ts}.png", data_dir)
        elif option_type == MESSAGE:
            data = request.form.get("data")
            save(MESSAGE, data, '{}.txt'.format(ts), data_dir)
        try:
            steg = Steganography(container_path)
            encoded = steg.encode(data, option_type)
            Steganography.save(encoded, IMAGE, os.path.join(encoded_dir, ts))
            return send_file(os.path.join(encoded_dir, '{}.png'.format(ts)), as_attachment=True), 200
        except Exception:
            return {"error": "Request format wrong or data is too big"}, 401

    return {"error": "Internal Server Error"}, 500


@app.route('/decode', methods=['POST'])
def do_decode_stuff():
    if request.files:
        option_type = request.form.get('type')
        # Save container image
        ts = str(int(datetime.timestamp(datetime.now())))
        container = request.files["container"]
        save(IMAGE, container, f"{ts}.png", containers_dir)
        container_path = os.path.join(containers_dir, f"{ts}.png")
        try:
            steg = Steganography(container_path)
            data = steg.decode(option_type)
            if option_type == IMAGE:
                Steganography.save(data, IMAGE, os.path.join(data_dir, ts))
                return send_file(os.path.join(data_dir, '{}.png'.format(ts)), as_attachment=True)
            elif option_type == MESSAGE:
                save(MESSAGE, data, '{}.txt'.format(ts), data_dir)
                return send_file(os.path.join(data_dir, '{}.txt'.format(ts)), as_attachment=True)
        except Exception as e:
            return {"error": f"Internal Server Error,{e}"}, 500

    return {"error": "Internal Server Error"}, 500


if __name__ == '__main__':
    containers_dir, data_dir, encoded_dir, decoded_dir = init_dirs()
    app.run(debug=True)
