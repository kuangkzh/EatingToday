import os
from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory,session
from werkzeug.utils import secure_filename
from datetime import timedelta
import time
import DBHelper


UPLOAD_FOLDER = 'static/img/food/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

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
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template('01-history-upload.html', message='上传成功！')
    return render_template('01-history-upload.html')


@app.route('/suggestions')
def suggestions():
    return render_template('02-suggestions.html')


@app.route('/group')
def group():
    user_id = session.get('user_id')
    res = DBHelper.conn.execute("SELECT feast.food_id,appoint_time,restaurant,food_name,people_limit,people_count,nickname,feast.feast_id"
                                " FROM feast JOIN foods ON foods.food_id=feast.food_id "
                                "JOIN user ON feast.host_user_id=user.user_id "
                                "JOIN (SELECT feast_id,count(*) as people_count FROM appointment GROUP BY feast_id)"
                                " as tmp ON tmp.feast_id=feast.feast_id;").fetchall()
    groups = []
    for i in res:
        color = "#0b0" if i[4] > i[5] else "#b00"
        status = "加入" if DBHelper.conn.execute("SELECT count(*) FROM appointment WHERE feast_id=? AND user_id=?",
                                               (i[7], user_id)).fetchone()[0] == 0 else "已加入"
        groups.append({"image": DBHelper.get_img(i[0]),
                       "time_format": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i[1])),
                       "restaurant": i[2], "food_name": i[3], "people_limit": i[4], "people_count": i[5],
                       "score": DBHelper.get_avg_score(i[0]), "host": i[6], "color": color,
                       "feast_id": i[7], "status": status})
    context = {'groups': groups}
    return render_template('03-group.html', **context)


@app.route('/aboutme')
def aboutme():
    return render_template('04-aboutme.html')


@app.route('/aboutme/settings')
def aboutme_settings(name):
    return render_template('04-aboutme-settings.html')


@app.route('/appoint/<feast_id>')
def appoint(feast_id):
    DBHelper.new_appoint(feast_id, session.get('user_id'), lambda: print(""))
    return redirect("/group")

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
