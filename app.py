from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///web_dev.db'
db = SQLAlchemy(app) 




class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)






@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')



@app.route('/posts')
def posts():
  posts = Post.query.all()
  return render_template('posts.html', posts=posts)



@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == "POST":
      title = request.form['title']
      text = request.form['text']
      post = Post(title=title, text=text)

      try:
        db.session.add(post)
        db.session.commit()
        return redirect('/index')
      except:
        return "При добавлении поста произошла ошибка"
      
    else:
      return render_template('create.html')






if __name__ == "__main__":
  app.run(debug=True)