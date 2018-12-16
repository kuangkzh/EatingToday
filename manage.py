import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory,session
from werkzeug.utils import secure_filename
from datetime import timedelta
import time
import DBHelper


UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(24)  # 设置为24位的字符,每次运行服务器都是不同的，所以服务器启动一次上次的session就清除。
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # 设置session的保存时间。


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/login-test', methods=['GET', 'POST'])
def login_test():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username, password)
        user_id = DBHelper.user_verification(username, password)
        if user_id:
            print('user_id:', user_id)
            session.permanent = True  # 默认session的时间持续31天
            session['user_id'] = user_id
            return redirect(url_for('history_test', name=username))
        elif username != "" and password != "":
            message = "用户名或密码错误"
            return render_template('login-test.html', message=message)
    return render_template('login-test.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<name>/history')
def history(name):
    return render_template('01-history.html', name=name)


@app.route('/<name>/history/<food>')
def history_detail(name, food):
    return render_template('01-history-detail.html', name=name, food=food)


@app.route('/<name>/history/upload')
def history_upload(name):
    return render_template('01-history-upload.html', name=name)


@app.route('/<name>/suggestions')
def suggestions(name):
    return render_template('02-suggestions.html', name=name)


@app.route('/<name>/group')
def group(name):
    return render_template('03-group.html', name=name)


@app.route('/<name>/aboutme')
def aboutme(name):
    return render_template('04-aboutme.html', name=name)


@app.route('/<name>/aboutme/settings')
def aboutme_settings(name):
    return render_template('04-aboutme-settings.html', name=name)


@app.route('/<name>/history-test')
def history_test(name):
    user_id = '2'
    user_history = DBHelper.get_history(user_id)
    history_list = []
    for record in user_history:
        food_name = record[0]
        t = record[1]
        time_array = time.localtime(t)
        time_format = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        record_dict = dict(food_name=food_name, time_format=time_format)
        history_list.append(record_dict)
    print(history_list)
    context = {'history': history_list}
    return render_template('history-test.html', name=name, **context)


if __name__ == '__main__':
    app.run(debug=True)
