from flask import Flask, flash, redirect, render_template, request
import os
import sqlite3
import uuid
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/upload/'
ALLOWED_EXTENSIONS = set(['gif', 'jpg', 'jpeg', 'png'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = b"private_key"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def unique_filename(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    return f'{str(uuid.uuid4())}.{ext}'

def get_data(type, board_route, post_id=0):
    with sqlite3.connect('database.db') as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        if type == "posts":
            if post_id == 0:
                cur.execute(f"SELECT * FROM posts_{board_route} ORDER BY id DESC")
            else:
                cur.execute(f"SELECT * FROM posts_{board_route} WHERE id = {post_id}")
        elif type == "comments":
            cur.execute(f"SELECT * FROM comments_{board_route}_{post_id} ORDER BY id")
        elif type == "num_comments":
            cur.execute(f'SELECT COUNT(*) as "num" FROM comments_{board_route}_{post_id}')
        return cur.fetchall()

def board(board_route, board_name):
    with sqlite3.connect('database.db') as db:
        if request.method == "POST":
            name = request.form.get("name")
            if not name:
                name = "Anonymous"
            post = request.form.get("post")
            if not post:
                flash("Post cannot be empty!", category="error")
                return redirect(f'/{board_route}')
            image = request.files["image"]
            if not image:
                flash("Post must contain an image!", category="error") 
                return redirect(f'/{board_route}')
            if image and allowed_file(image.filename):
                filename = secure_filename(unique_filename(image.filename))
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                img_src = f'{UPLOAD_FOLDER}{filename}'
            db.execute(f"INSERT INTO posts_{board_route} (name, post, img_src, timestamp) VALUES (?, ?, ?, strftime('%Y-%m-%d %H:%M:%S','now'))", (name, post, img_src))
            return redirect(f"/{board_route}")
        else:
            db.execute(f"CREATE TABLE IF NOT EXISTS posts_{board_route} (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(64), post VARCHAR(4096) NOT NULL, img_src VARCHAR(255) NOT NULL, timestamp DATETIME)")
            posts = get_data("posts", board_route)
            return render_template("board.html", board_route=board_route, board_name=board_name, posts=posts, get_data=get_data)

def board_post(board_route, board_name, post_id):
    with sqlite3.connect('database.db') as db:
        if request.method == "POST":
            name = request.form.get("name")
            if not name:
                name = "Anonymous"
            comment = request.form.get("comment")
            if not comment:
                flash("Comment cannot be empty!", category="error")
                return redirect(f'/{board_route}/{post_id}')
            image = request.files["image"]
            if not image:
                img_src = None
            if image and allowed_file(image.filename):
                filename = secure_filename(unique_filename(image.filename))
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                img_src = f'{UPLOAD_FOLDER}{filename}'
            db.execute(f"INSERT INTO comments_{board_route}_{post_id} (post_id, name, comment, img_src, timestamp) VALUES (?, ?, ?, ?, strftime('%Y-%m-%d %H:%M:%S','now'))", (post_id, name, comment, img_src))
            return redirect(f"/{board_route}/{post_id}") 
        else:
            db.execute(f"CREATE TABLE IF NOT EXISTS comments_{board_route}_{post_id} (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, name VARCHAR(64), comment VARCHAR(4096) NOT NULL, img_src VARCHAR(255), timestamp DATETIME)")
            post = get_data("posts", board_route, post_id)
            comments = get_data("comments", board_route, post_id)
            return render_template("board_post.html", board_route=board_route, board_name=board_name, post=post, comments=comments)

@app.route("/")
def check_age():
    return render_template('check_age.html')

@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/a", methods=["GET", "POST"])
def a():
    return board("a", "ANIME")

@app.route("/a/<int:post_id>", methods=["GET", "POST"])
def a_post(post_id):
    return board_post("a", "ANIME", post_id)

@app.route("/b", methods=["GET", "POST"])
def b():
    return board("b", "RANDOM")

@app.route("/b/<int:post_id>", methods=["GET", "POST"])
def b_post(post_id):
    return board_post("b", "RANDOM", post_id)

@app.route("/c", methods=["GET", "POST"])
def c():
    return board("c", "CARTOONS")
    
@app.route("/c/<int:post_id>", methods=["GET", "POST"])
def c_post(post_id):
    return board_post("c", "CARTOONS", post_id)

@app.route("/d", methods=["GET", "POST"])
def d():
    return board("d", "DRAMA")

@app.route("/d/<int:post_id>", methods=["GET", "POST"])
def d_post(post_id):
    return board_post("d", "DRAMA", post_id)

@app.route("/m", methods=["GET", "POST"])
def m():
    return board("m", "MUSIC")
    
@app.route("/m/<int:post_id>", methods=["GET", "POST"])
def m_post(post_id):
    return board_post("m", "MUSIC", post_id)
    
@app.route("/pc", methods=["GET", "POST"])
def pc():
    return board("pc", "PERSONAL COMPUTERS")
    
@app.route("/pc/<int:post_id>", methods=["GET", "POST"])
def pc_post(post_id):
    return board_post("pc", "PERSONAL COMPUTERS", post_id)

@app.route("/vg", methods=["GET", "POST"])
def vg():
    return board("vg", "VIDEO GAMES")

@app.route("/vg/<int:post_id>", methods=["GET", "POST"])
def vg_post(post_id):
    return board_post("vg", "VIDEO GAMES", post_id)

@app.route("/x", methods=["GET", "POST"])
def x():
    return board("x", "PARANORMAL")

@app.route("/x/<int:post_id>", methods=["GET", "POST"])
def x_post(post_id):
    return board_post("x", "PARANORMAL", post_id)
