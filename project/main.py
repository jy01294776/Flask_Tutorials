from flask import Blueprint, render_template,request, url_for, flash, redirect,Flask
from flask_login import login_required, current_user
from . import db
import os
import sqlite3
from werkzeug.exceptions import abort

main = Blueprint('main', __name__)
main.secret_key = 'your secret key'

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
def profile():
    return render_template('profile.html', name = current_user.name)

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your secret key'
    app.register_blueprint(main)
    return app

def get_db_connection():
    import os.path

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR,'database.db')
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

@main.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)


@main.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)


@main.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))