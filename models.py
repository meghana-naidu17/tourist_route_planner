from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80),  unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    routes     = db.relationship('RouteHistory', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class RouteHistory(db.Model):
    __tablename__ = 'route_history'
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start        = db.Column(db.String(100), nullable=False)
    end          = db.Column(db.String(100), nullable=False)
    transport    = db.Column(db.String(50))
    optimize     = db.Column(db.String(50))
    distance     = db.Column(db.Float)
    cost         = db.Column(db.Integer)
    time         = db.Column(db.Integer)
    path         = db.Column(db.Text)   # JSON string of stop list
    searched_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Route {self.start}→{self.end}>'
