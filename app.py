from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from models import get_dca_transactions, get_api_credentials
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

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
    password = db.Column(db.String(30), nullable=False)
    public_key = db.Column(db.String(50), nullable=False)
    private_key = db.Column(db.String(50), nullable=False)
    api_user_id = db.Column(db.String(10), nullable=False)
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

#Database manipulation
@app.route('/create_strategy', methods=['POST'])
def create_new_strategy():
    user_id = request.json['user_id']
    amount = request.json['amount']
    frequency = request.json['frequency']
    limit = 0 if request.json.get('limit') is None else request.json['limit']
    goal = request.json['goal']

    new_strategy = Strategy(
        user_id=user_id,
        amount=amount,
        frequency=frequency,
        limit=limit,
        avg_price=0,
        goal=goal,
        balance=0,
        num_of_transactions=0
    )

    db.session.add(new_strategy)
    db.session.commit()
    return jsonify({"message": "Strategy added successfully", "strategy_id": new_strategy.strategy_id}), 201

@app.route('/add_user', methods=['POST'])
def add_new_user():
    username = request.json['username']
    password = request.json['password']
    public_key = request.json['public_key']
    private_key = request.json['private_key']
    api_user_id = request.json['api_user_id']
    new_user = User(
        username=username,
        password=password,
        public_key=public_key,
        private_key=private_key,
        api_user_id=api_user_id
    )

    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User added successfully", "user_id": new_user.user_id}), 201

@app.route('/add_transactions', methods=['POST', 'GET'])
def add_new__dca_transactions():
    user_id = request.json['user_id']
    strategy_id = request.json['strategy_id']
    user_data = User.query.get(user_id)
    public_key = user_data.public_key
    private_key = user_data.private_key
    api_user_id = user_data.api_user_id
    public_key, nonce, signature = get_api_credentials(api_user_id, public_key, private_key)
    print(f'Public key: {public_key}, nonce: {nonce}, signature: {signature}, api_user_id: {api_user_id}, private_key: {private_key}')
    def get_transactions(user_id, strategy_id):
        transactions = Transaction.query.join(Strategy).filter(Strategy.user_id == user_id,
                                                               Strategy.strategy_id == strategy_id).order_by(Transaction.date.desc()).limit(35).all()
        transactions_list = [
            {"transaction_id": transaction.transaction_id, "amount": transaction.amount, "price": transaction.price,
             'date': transaction.date} for transaction in transactions]
        return transactions_list

    old_transactions = get_transactions(user_id, strategy_id)
    new_transactions = get_dca_transactions(public_key, signature, '259719', nonce, amount=125)
    for transaction in new_transactions:
        #transaction vypada takto: {'amount': 5.514e-05, 'price': 2252865, 'date': '2024-12-23'}
        if not any(t['amount'] == transaction['amount'] and t['date'] == transaction['date'] for t in old_transactions):
            transaction_date = datetime.strptime(transaction['date'], '%Y-%m-%d').date()

            if not any(
                    t['amount'] == transaction['amount'] and t['date'] == transaction_date for t in old_transactions):
                new_transaction = Transaction(
                    strategy_id=1,
                    amount=transaction['amount'],
                    price=transaction['price'],
                    date=transaction_date
                )
                db.session.add(new_transaction)

    db.session.commit()
    return jsonify({"message": "Transactions added successfully"}), 201

@app.route('/get_user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({"user_id": user.user_id, "username": user.username,
                        'balance_btc': user.balance_btc, 'balance_eth': user.balance_eth, 'balance_czk': user.balance_czk, 'balance_locked': user.balance_locked})
    else:
        return jsonify({"message": "User not found"}), 404

@app.route('/get_strategies/<int:user_id>', methods=['GET'])
def get_strategies(user_id):
    strategies = Strategy.query.filter_by(user_id=user_id).all()
    strategies_list = [{"strategy_id": strategy.strategy_id, "amount": strategy.amount, "frequency": strategy.frequency,
                        'limit': strategy.limit, 'avg_price': strategy.avg_price, 'goal': strategy.goal, 'balance': strategy.balance,
                        'num_of_transactions': strategy.num_of_transactions, 'transactions': [{'transaction_id': transaction.transaction_id,
                                                                                             'amount': transaction.amount, 'price': transaction.price,
                                                                                             'date': transaction.date} for transaction in strategy.transactions
                                                                                                ]}
                       for strategy in strategies]
    return jsonify(strategies_list)



#Frontend
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

