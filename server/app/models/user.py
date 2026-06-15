from bson import ObjectId

class User:
    def __init__(self, data):
        self.id = str(data.get("_id", ""))
        self.username = data.get("username", "")
        self.email = data.get("email", "")
        self.password = data.get("password", "")
        self.is_admin = data.get("is_admin", False)
        
    def to_dict(self):
        return {
            "_id": self.id,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "is_admin": self.is_admin
        }
