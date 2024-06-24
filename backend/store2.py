from datetime import datetime
import json
import sys
from flask import Flask, flash, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from icecream import ic

# DEBUG = True

db = SQLAlchemy()

app = Flask(__name__, template_folder='../templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///storeDB.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'  # Needed for session management
db.init_app(app)

with app.app_context():
    db.create_all()

def custom_output(*args):
    """
    Custom output function for logging with timestamp.
    flush() = The log file updates in real time
    """
    time_str = datetime.now().strftime("%d-%m-%Y - %H:%M:%S")
    log_message = f"{time_str} {' '.join(map(str, args))}\n"
    log_file.write(log_message)
    log_file.flush()
    print(log_message)

class Users(db.Model):
    """
    Creating a Users Class
    """
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    _balance = db.Column(db.Float, default=0.0)
    _purchase_history = db.Column(db.PickleType, default=[])

    def __init__(self, first_name, last_name, username, password, role):
        """Initialize a new user."""
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = generate_password_hash(password)
        self._balance = 0
        self._purchase_history = []
        self.role = role

    def __repr__(self):
        return f'<User (ID = {self.id}, Name={self.first_name} {self.last_name})>'

    def as_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'balance': self._balance,
            'purchase_history': self._purchase_history,
            'role': self.role
        }

    def __str__(self) -> str:
        return json.dumps(self.as_dict())

    def basic_user(self):
        print(f"User ID: {self.id}, First Name: {self.first_name} Is A Basic User")

    def reset_password(self, new_password):
        """Reset the user's password."""
        self.password = generate_password_hash(new_password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password is correct."""
        return check_password_hash(self.password, password)

    def deposit(self, amount):
        """Deposit an amount to the user's balance."""
        if amount > 0:
            self._balance += amount
        else:
            raise ValueError("Deposit amount must be positive")

    def withdraw(self, amount):
        """Withdraw an amount from the user's balance."""
        if self._balance >= amount:
            self._balance -= amount
        else:
            raise ValueError("Insufficient balance")

    def add_purchase(self, game_title):
        """Add a game to the user's purchase history."""
        self._purchase_history.append(game_title)

    @property
    def balance(self):
        return self._balance

    @property
    def purchase_history(self):
        return self._purchase_history


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Game {self.title}>'

    def __init__(self, title, price, stock):
        self.title = title
        self.price = price
        self.stock = stock

    def as_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'stock': self.stock
        }


