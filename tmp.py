from flask import Flask, render_template, request, redirect
import sqlite3
import re
import unicodedata
import os

BASE_DIR = os.path.dirname(__file__)

_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')


def slugify(value):
    #https://gist.github.com/berlotto/6295018
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub('-', value)

#MODEL Layer

conn = sqlite3.connect(os.path.join(BASE_DIR, 'db.sqlite3'), check_same_thread=False)

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



#CONTROLLER Layer
app = Flask(__name__)
DEFAULT_USER = 'admin'

@app.route('/')
def index():
    curs = conn.execute('SELECT * FROM post ORDER BY DATE DESC ')
    posts = [post for post in curs.fetchall()]
    return render_template('index.html', posts = posts)

@app.route('/form_submit/<action>/<post_id>')
def form_submit(action, post_id):
    return render_template('form_submission_response.html', action=action, post_id = post_id)



@app.route('/create', methods=['GET', 'POST'])
def create_post():

    if request.method == 'POST':
        title = request.form.get('title', '')
        post = request.form.get('blog-post', '')
        #print title
        insert_post(title=title, post=post, user=DEFAULT_USER)
        return redirect('/form_submit/created/' + title)

    return render_template('post_create.html')


if __name__ == "__main__":
    print os.getcwd()
    print 'base_dir', BASE_DIR
    print 'DB Path', os.path.join(BASE_DIR, 'db.sqlite3')
    init_db()
    app.run(debug=True, port=5001)