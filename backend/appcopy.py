"""
Online games steore (OOP)
"""

from datetime import datetime
import json
import sys
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from icecream import ic
from standards import StoreActions, UserActions, AdminActions

DEBUG = True

db = SQLAlchemy()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    # print("User Created!")
    # Constructor Method - Builds the object

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)

    def __init__(self, user_id, first_name, last_name, username, password, role):
        """Initialize a new user."""
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.password = generate_password_hash(password)
        self._balance = 0
        self._purchase_history = []
        self.role = role

    def __repr__(self):
        return f'<User (ID = {self.user_id}, Name={self.first_name} {self.last_name})>'

    def as_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'stock': self.stock
        }

    def __str__(self) -> str:
        return json.dumps({
            "User ID": self.user_id,
            'First Name': self.first_name,
            'Last Name': self.last_name,
            'Username': self.username,
            'Balance': self._balance,
            'Purchase History': self._purchase_history
        })

    def basic_user(self):
        print(f"User ID: {self.user_id}, First Name: {self.first_name} Is A Basic User")

    def reset_password(self, new_password):
        """Reset the user's password."""
        self.password = new_password

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
        # purchase_date = datetime.now().strftime("%d-%m-%Y %H:%M")
        self._purchase_history.append(("Title: " ,game_title))

    @property
    def balance(self):
        return self._balance

    @property
    def purchase_history(self):
        return self._purchase_history


# Creating an ADMIN USER class that inherits information from the Users class
# class AdminUser(Users):
#     """
#     Creating an Admin user class that inherits from the Users class
#     """

#     def user_is_admin(self):
#         print(f"User ID: {self.user_id}, First Name: {self.first_name} Is an Admin")

#     def __str__(self) -> str:
#         return json.dumps({
#             "User ID": self.user_id,
#             'First Name': self.first_name,
#             'Last Name': self.last_name,
#             'Username': self.username,
#             'Balance': self._balance,
#             'Admin': True
#         })
    
