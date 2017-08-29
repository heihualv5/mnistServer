import os
import time
import tensorflow as tf
import numpy as np
import urllib2 as ub
from flask import Flask, request
from PIL import Image
from io import BytesIO
from cassandra.cluster import Cluster


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getcwd()

sess = tf.Session()
saver = tf.train.import_meta_graph("./tmp/model.ckpt.meta")
saver.restore(sess,tf.train.latest_checkpoint('./tmp'))

cluster = Cluster(["10.10.10.100"])
session = cluster.connect()
keyspacename='mnist'
session.execute("create keyspace if not exists mnist with replication = {'class': 'SimpleStrategy', 'replication_factor': 1};")
session.set_keyspace('mnist')
session.execute("create table if not exists picdatabase(timestamp double, filedata blob ,answer int ,primary key(timestamp));")

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        data = request.files['file']
        if data :
            file=data.read()
            im = Image.open(BytesIO(file))
            imout=im.convert('L')
            xsize, ysize=im.size
            if xsize != 28 or ysize!=28:
                imout=imout.resize((28,28),Image.ANTIALIAS)
            arr = []
            for i in range(28):
                for j in range(28):
                    pixel = float(1.0 - float(imout.getpixel((j, i)))/255.0)
                    arr.append(pixel)
            keep_prob=tf.get_default_graph().get_tensor_by_name('dropout/Placeholder:0')
            x=tf.get_default_graph().get_tensor_by_name('x:0')
            y=tf.get_default_graph().get_tensor_by_name('fc2/add:0')
            arr1 = np.array(arr).reshape((1,28*28))
            pre_vec=sess.run(y,feed_dict={x:arr1,keep_prob:1.0})
            pre=str(np.argmax(pre_vec[0],0))+'\n'
            times=time.time()
            params=[times,bytearray(file),int(pre)]
            session.execute("INSERT INTO picdatabase (timestamp,filedata,answer) VALUES (%s, %s, %s)",params)
            result=session.execute("SELECT * FROM picdatabase")
            for x in result:
                print (x.timestamp, x.filedata,x.answer)
            return pre
    if request.method=='GET':
        utf8url=request.args.get('url')
        url = utf8url.encode("utf-8")
        data=ub.urlopen(url)
        file=data.read()
        im = Image.open(BytesIO(file))
        imout=im.convert('L')
        xsize, ysize=im.size
        if xsize != 28 or ysize!=28:
            imout=imout.resize((28,28),Image.ANTIALIAS)
        arr = []
        for i in range(28):
            for j in range(28):
                pixel = float(1.0 - float(imout.getpixel((j, i)))/255.0)
                arr.append(pixel)
        keep_prob=tf.get_default_graph().get_tensor_by_name('dropout/Placeholder:0')
        x=tf.get_default_graph().get_tensor_by_name('x:0')
        y=tf.get_default_graph().get_tensor_by_name('fc2/add:0')
        arr1 = np.array(arr).reshape((1,28*28))
        pre_vec=sess.run(y,feed_dict={x:arr1,keep_prob:1.0})
        pre=str(np.argmax(pre_vec[0],0))+'\n'
        times=time.time()
        params=[times,bytearray(file),int(pre)]
        session.execute("INSERT INTO picdatabase (timestamp,filedata,answer) VALUES (%s, %s,%s)",params)
        result=session.execute("SELECT * FROM picdatabase")
        for x in result:
            print (x.timestamp,x.filedata,x.answer)
        return pre
    return '-1'



if __name__ == '__main__':
    app.run()