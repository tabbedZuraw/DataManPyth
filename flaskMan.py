import re
import json
from hashlib import sha256
from collections import Counter
from pymongo import MongoClient
from flask import Flask, request, redirect, render_template, flash
import socket
from werkzeug import secure_filename
import os

sha = ''
words2 = []
count = ''
app = Flask(__name__,  template_folder='templates')


ALLOWED_EXTENSIONS = set(['txt', ''])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    client = MongoClient('localhost:27017')
    db = client.dataCollection
    upload_folder = '/home/bartosz/PythPro/'   #Local directory
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(upload_folder, filename))
            file = open(filename, 'r')
            text = file.read().lower()
            global sha
            sha = sha256(text).hexdigest()
            dbData = None
            dbData = db.dataCollection.find( { 'SHA': sha } )
            if db.dataCollection.find( { 'SHA': sha } ).count() > 0:
                return render_template('seenB4.html')
            else:
                text = re.sub('[^a-z\ \']+',' ', text)
                words = list(text.split())
                words2 = [s for s in words if len(s) >= 2]
                global count
                count = Counter(words2)
                global words2
                words2 = list(set(words2))
                return render_template('temp.html')
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
@app.route('/basic')
def basic():
    foundD = {}
    notFoundD = {}
    
    with open('thesurus.json') as normsf:
                norms = json.load(normsf)

    for x in words2:
            temp = norms.get(x, [])
            if temp != []:
                foundD[x] = [count.get(x),temp[0], temp[1], temp[2]]
            else:notFoundD[x] = [count.get(x), 'NotFound']


    foundD = sorted(foundD.items(), key= lambda x: x[1][0], reverse=True)
    notFoundD = sorted(notFoundD.items(), key= lambda x: x[1][0], reverse=True)

    client = MongoClient('localhost:27017')
    db = client.dataCollection
    db.dataCollection.insert_one({
                'Found' : foundD,
                'NotFound' : notFoundD,
                'SHA' : sha,
                'Score' : '0'})


    return render_template('basic.html',
                            foundD = foundD,
                            notFoundD = notFoundD)


@app.route('/advancedSet')
def advancedSet():
    return render_template('entryF.html')

    
@app.route('/advanced' , methods=['POST'])
def advanced():
    aAn = {}
    notFoundD = {}
    userOpt = request.form['userOpt']

    with open('thesurus.json') as normsf:
                norms = json.load(normsf)


    for x in words2:
            temp = norms.get(x, [])
            if temp != []:
                aAn[x] = [int(list(temp[int(userOpt)].values())[0]) * count.get(x)]
            else:notFoundD[x] = [0]

            
    aAn = sorted(aAn.items(), key= lambda x: x[1][0], reverse=True)
    notFoundD = sorted(notFoundD.items(), key= lambda x: x[1][0], reverse=True)
    return render_template('advanced.html',
                            aAn = aAn)
if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    port = sock.getsockname()[1]
    sock.close()
    app.debug = True
    app.run(port=port)   