#     def __init__(self, user_id, first_name, last_name, username, password):
#         super().__init__(user_id, first_name, last_name, username, password)

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

    def check_duplicate(self, user_id):
        """Check if a user ID already exists."""
        return any(user.user_id == user_id for user in self.users)

    def create_account(self, user_id, first_name, last_name, username, password, role="Basic User"): # is_admin=False,
        """Create a new user or admin account."""
        if self.check_duplicate(user_id):
            print(f"User ID {user_id} already exists.")
            return
        user = Users(user_id, first_name, last_name, username, password, role)
        self.users.append(user)
        add_entry_to_database(user)
        # print(f"Account Created! ID: {user.user_id}, Name: {user.first_name} {user.last_name}")
        ic("User Created!", user_id)
        return user

    def get_user_by_id(self, user_id):
        """Retrieve a user by their user ID."""
        return next((user for user in self.users if str(user.user_id) == str(user_id)), None)

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

        print("Users: ")
        for user in self.users:
            if not user.role == "Admnin":
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
        """
        View all registered users.
        """
        print("All Registered Users:")
        with app.app_context():
            users = Users.query.all()
            for user in users:
                print(f'{user.id}: Name: {user.first_name} {user.last_name} (Usernamee: {user.username})')

    def user_withdrawal(self):
        """
        Withdraw an amount from a user's account.
        """
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
        """
        Display all games in the store.
        """
        result = get_games()
        if result == None:
            print ("OOPS, No games found :(")
        else:
            print (result)

    def view_library(self, user):
        """Display the games in the user's library (purchased games)."""
        if not user.purchase_history:
            print("You have no games in your library.")
        else:
            print("Your Library:")
            for game_title in user.purchase_history:
                print("Title: ", game_title)

    def add_game(self):
        """
        Add a new game to the store's inventory.
        """
        title = input("Enter game title: ")
        price = float(input("Enter game price: "))
        stock = int(input("Enter game stock: "))
        game = Game(title, price, stock)
        self.games.append(game)
        add_entry_to_database(game)
        print ("Game", title, "added the inventory")

    def remove_game(self):
        """Remove a game from the store's inventory."""
        self.view_store()
        title = input("Enter the title of the game to remove: ")
        for game in self.games:
            if game.title == title:
                confirmation = input(f"Are you sure you want to delete the game '{title}'? (y/n): ")
                if confirmation.lower() == 'y':
                    self.games.remove(game)
                    print(f"The game '{title}' has been successfully deleted.")
                    return
                else:
                    print("Deletion cancelled.")
        print("Game not found.")

    def change_game_price(self):
        """Change the price of a game."""
        self.view_store()
        title = input("Enter the title of the game to change the price: ")
        for game in self.games:
            if game.title == title:
                new_price = float(input("Enter the new price: "))
                game.price = new_price
                print(f"Game '{title}' price updated to ${new_price}.")
                return
        print("Game not found.")

    def change_game_stock(self):
        """Change the stock quantity of a game."""
        self.view_store()
        title = input("Enter the title of the game to change the stock: ")
        for game in self.games:
            if game.title == title:
                new_stock = int(input("Enter the new stock: "))
                game.stock = new_stock
                print(f"Game '{title}' stock updated to {new_stock}.")
                return
        print("Game not found.")

    def purchase_game(self, user):
        """Allow a user to purchase a game."""
        self.view_store()
        title = input("Enter the title of the game to purchase: ")
        for game in self.games:
            if game.title == title:
                if game.stock > 0:
                    if user.balance >= game.price:
                        user.withdraw(game.price)
                        game.stock -= 1
                        user.add_purchase(game.title)
                        print(f"Game '{title}' purchased successfully.")
                    else:
                        print("Insufficient balance.")
                else:
                    print("Game is out of stock.")
                return
        print("Game not found.")

    def gift_game(self, gift_from):
        """Allow a user to gift a game to another registered user."""
        print("Accounts:")
        self.show_all_users(show_admins=False)  # Show only non-admin users

        # Get recipient account
        while True:
            gift_to_id = input("Please Insert User ID To Gift To: ")
            if str(gift_to_id) == str(gift_from.user_id):
                print("You cannot gift a game to yourself. Please choose a different user.")
            else:
                gift_to = self.get_user_by_id(gift_to_id)
                if gift_to:
                    break
                else:
                    print("Invalid user ID. Please try again.")

        # Show available games
        self.view_store()
        title = input("Enter the title of the game to gift: ")

        for game in self.games:
            if game.title == title:
                if game.stock > 0:
                    if gift_from.balance >= game.price:
                        gift_from.withdraw(game.price)
                        gift_from.add_purchase(game.title)  # Add to gifting user's purchase history
                        game.stock -= 1
                        gift_to.add_purchase(game.title)  # Add to recipient's library
                        print(f"Game '{title}' gifted successfully to {gift_to.username}.")
                    else:
                        print("Insufficient balance.")
                else:
                    print("Game is out of stock.")
                return
        print("Game not found.")

    def show_menu(self):
        """Display the main menu for the store."""
        while True:
            for action in StoreActions:
                print(f'{action.value} - {action.name}')
            try:
                selection = int(input("Please Select - "))
                return StoreActions(selection)
            except (ValueError, KeyError):
                print("Invalid selection. Please try again.")
                continue

    def show_user_menu(self):
        """Display the menu for logged-in users."""
        while True:
            for action in UserActions:
                print(f'{action.value} - {action.name}')
            try:
                selection = int(input("Please Select - "))
                return UserActions(selection)
            except (ValueError, KeyError):
                print("Invalid selection. Please try again.")
                continue

    def show_admin_menu(self):
        """Display the menu for admin users."""
        while True:
            for action in AdminActions:
                print(f'{action.value} - {action.name}')
            try:
                selection = int(input("Please Select - "))
                if selection == AdminActions.VIEW_USERS.value:
                    return AdminActions.VIEW_USERS  # Return VIEW_USERS action
                return AdminActions(selection)
            except (ValueError, KeyError):
                print("Invalid selection. Please try again.")
                continue

def user_data_gathering():
    user_id = input("User ID: ")
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    username = input("Username: ")
    password = input("Password: ")
    is_admin = input("Is the user an admin? (y/n): ").lower() == 'y'
    role = "Admin" if is_admin else "Basic User"

    return user_id, first_name, last_name, username, password, role

def test_add_users(gaming_store):
    if DEBUG:
        c1 = gaming_store.create_account(1, "Admin", "Admin", "Admin", "Admin", "Admin")
        c1.deposit(500)
        c2 = gaming_store.create_account(2, "2", "2", "2", "2")
        c2.deposit(300)
        c3 = gaming_store.create_account(3, "3", "3", "3", "3")
        c3.deposit(50)

def add_entry_to_database(entry):
    with app.app_context():    
        try:
            db.session.add(entry)
            db.session.commit()       
            print ("Entry succeeded!")
        except Exception as e:
            db.session.rollback()
            print (f"Failed to register entry:{e}")

def try_get_user (username, password):    
    with app.app_context():
        user = Users.query.filter_by(username=username).first()
        if user and user.check_password(password):
            print("User Found")
            db.session.expunge(user)
            return user
        print("User NOT Found")
        return None

