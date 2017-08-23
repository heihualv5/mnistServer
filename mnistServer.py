import os
import tensorflow as tf
from flask import Flask, request, url_for, send_from_directory,render_template
from werkzeug import secure_filename
from PIL import Image
import numpy as np

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getcwd()
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

sess = tf.Session()
saver = tf.train.import_meta_graph("./tmp/model.ckpt.meta")
saver.restore(sess,tf.train.latest_checkpoint('./tmp'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            im = Image.open(filename)
            imout=im.convert('L')
            xsize, ysize=im.size
            if xsize != 28 or ysize!=28:
                imout=imout.resize((28,28),Image.ANTIALIAS)
                imout.save("return.png","png")
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
            pre=str(np.argmax(pre_vec[0],0))
            return pre
    return '-1'


if __name__ == '__main__':
    app.run()