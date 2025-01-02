from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from models import get_btc_current_price, get_all_current_prices
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql.sqltypes import DateTime

app = Flask(__name__)

#Creating an SQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Base = declarative_base()
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    balance_btc = db.Column(db.Float, default=0.0)
    balance_eth = db.Column(db.Float, default=0.0)
    balance_czk = db.Column(db.Float, default=0.0)
    balance_locked = db.Column(db.Float, default=0.0)

    strategies = db.relationship('Strategy', back_populates='user')
class Strategy(db.Model):
    __tablename__ = 'strategies'

    strategy_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    amount = db.Column(db.Integer, nullable=False)
    frequency = db.Column(db.Integer, nullable=False)
    limit = db.Column(db.Integer, nullable=False)
    avg_price = db.Column(db.Float, nullable=False)
    goal = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Float, nullable=False)
    num_of_transactions = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', back_populates='strategies')
    transactions = db.relationship('Transaction', back_populates='strategy')
class Transaction(db.Model):
    __tablename__ = 'transactions'

    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategies.strategy_id'))
    amount = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    strategy = db.relationship('Strategy', back_populates='transactions')
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