@app.route('/')
def home():
    return 'Welcome to the Games Library'

# Create a game
@app.route('/games', methods=['POST'])
def create_game():
    data = request.get_json()
    new_game = Game(title=data['title'], price=data['price'], stock=data['stock'])
    db.session.add(new_game)
    db.session.commit()
    return jsonify({'message': 'Game created successfully'}), 201

# Read all games
@app.route('/games', methods=['GET'])
def get_games():
    with app.app_context():
        games = Game.query.all()
        if not games:
            return None
        result = [game.as_dict() for game in games]
        return json.dumps(jsonify(result).json)

# Update a game
@app.route('/games/<int:id>', methods=['PUT'])
def update_game(id):
    game = Game.query.get_or_404(id)
    data = request.get_json()
    game.title = data.get('title', game.title)
    game.price = data.get('price', game.price)
    game.stock = data.get('stock', game.stock)
    db.session.commit()
    return jsonify({'message': 'Game updated successfully'})

# Delete a game
@app.route('/games/<int:id>', methods=['DELETE'])
def delete_game(id):
    game = Game.query.get_or_404(id)
    db.session.delete(game)
    db.session.commit()
    return jsonify({'message': 'Game deleted successfully'})

if __name__ == '__main__':
    # he database tables
    with app.app_context():
        db.create_all()
    log_file = open('debug.log', 'w')
    ic.configureOutput(outputFunction=custom_output)
    ic("Program started")

    gaming_store = GamingStore()
    test_add_users(gaming_store)

    # app.run(debug=True)

    while True:
        user_selection = gaming_store.show_menu()

        if user_selection == StoreActions.REGISTER:
            user_data = user_data_gathering()
            gaming_store.create_account(*user_data)

        elif user_selection == StoreActions.LOGIN:
            username = input("Username: ")
            password = input("Password: ")
            user = try_get_user(username, password)
            # user = next((user for user in gaming_store.users if user.username == username and user.check_password(password)), None)
            ic()
            if user:
                print(f"Welcome {user.first_name}!")
                if user.role == "Admin":

                    while True:
                        admin_selection = gaming_store.show_admin_menu()
                        if admin_selection == AdminActions.VIEW_STORE:
                            gaming_store.view_store()

                        elif admin_selection == AdminActions.VIEW_USERS:
                            gaming_store.view_all_users()

                        elif admin_selection == AdminActions.ADD_GAME:
                            gaming_store.add_game()

                        elif admin_selection == AdminActions.REMOVE_GAME:
                            gaming_store.remove_game()

                        elif admin_selection == AdminActions.CHANGE_STOCK:
                            gaming_store.change_game_stock()

                        elif admin_selection == AdminActions.CHANGE_PRICE:
                            gaming_store.change_game_price()

                        elif admin_selection == AdminActions.USER_LOGOUT:
                            break

                        elif admin_selection == AdminActions.EXIT:
                            log_file.close()
                            print("Goodbye :)")
                            sys.exit()

                else:
                    while True:
                        user_selection = gaming_store.show_user_menu()
                        if user_selection == UserActions.VIEW_STORE:
                            gaming_store.view_store()

                        elif user_selection == UserActions.BUY_GAME:
                            gaming_store.purchase_game(user)

                        elif user_selection == UserActions.VIEW_LIBRARY:
                            gaming_store.view_library(user)

                        elif user_selection == UserActions.PURCHASE_HISTORY:
                            gaming_store.purchase_history(user)

                        elif user_selection == UserActions.SEND_GIFT:
                            gaming_store.gift_game(user)

                        elif user_selection == UserActions.DEPOSIT:
                            gaming_store.deposit_to_account(user)

                        elif user_selection == UserActions.CHECK_BALANCE:
                            gaming_store.check_balance(user)

                        elif user_selection == UserActions.USER_LOGOUT:
                            break

                        elif user_selection == UserActions.EXIT:
                            log_file.close()
                            print("Goodbye :)")
                            sys.exit()

                        elif user_selection == UserActions.DELETE_ACCOUNT:
                            if gaming_store.delete_account(user):
                                print("Logged out.")
                                break
                            else:
                                print("Account deletion failed.")

                        elif user_selection == UserActions.USER_LOGOUT:
                            break

                        elif user_selection == UserActions.EXIT:
                            log_file.close()
                            print("Goodbye :)")
                            sys.exit()

            else:
                print("Invalid username or password.")

        elif user_selection == StoreActions.EXIT:
            log_file.close()
            print("Goodbye :)")
            sys.exit()
