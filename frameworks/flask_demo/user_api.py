from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/alexlc/Products/src/AI/python-tutorials/basic/gram/school_db.db'
db = SQLAlchemy(app)
# Manage DB schema
# migrate = Migrate(app, db)

# MongoDB
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/my_mg'
# mongo = PyMongo(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True,nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

with app.app_context():
    # Or use flask db init; flask db migrate; flask db upgrade cmd to init DB
    db.create_all()

@app.route('/getUserNames')
def index():
    users = User.query.all()
    return f'Users:{[user.username for user in users]}'

    # Query with MongoDB
    # users = mongo.db.users.find()
    # return jsonify([user for user in users])

if __name__ == '__main__':
    app.run(debug=True)
