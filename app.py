from crypt import methods

from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from models import (get_last_transaction, get_api_credentials, get_dca_limit_price, make_limit_order, check_order_status,
                    get_pending_dca_transaction, cancel_pending_dca_transaction, make_instant_order, get_btc_czk_price, get_balances)
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
#musim pridat type - BUY/SELL
class Transaction(db.Model):
    __tablename__ = 'transactions'

    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategies.strategy_id'))
    amount = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='FILLED')
    order_id = db.Column(db.Integer, nullable=False)
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

@app.route('/edit_strategy/<int:user_id>/<int:strategy_id>', methods=['POST', 'GET'])
def edit_strategy(user_id, strategy_id):
    strategy = Strategy.query.filter_by(user_id=user_id, strategy_id=strategy_id).first()
    if not strategy:
        return jsonify({"error": "Strategy not found"}), 404

    data = request.get_json()

    strategy.amount = data.get('amount', strategy.amount)
    strategy.frequency = data.get('frequency', strategy.frequency)
    strategy.limit = data.get('limit', strategy.limit)
    strategy.goal = data.get('goal', strategy.goal)

    db.session.commit()
    return jsonify({"message": f"Strategy  {strategy.strategy_id}edited successfully"}), 201

@app.route('/update', methods=['POST', 'GET'])
def update():
    user_id = request.json['user_id']
    user = User.query.get(user_id)
    data = request.get_json()

    public_key = user.public_key
    private_key = user.private_key
    api_user_id = user.api_user_id
    public_key, nonce, signature = get_api_credentials(api_user_id, public_key, private_key)

    #update user
    czk_balance, btc_balance, eth_balance, balance_locked = get_balances(api_user_id, public_key, nonce, signature)
    user.balance_btc = btc_balance
    user.balance_eth = eth_balance
    user.balance_czk = czk_balance
    user.balance_locked = balance_locked
    db.session.commit()

    #update strategies
    strategies = Strategy.query.filter_by(user_id=user_id).all()
    strat_ids = [strategy.strategy_id for strategy in strategies]

    for id in strat_ids:
        strategy = Strategy.query.get(id)
        transactions = strategy.transactions
        bought =  float(0)
        amount = float(0)
        for transaction in transactions:
            if transaction['status'] == 'FILLED':
                purchase = transaction['amount'] * transaction['price']
                bought += purchase
                amount+= transaction['amount']

        num_of_transactions = strategy.num_of_transactions
        strategy.avg_price = round(bought/num_of_transactions, 2)

        public_key, nonce, signature = get_api_credentials(api_user_id, public_key, private_key)
        current_btc_price = int(get_btc_czk_price())

        strategy.balance = round(current_btc_price*amount, 2)

        db.session.commit()

    return jsonify({"message": f"User {user.user_id}: {user.username}updated successfully"}), 201


    avg_price = ''
    balance = ''


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



@app.route('/get_user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({"user_id": user.user_id, "username": user.username,
                        'balance_btc': user.balance_btc, 'balance_eth': user.balance_eth, 'balance_czk': user.balance_czk, 'balance_locked': user.balance_locked,
                        'strategies': [{'strategy_id': strategy.strategy_id, 'amount': strategy.amount, 'frequency': strategy.frequency,
                                        'limit': strategy.limit, 'avg_price': strategy.avg_price, 'goal': strategy.goal, 'balance': strategy.balance,
                                        'num_of_transactions': strategy.num_of_transactions} for strategy in user.strategies]}), 200
    else:
        return jsonify({"message": "User not found"}), 404

@app.route('/get_user_id', methods=['POST', 'GET'])
def get_user_id():
    username = request.json['username']
    user = User.query.filter_by(username).first()
    if user:
        return int(user.user_id)
    return None

