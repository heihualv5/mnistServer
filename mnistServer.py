import os
import urllib2 as ub
from flask import Flask, request
import database_Control
import model_load

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getcwd()

sess=model_load.model_ini()
session=database_Control.database_ini()

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        data = request.files['file']
        if data :
            file=data.read()
            pre=model_load.Number_recognition(file,sess)
            database_Control.database_insert(session,file,pre)
            return pre
    if request.method=='GET':
        utf8url=request.args.get('url')
        url = utf8url.encode("utf-8")
        data=ub.urlopen(url)
        file=data.read()
        pre=model_load.Number_recognition(file,sess)
        database_Control.database_insert(session,file,pre)
        return pre
    return '-1'




if __name__ == '__main__':
    app.run()