from flask import Flask, render_template, request, redirect
import sqlite3
import re
import unicodedata

#util methods

_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


def slugify(value):
    #https://gist.github.com/berlotto/6295018
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub('-', value)


#Model

#create a DB connection
conn = sqlite3.connect('db.sqlite3', check_same_thread=False) #not recommended, just done for this demo
def init_db():
    conn.execute('''
      CREATE TABLE IF NOT EXISTS 
      post (
        post_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id TEXT NOT NULL,
        date TIMESTAMP  DEFAULT CURRENT_TIMESTAMP NOT NULL, 
        title TEXT NOT NULL, 
        body TEXT NOT NULL,
        slug TEXT NOT NULL
    )
    ''')
    conn.commit()

def insert_post(title, post, user):
    slug = slugify(title)

    conn.execute('''
    INSERT INTO post (user_id, title, body, slug)
    VALUES (?, ?, ?, ?)
    ''', (user, title, post, slug))
    conn.commit()


#Controllers

DEFAULT_USER = 'admin'

app = Flask(__name__)


@app.route('/')
def index():
    curs = conn.execute('SELECT * FROM post')
    posts = [post for post in  curs.fetchall()]
    return render_template('index.html', posts = posts)

@app.route('/create', methods=['GET', 'POST'])
def create_post():

    if request.method == "POST":
        title = request.form.get('title', '')
        post = request.form.get('blog-post', '')
        insert_post(title=title, post=post,user=DEFAULT_USER)
        return redirect('/')

    return render_template('post_create.html')


@app.route('/post/<int:id>/<slug>')
def detail_post(id, slug):
    pass







if __name__ == "__main__":
    init_db()
    app.run(debug=True)