class GamingStore:
    """Represents the gaming store."""

    def __init__(self):
        """Initialize the gaming store with users and games."""
        self.users = []
        self.games = []

    def create_account(self, first_name, last_name, username, password, role="Basic User"):
        """Create a new user or admin account."""
        user = Users(first_name, last_name, username, password, role)
        add_entry_to_database(user)
        ic("User Created!", username)
        return user

    def get_user_by_id(self, user_id):
        """Retrieve a user by their user ID."""
        return next((user for user in self.users if str(user.id) == str(user_id)), None)

    def get_user_by_username(self, username):
        """Retrieve a user by their username."""
        return next((user for user in self.users if user.username == username), None)

    def show_all_users(self, show_admins=False):
        """Display all users, optionally showing admin users."""
        print("Accounts:")

        if show_admins:
            users_to_show = self.users
        else:
            users_to_show = [user for user in self.users if not user.role == "Admin"]

        for user in users_to_show:
            if user.role == "Admin":
                user.user_is_admin()
            else:
                user.basic_user()
            print(user)
            print()

    def deposit_to_account(self, user):
        """Allow a user to deposit money into their account."""
        try:
            amount = float(input("Enter amount to deposit: "))
            user.deposit(amount)
            print(f"Deposit of ${amount:.2f} successful. New balance: ${user.balance:.2f}")
        except ValueError:
            print("Invalid amount. Deposit failed.")

    def check_balance(self, user):
        """Check the balance of a user's account."""
        print(f"Current Balance for {user.username}: ${user.balance:.2f}")

    def delete_account(self, user):
        """Delete a user's account and log them out."""
        username = input("Enter username: ")
        password = input("Enter password: ")
        if user.username == username and user.check_password(password):
            confirmation = input("Are you sure you want to delete the account? (y/n): ")
            if confirmation.lower() == 'y':
                self.users.remove(user)
                print(f"Account for {user.username} deleted.")
                print("Logging out...")
                return True  # Indicate successful deletion
        else:
            print("Incorrect username or password. Account deletion failed.")
        return False  # Indicate deletion failure

    def purchase_history(self, user):
        """View the purchase history of a user."""
        print(f"Purchase History for {user.username}:")
        for purchase in user.purchase_history:
            print(f"Game - {purchase}")

    def view_all_users(self):
        """View all registered users."""
        print("All Registered Users:")
        with app.app_context():
            users = Users.query.all()
            for user in users:
                print(f'{user.id}: Name: {user.first_name} {user.last_name} (Username: {user.username})')

    def user_withdrawal(self):
        """Withdraw an amount from a user's account."""
        self.show_all_users()
        user_id = input("Please Insert User ID: ")
        c = self.get_user_by_id(user_id)
        if c:
            try:
                amount = float(input("Please Insert Amount to Withdraw: "))
                c.withdraw(amount)
                print("After Withdrawal: ")
                print(c)
                ic("Withdrawal: ", c)
            except ValueError as e:
                print(e)
        else:
            print(f"user with ID {user_id} not found.")

    def view_store(self):
        """Display all games in the store."""
        result = get_games()
        if result is None:
            print("OOPS, No games found :(")
        else:
            print(result)

    def view_library(self, user):
        """Display the games in the user's library (purchased games)."""
        if not user.purchase_history:
            print("You have no games in your library.")
        else:
            print("Your Library:")
            for game_title in user.purchase_history:
                print("Title: ", game_title)

    def add_game(self):
        """Add a new game to the store's inventory."""
        title = input("Enter game title: ")
        price = float(input("Enter game price: "))
        stock = int(input("Enter stock quantity: "))
        game = Game(title, price, stock)
        add_game_to_store(game)
        ic("Game Added!")

    def show_games(self):
        """Display all games available in the store."""
        print("Available Games:")
        for game in self.games:
            print(f"{game.id}: {game.title} - ${game.price:.2f} (Stock: {game.stock})")

    def show_all_users(self, show_admins=False):
        """Display all users, optionally showing admin users."""
        print("Accounts:")

        if show_admins:
            users_to_show = self.users
        else:
            users_to_show = [user for user in self.users if not user.role == "Admin"]

        for user in users_to_show:
            if user.role == "Admin":
                user.user_is_admin()
            else:
                user.basic_user()
            print(user)
            print()

    def buy_game(self, user, game_id):
        """Allow a user to purchase a game."""
        game = next((game for game in self.games if game.id == game_id), None)
        if game:
            if user.balance >= game.price and game.stock > 0:
                user.withdraw(game.price)
                game.stock -= 1
                user.add_purchase(game.title)
                print(f"Game '{game.title}' purchased successfully!")
            else:
                print("Insufficient balance or game out of stock.")
        else:
            print("Game not found.")

    def send_gift(self, sender, receiver_username, game_id):
        """Allow a user to send a game as a gift to another user."""
        receiver = self.get_user_by_username(receiver_username)
        if receiver:
            game = next((game for game in self.games if game.id == game_id), None)
            if game:
                if sender.balance >= game.price and game.stock > 0:
                    sender.withdraw(game.price)
                    game.stock -= 1
                    receiver.add_purchase(game.title)
                    print(f"Game '{game.title}' gifted to {receiver.username} successfully!")
                else:
                    print("Insufficient balance or game out of stock.")
            else:
                print("Game not found.")
        else:
            print("Receiver not found.")