@app.route('/get_strategies/<int:user_id>', methods=['GET'])
def get_strategies(user_id):
    strategies = Strategy.query.filter_by(user_id=user_id).all()
    strategies_list = [{"strategy_id": strategy.strategy_id, "amount": strategy.amount, "frequency": strategy.frequency,
                        'limit': strategy.limit, 'avg_price': strategy.avg_price, 'goal': strategy.goal, 'balance': strategy.balance,
                        'num_of_transactions': len(strategy.transactions), 'transactions': [{'transaction_id': transaction.transaction_id,
                                                                                             'amount': transaction.amount, 'price': transaction.price, 'status': transaction.status,
                                                                                             'date': transaction.date, 'order_id': transaction.order_id} for transaction in strategy.transactions
                                                                                                ]}
                       for strategy in strategies]
    return jsonify(strategies_list)

#toto by se melo provest kazdy interval dca
@app.route('/make_dca_order', methods=['POST', 'GET'])
def make_dca_limit_order():
    user_id, strategy_id = request.json['user_id'], request.json['strategy_id']
    user_data, strategy_data = User.query.get(user_id), Strategy.query.get(strategy_id)

    limit_price = get_dca_limit_price(strategy_data.limit)
    amount = strategy_data.amount

    public_key = user_data.public_key
    private_key = user_data.private_key
    api_user_id = user_data.api_user_id
    public_key, nonce, signature = get_api_credentials(api_user_id, public_key, private_key)

    response = make_limit_order(limit_price, amount, api_user_id, public_key, nonce, signature)
    if response['error'] == False:
        public_key, nonce, signature = get_api_credentials(api_user_id, public_key, private_key)
        order_id = get_pending_dca_transaction(public_key, signature, api_user_id, nonce, amount)

        new_transaction = Transaction(
            strategy_id=strategy_id,
            amount=amount,
            price=limit_price,
            status='OPEN',
            order_id=order_id,
            date=datetime.now()
        )

        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({"message": "Order placed successfully"}), 201
    else:
        return jsonify({"message": f"{response['errorMessage']}"}), 400

#KDYZ NASTAL DCA DEN
@app.route('/cancel_and_buy_dca', methods=['POST', 'GET'])
def cancel_and_buy_dca():
    user_id, strategy_id = request.json['user_id'], request.json['strategy_id']
    user_data, strategy_data = User.query.get(user_id), Strategy.query.get(strategy_id)

    amount = strategy_data.amount
    order_id = strategy_data.transactions[-1].order_id

    public_key = user_data.public_key
    private_key = user_data.private_key
    api_user_id = user_data.api_user_id

    public_key, nonce, signature = get_api_credentials(api_user_id, public_key, private_key)
    limit_order_status = check_order_status(api_user_id, public_key, nonce, signature, order_id)

    if limit_order_status == 'OPEN':
        strategy_data.transactions[-1].status = 'CANCELLED'
        db.session.commit()

        public_key, nonce, signature = get_api_credentials(api_user_id, public_key, private_key)
        transaction_id = get_pending_dca_transaction(public_key, signature, api_user_id, nonce, amount)

        if transaction_id:
            public_key, nonce, signature = get_api_credentials(api_user_id, public_key, private_key)

            if cancel_pending_dca_transaction(public_key, signature, api_user_id, nonce, transaction_id):
                public_key, nonce, signature = get_api_credentials(api_user_id, public_key, private_key)

                make_instant_order(amount, api_user_id, public_key, nonce, signature)
                public_key, nonce, signature = get_api_credentials(api_user_id, public_key, private_key)

                order_id = get_last_transaction(public_key, signature, api_user_id, nonce, amount)

                new_transaction = Transaction(
                    strategy_id=strategy_id,
                    amount=amount,
                    price=get_btc_czk_price(),
                    status='FILLED',
                    order_id=order_id,
                    date=datetime.now()
                )
                db.session.add(new_transaction)
                db.session.commit()
                return jsonify({"message": "Transaction cancelled and instant order placed"}), 200

            else: return jsonify({"message": "Transaction not cancelled"}), 400

        else: return jsonify({"message": "Transaction not found"}), 404

    else: return jsonify({"message": "Order already filled"}), 400


#Frontend
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
