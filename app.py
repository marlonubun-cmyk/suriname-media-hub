from flask import Flask, render_template
from config import Config
from models import db, Media
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

@app.route("/")
def home():
    media = Media.query.filter_by(active=True).all()
    return render_template("index.html", media=media)

if __name__ == "__main__":
    app.run(debug=True)