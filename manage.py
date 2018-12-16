import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory,session
from werkzeug.utils import secure_filename
from datetime import timedelta
import time
import DBHelper


UPLOAD_FOLDER = 'static/img/food/'
ALLOWED_EXTENSIONS = set(['jpg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(24)  # 设置为24位的字符,每次运行服务器都是不同的，所以服务器启动一次上次的session就清除。
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # 设置session的保存时间。


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username, password)
        user_id = DBHelper.user_verification(username, password)
        if user_id:
            print('user_id:', user_id)
            session.permanent = True
            session['user_id'] = user_id
            return redirect(url_for('history'))
        elif username != "" and password != "":
            message = "用户名或密码错误"
            return render_template('login.html', message=message)
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


@app.route('/history')
def history():
    user_id = session.get('user_id')
    user_history = DBHelper.get_history(user_id)
    # food_name,time,restaurant,history.food_id
    history_list = []
    for record in user_history:
        food_name = record[0]
        t = record[1]
        restaurant = record[2]
        food_id = record[3]
        print(food_id)
        score = DBHelper.get_avg_score(food_id)
        image = DBHelper.get_img(food_id)
        print(image)
        time_array = time.localtime(t)
        time_format = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        record_dict = dict(food_name=food_name, time_format=time_format, restaurant=restaurant, image=image, score=score)
        history_list.append(record_dict)
    print(history_list)
    context = {'history': history_list}
    return render_template('01-history.html', **context)


@app.route('/history/<food>')
def history_detail(food):
    return render_template('01-history-detail.html', food=food)


@app.route('/history/upload', methods=['GET', 'POST'])
def history_upload():
    if request.method == 'POST':
        t = time.time()
        # 检查标题
        if 'food_name' == '':
            message = '请输入食物名称'
            return redirect(url_for('history', message=message))
        # 检查图片是否存在
        if 'file' not in request.files:
            filename = 'logo.png'
        else:
            file = request.files['file']
            # 检查图片格式
            if file and not allowed_file(file.filename):
                message = '请上传jpg格式的图片'
                return redirect(url_for('history', message=message))
            # 时间戳作为文件名
            filename = str(t) + '.jpg'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(file.filename)
        # 更新数据库
        food_name = request.form['food_name']
        restaurant = request.form['restaurant']
        comment = request.form['comment']
        score = request.form['score']
        hot = request.form['hot']
        salty = request.form['salty']
        sweet = request.form['sweet']
        sour = request.form['sour']
        oily = request.form['oily']
        food_id = DBHelper.get_food_id(food_name, restaurant)
        user_id = session.get('user_id')
        DBHelper.edit_comment(user_id, food_id, score, hot, salty, sweet, sour, oily, comment, '', '')
        DBHelper.picture_path(user_id, food_id, filename)
        DBHelper.new_history(user_id, food_id, t)
        return redirect(url_for('history'))
    return render_template('01-history-upload.html')


@app.route('/suggestions')
def suggestions():
    return render_template('02-suggestions.html')


@app.route('/group')
def group():
    return render_template('03-group.html')


@app.route('/aboutme')
def aboutme():
    return render_template('04-aboutme.html')


@app.route('/aboutme/settings')
def aboutme_settings(name):
    return render_template('04-aboutme-settings.html')


# ------以下为测试页面-------


@app.route('/login-test', methods=['GET', 'POST'])
def login_test():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username, password)
        user_id = DBHelper.user_verification(username, password)
        if user_id:
            print('user_id:', user_id)
            session.permanent = True
            session['user_id'] = user_id
            return redirect(url_for('history_test'))
        elif username != "" and password != "":
            message = "用户名或密码错误"
            return render_template('login-test.html', message=message)
    return render_template('login-test.html')


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
