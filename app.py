import sqlite3
import os
from flask import Flask, render_template, g, request, url_for, redirect
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user
from UserLogin import UserLogin

# Конфигурация
DATABASE = '/page.db'
DEBUG = True
SECRET_KEY = '2bc9e26090f2236c531e1f60e9f69cd4d077ae7f'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'page.db')))

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link.db'):
        g.link_db = connect_db()
    return g.link_db


@app.route('/')
def index():
    return render_template('base.html')


@app.route('/enter')
def enter():
    return render_template('enter.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userLogin = UserLogin().create(user)
            login_user(userLogin)
            return redirect(url_for('enter'))

        print('Неверный пароль или логин')
    return render_template('login.html', menu=dbase.getMenu(), title="Авторизация")


@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                print('good')
                return redirect(url_for('login'))
            else:
                print('bad')
        else:
            print('repeat')
    return render_template('sign_up.html', menu=dbase.getMenu(), title="Регистрация")


dbase = None


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link.db'):
        g.link_db.close()


if __name__ == "__main__":
    app.run(debug=True)
