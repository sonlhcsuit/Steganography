from flask import Flask,request,jsonify,send_file,render_template
from datetime import datetime
from core import Steganography
import os
CONTAINER = 'CONTAINER'
DATA = 'DATA'
MESSAGE = 'MESSAGE'
IMAGE = 'IMAGE'
def init_dirs():
    containers_dir = os.path.join( os.getcwd() ,'containers')
    data_dir = os.path.join(os.getcwd(),'data')
    encoded_dir = os.path.join(os.getcwd(),'encoded')
    decoded_dir = os.path.join(os.getcwd(),'decoded')
    dirs = [containers_dir,data_dir,encoded_dir,decoded_dir]
    for dir in dirs:
        if not os.path.isdir(dir):
            os.mkdir(dir)
    return dirs

def save(type,content,filename,path):
    """
    Using for storage image or text
    :param type: IMAGE or MESSAGE - text.
    :param content: data. if IMAGE must be FILESTORAGE class
    :param filename: name of file
    :return:
    """
    if type == MESSAGE:
        f =  open(os.path.join(path,filename),"w")
        f.write(content)
        f.close()
    elif type == IMAGE:
        try:
            content.save(os.path.join(path,filename))
        except:
            raise Exception("SAVE FAULT!")

containers_dir,data_dir,encoded_dir,decoded_dir = init_dirs()

app = Flask(__name__)
@app.route('/',methods=['GET'])
def html():
    f = open('web/index.html')
    data = f.read()
    return data
@app.route('/home',methods=['POST','GET'])
def index():
    t = {"message":"WELCOME TO Steggy !"}
    print(t)
    return t,200
@app.route('/electronics.png')
def ele():
    return send_file(os.path.join(os.getcwd(), 'electronics.png'), as_attachment=True), 200
@app.route('/encode',methods=['post'])
def do_encode_stuff():
    if request.files:

        type = request.form.get('type')

        ts = str(int(datetime.timestamp(datetime.now())))
        container_path = None
        data_path = None
        # For Saving Data
        container = request.files["container"]
        temp = container.filename.split(".")
        extension = temp[len(temp)-1]
        save(IMAGE,container,'{}.{}'.format(ts,extension),containers_dir)
        container_path = os.path.join(containers_dir,'{}.{}'.format(ts,extension))
        print("Save container success!")
        print(container_path)

        data = None
        if type == IMAGE:
            data = request.files["data"]
            temp = data.filename.split(".")
            extension = temp[len(temp) - 1]
            save(IMAGE, data, '{}.{}'.format(ts, extension), data_dir)
            data_path = os.path.join(data_dir,'{}.{}'.format(ts, extension))
            print("Save image data success!")
            print(data_path)
        elif type == MESSAGE:
            data = request.form.get("data")
            save(MESSAGE,data,'{}.txt'.format(ts),data_dir)
            data_path = os.path.join(data_dir,'{}.txt'.format(ts))
            f = open(data_path,"r")
            data_path = ''.join(f.readlines())
            f.close()
            print("Save text data success!")
            print(data_path)

        try:
            steg = Steganography(container_path)
            encoded = steg.encode(data_path,type)
            Steganography.save(encoded,IMAGE,os.path.join(encoded_dir,ts))
            return send_file(os.path.join(encoded_dir,'{}.png'.format(ts)), as_attachment=True),200
        except Exception:
            return {"error": "Request format wrong or data is too big"},401


    return {"error":"Internal Server Error"},500

@app.route('/decode',methods=['post'])
def do_decode_stuff():
    if request.files:

        type = request.form.get('type')

        ts = str(int(datetime.timestamp(datetime.now())))
        # For Saving Data
        container = request.files["container"]
        temp = container.filename.split(".")
        extension = temp[len(temp)-1]
        save(IMAGE,container,'{}.{}'.format(ts,extension),decoded_dir)
        container_path = os.path.join(decoded_dir,'{}.{}'.format(ts,extension))
        print("Save container success!")
        print(container_path)
        try:
            steg = Steganography(container_path)
            data = steg.decode(type)
            if type == IMAGE:
                Steganography.save(data,IMAGE,os.path.join(data_dir,ts))
                return send_file(os.path.join(data_dir,'{}.png'.format(ts)), as_attachment=True)
            elif type == MESSAGE:
                save(MESSAGE,data,'{}.txt'.format(ts),data_dir)
                return send_file(os.path.join(data_dir,'{}.txt'.format(ts)), as_attachment=True)
        except Exception:
            return {"error":"Internal Server Error"},500

    return {"error":"Internal Server Error"},500

if __name__ == '__main__':
    app.run(debug=True)