from flask import flash, url_for, abort
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///web_dev.db'
db = SQLAlchemy(app) 

# Редактирование поста
@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        if not title or not text:
            flash('Заполните все поля!', 'danger')
        else:
            post.title = title
            post.text = text
            db.session.commit()
            flash('Пост успешно обновлён!', 'success')
            return redirect(url_for('posts'))
    return render_template('edit_post.html', post=post)

# Удаление поста
@app.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Пост удалён!', 'success')
    return redirect(url_for('posts'))





class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('posts', lazy=True))





# Декоратор для начальной страницы
@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')




# Объединённая страница: просмотр и добавление постов
from flask import flash
@app.route('/posts', methods=['GET', 'POST'])
def posts():
    posts = Post.query.order_by(Post.id.desc()).all()
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('Только авторизованные пользователи могут добавлять посты.', 'danger')
            return redirect('/login')
        title = request.form['title']
        text = request.form['text']
        if not title or not text:
            flash('Заполните все поля!', 'danger')
        else:
            post = Post(title=title, text=text, user_id=current_user.id)
            try:
                db.session.add(post)
                db.session.commit()
                flash('Пост успешно добавлен!', 'success')
                return redirect('/posts')
            except Exception as e:
              app.logger.error(f"Ошибка при добавлении поста: {e}")
              flash('При добавлении поста произошла ошибка', 'danger')
    return render_template('posts.html', posts=posts)





app.secret_key = 'your_secret_key'  # обязательно для работы Flask-Login

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Модель пользователя
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return 'Пользователь с таким логином уже существует'
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect('/posts')
    return render_template('register.html')

# Страница логина
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect('/posts')
        else:
            return "Неверный логин или пароль"
    return render_template('login.html')

# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


# Удалён маршрут /create, логика перенесена в /posts



with app.app_context():
    db.create_all()



if __name__ == "__main__":
  app.run(debug=True)