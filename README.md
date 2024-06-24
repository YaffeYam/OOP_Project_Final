# Gaming Store Application
## Overview
This project implements a gaming store application that allows users to
* Create accounts
* Deposit money
* Purchase games
* View their purchase history
* More TBA.

## Features
* User Account Management: Create, login, delete, and manage user accounts.
* Admin User Management: Admins can manage games, view all users, and perform administrative actions.
* Game Store: View available games, purchase games, and manage game inventory.
* Logging: Real-time logging with timestamped messages.
* Admin users have additional functionalities such as adding or removing games from the store and managing user accounts.

## Installation
To run this application, ensure you have Python installed. Then, follow these steps:
pip install -r requirements.txt

## Usage
### Creating an Account
### Users can create an account by selecting the REGISTER option from the main menu. Admins can also be created during the registration process.

## Logging In
### Users can log in by selecting the LOGIN option and providing their username and password.

## Admin Actions
* After logging in as an admin, the following actions are available:
    * View all users
    * Add a new game to the store
    * Remove a game from the store
    * Change game stock quantity
    * Change game price
    * User Actions

* After logging in as a user, the following actions are available:
    * View the game store
    * Purchase a game
    * View purchased games (library)
    * View purchase history
    * Send a game as a gift to another user
    * Deposit money into the account
    * Check account balance
    * Delete account
    * Game Store Management
    * Admins can manage the game store by adding new games, removing games, and updating game prices and stock quantities.

* Code Structure
    * Client class: Represents a user with methods for managing user information and transactions.
    * AdminUser class: Inherits from Client and includes admin-specific functionalities.
    * Game class: Represents a game in the store with attributes for title, price, and stock.
    * GamingStore class: Manages the store's clients and games, handles user and admin actions, and provides a menu-driven interface.
    * Logging
    * Logging is configured to write to debug.log with real-time updates. The custom_output function is used to format log messages with timestamps.