def add_entry_to_database(entry):
    """Add a new entry to the database."""
    with app.app_context():
        db.session.add(entry)
        db.session.commit()

def get_games():
    """Retrieve all games from the database."""
    with app.app_context():
        games = Game.query.all()
        return [game.as_dict() for game in games]

def add_game_to_store(game):
    """Add a game to the store's database."""
    with app.app_context():
        db.session.add(game)
        db.session.commit()

def initialize_database():
    """Initialize the database with initial data."""
    with app.app_context():
        db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register_view')
def register_view():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        print("Received data:", data)  # Debug log

        if data is None:
            return jsonify({'error': 'Invalid data'}), 400

        first_name = data.get('userFirstName')
        last_name = data.get('userLastName')
        username = data.get('userUserName')
        password = data.get('userPassword')
        confirm_password = data.get('confirmPassword')
        is_admin = 'isAdmin' in data

        if not first_name or not last_name or not username or not password or not confirm_password:
            return jsonify({'error': 'All fields are required'}), 400

        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400

        if store.get_user_by_username(username):
            return jsonify({'error': 'Username already exists'}), 400
        
        role = "Admin" if is_admin else "Basic User"
        user = store.create_account(first_name, last_name, username, password, role)
        if user:
            return redirect(url_for('login_view'))
        else:
            return jsonify({'error': 'User ID already exists'}), 400
    return render_template('register.html')

@app.route('/login_view')
def login_view():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data['username']
        password = data['password']
        user = store.get_user_by_username(username)
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('/'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/users', methods=['GET'])
def view_users():
    users = Users.query.all()
    return render_template('users.html', users=[user.as_dict() for user in users])

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = store.get_user_by_id(user_id)
    if request.method == 'POST':
        amount = float(request.form['amount'])
        
        if amount > 0:
            user.deposit(amount)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return render_template('deposit.html', error='Invalid deposit amount')
    return render_template('deposit.html')

@app.route('/store_view', methods=['GET'])
def view_store():
    games = get_games()
    return render_template('store.html', games=games)

@app.route('/library', methods=['GET'])
def view_library():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = store.get_user_by_id(user_id)
    return render_template('library.html', purchase_history=user.purchase_history)

@app.route('/buy', methods=['GET', 'POST'])
def buy_game():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = store.get_user_by_id(user_id)
    if request.method == 'POST':
        game_id = int(request.form['game_id'])
        
        game = Game.query.get(game_id)
        if game:
            if user.balance >= game.price and game.stock > 0:
                user.withdraw(game.price)
                game.stock -= 1
                user.add_purchase(game.title)
                db.session.commit()
                return redirect(url_for('view_library'))
            else:
                return render_template('buy.html', error='Insufficient balance or game out of stock')
        else:
            return render_template('buy.html', error='Game not found')
    games = Game.query.all()
    return render_template('buy.html', games=games)

@app.route('/gift', methods=['GET', 'POST'])
def send_gift():
    sender_id = session.get('user_id')
    if not sender_id:
        return redirect(url_for('login'))
    
    sender = store.get_user_by_id(sender_id)
    if request.method == 'POST':
        receiver_username = request.form['receiver_username']
        game_id = int(request.form['game_id'])
        
        receiver = store.get_user_by_username(receiver_username)
        game = Game.query.get(game_id)
        
        if receiver and game:
            if sender.balance >= game.price and game.stock > 0:
                sender.withdraw(game.price)
                game.stock -= 1
                receiver.add_purchase(game.title)
                db.session.commit()
                return redirect(url_for('view_library'))
            else:
                return render_template('gift.html', error='Insufficient balance or game out of stock')
        else:
            return render_template('gift.html', error='Receiver or game not found')
    games = Game.query.all()
    return render_template('gift.html', games=games)

if __name__ == '__main__':
    store = GamingStore()
    initialize_database()
    log_file = open('debug.log', 'w')
    app.run(debug=True)
