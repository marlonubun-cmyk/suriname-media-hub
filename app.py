import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# ----------------------------
# App setup
# ----------------------------
app = Flask(__name__)

# ----------------------------
# Database config (Render proof)
# ----------------------------
database_url = os.environ.get("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is not set")

# Render sometimes uses postgres://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Optional: prevent connection timeout issues on Render
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

db = SQLAlchemy(app)

# ----------------------------
# Example Model (Test model)
# ----------------------------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<User {self.email}>"

# ----------------------------
# Routes
# ----------------------------

@app.route("/")
def home():
    return "App is running 🚀"

@app.route("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


# ----------------------------
# Database init (SAFE)
# ----------------------------
def init_db():
    with app.app_context():
        db.create_all()


# ----------------------------
# Local run only
# ----------------------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
