from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin):
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = datetime.utcnow()
        self.last_login = datetime.utcnow()
        self.scan_history = []

    @staticmethod
    def create(username, email, password):
        """Create a new user instance with hashed password"""
        password_hash = generate_password_hash(password)
        # In a real application, you would get the ID from the database
        # For this example, we'll use a simple incrementing number
        id = len(users) + 1
        user = User(id, username, email, password_hash)
        users.append(user)
        return user

    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)

    def add_scan(self, filename, result):
        """Add a scan result to user's history"""
        scan = {
            'filename': filename,
            'timestamp': datetime.utcnow(),
            'result': result
        }
        self.scan_history.append(scan)

    def get_id(self):
        """Required for Flask-Login"""
        return str(self.id)

# In-memory storage for users (in a real app, this would be a database)
users = []

def get_user_by_id(user_id):
    """Retrieve a user by ID"""
    try:
        user_id = int(user_id)
        for user in users:
            if user.id == user_id:
                return user
    except ValueError:
        return None
    return None

def get_user_by_email(email):
    """Retrieve a user by email"""
    for user in users:
        if user.email == email:
            return user
    return None
