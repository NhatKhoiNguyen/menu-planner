import jwt
import datetime
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("MONGO_URI")

def generate_token(user_id, expires_in=3600):
    payload = {
        "user_id": str(user_id),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print(">>> Token payload:", payload)
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return None  # Token hết hạn
    except jwt.InvalidTokenError:
        return None  # Token không hợp lệ
    except Exception as e:
        print(">>> Token verification failed:", e)
        return None
