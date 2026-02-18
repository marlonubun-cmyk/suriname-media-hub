import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

# ----------------------------
# App setup
# ----------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# ----------------------------
# Database config
# ----------------------------
database_url = os.environ.get("DATABASE_URL")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ----------------------------
# Login manager
# ----------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ----------------------------
# Models
# ----------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ----------------------------
# Routes
# ----------------------------

@app.route("/")
def index():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    posts = Post.query.all()
    return render_template("dashboard.html", posts=posts)


@app.route("/add-post", methods=["POST"])
@login_required
def add_post():
    title = request.form["title"]
    content = request.form["content"]

    new_post = Post(title=title, content=content)
    db.session.add(new_post)
    db.session.commit()

    return redirect(url_for("dashboard"))


# ----------------------------
# Init DB
# ----------------------------
def init_db():
    with app.app_context():
        db.create_all()

        # Create default admin if not exists
        if not User.query.filter_by(email="admin@site.com").first():
            admin = User(email="admin@site.com")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("Admin created: admin@site.com / admin123")


if __name__ == "__main__":
    init_db()
    app.run()
