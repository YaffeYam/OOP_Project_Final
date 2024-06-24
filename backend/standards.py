from enum import Enum, auto

class StoreActions(Enum):
    LOGIN = auto()
    REGISTER = auto()
    ADD_GAME = auto()  # Added for CRUD operations
    REMOVE_GAME = auto()  # Added for CRUD operations
    UPDATE_GAME = auto()  # Added for CRUD operations
    EXIT = auto()

class UserActions(Enum):
    VIEW_STORE = auto()
    VIEW_LIBRARY = auto()
    BUY_GAME = auto()
    PURCHASE_HISTORY = auto()
    SEND_GIFT = auto()
    DEPOSIT = auto()
    CHECK_BALANCE = auto()
    USER_LOGOUT = auto()
    EXIT = auto()
    DELETE_ACCOUNT = auto()

class AdminActions(Enum):
    VIEW_STORE = auto()
    VIEW_USERS = auto()
    ADD_GAME = auto()
    REMOVE_GAME = auto()
    CHANGE_STOCK = auto()
    CHANGE_PRICE = auto()
    USER_LOGOUT = auto()
    EXIT = auto()
