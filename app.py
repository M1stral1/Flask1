from flask import Flask, render_template, url_for, request, redirect, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from bcrypt import hashpw, gensalt
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Flask1.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Установите собственный секретный ключ
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Указывает URL-адрес для входа
db = SQLAlchemy(app)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Проверка, что пользователь с таким именем или email не существует
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return 'Имя пользователя или email уже заняты'

        # Хеширование пароля
        hashed_password = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

        # Создание нового пользователя и сохранение в базе данных
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Успешная регистрация', 'success')  # Добавление флеш-сообщения с категорией 'success'

        return redirect(url_for('front'))

    return render_template('register.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/login")
def index():
    return render_template("index.html")
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Проверка пользователя в базе данных
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            login_user(user)  # Вход пользователя
            flash('Успешный вход', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Неверные учетные данные', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()  # Выход пользователя
    flash('Вы успешно вышли', 'success')
    return redirect(url_for('front'))


@app.route("/")
def front():
    return render_template('front.html')


@app.route("/history")
def history():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template("history.html", articles=articles)


@app.route("/history/<int:id>")
def history_detail(id):
    article = Article.query.get(id)
    return render_template("history_detail.html", article=article)


@app.route("/history/<int:id>/delete")
def history_delete(id):
    article = Article.query.get_or_404(id)
    try:
        db.session.delete(article)
        db.session.commit()
        return redirect("/history")
    except:
        return "There is an error"


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/history/<int:id>/update", methods=['POST', 'GET'])
def history_update(id):
    article = Article.query.get_or_404(id)
    if request.method == "POST":
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/')
        except:
            return "There is an error"
    else:
        return render_template("post_update.html", article=article)


@app.route("/create", methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        article = Article(title=title, intro=intro, text=text)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/')
        except:
            return "There is an error"
    else:
        return render_template("create.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=2682)
