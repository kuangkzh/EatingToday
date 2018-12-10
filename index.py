import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import time

import DBHelper


UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<name>/history')
def user_history(name):
    user_id = '1'
    history = DBHelper.get_history(user_id)
    history_list = []
    for record in history:
        food_name = record[0]
        t = record[1]
        time_array = time.localtime(t)
        time_format = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        record_dict = dict(food_name=food_name, time_format=time_format)
        history_list.append(record_dict)
    print(history_list)
    context = {'history': history_list}
    return render_template('history.html', name=name, **context)


if __name__ == '__main__':
    app.run(debug=True)
