from flask import Flask, render_template, request, redirect
import sqlite3
import re
import unicodedata
import os



#config methods
BASE_DIR = os.path.dirname(__file__)

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
conn = sqlite3.connect(os.path.join(BASE_DIR, 'db.sqlite3'), check_same_thread=False) #not recommended, just done for this demo
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

def remove_post(post_id):
    conn.execute('''
    DELETE FROM post 
    WHERE post_id = ?
    ''', (post_id,))
    conn.commit()

def change_post(title, post, post_id):
    slug = slugify(title)
    conn.execute('''
    UPDATE post 
    set 
      title = ?,
      body = ?,
      slug = ?
    WHERE 
      post_id = ?
    ''', (title, post, slug, post_id))
    conn.commit()

#Controllers

DEFAULT_USER = 'admin'

app = Flask(__name__)


@app.route('/')
def index():
    curs = conn.execute('SELECT * FROM post ORDER BY DATE DESC ')
    posts = [post for post in curs.fetchall()]
    return render_template('index.html', posts = posts)

@app.route('/form_submit/<action>/<post_id>')
def form_submit(action, post_id):
    return render_template('form_submission_response.html', action=action, post_id = post_id)




@app.route('/delete/<int:id>', methods=['POST'])
def delete_post(id):
    if request.method == 'POST':
        print 'deleting, id:', id
        result = remove_post(id)
        return redirect('/form_submit/deleted/%d'%(id, ))
    else:
        return """Shouldnt be on this page and raise an error"""

@app.route('/create', methods=['GET', 'POST'])
def create_post():

    if request.method == "POST":
        title = request.form.get('title', '')
        post = request.form.get('blog-post', '')
        insert_post(title=title, post=post,user=DEFAULT_USER)
        return redirect('/form_submit/created/'+title)

    return render_template('post_create.html')

@app.route('/post/<int:id>/<slug>')
def detail_post(id, slug):
    curs = conn.execute('SELECT * FROM post where post_id = ?', (id, ))
    result = curs.fetchone()
    return render_template('post_detail.html', post = result)



@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_post(id):

    if request.method == "POST":
        title = request.form.get('title', '')
        post = request.form.get('blog-post', '')
        change_post(title=title, post=post, post_id=id)
        return redirect('/form_submit/updated/%d'%(id,))
    else:
        curs = conn.execute('SELECT * FROM post where post_id = ?', (id,))
        post = curs.fetchone()
        return render_template('post_update.html', title=post[3], body=post[4])

if __name__ == "__main__":
    import os

    init_db()
    print BASE_DIR
    app.run(debug=True)