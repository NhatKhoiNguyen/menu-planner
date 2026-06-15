from flask import request, jsonify, current_app
from functools import wraps
from app.utils.token_utils import verify_token
from bson import ObjectId

def get_current_user_from_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, jsonify({"error": "Token thiếu hoặc sai định dạng"}), 401

    token = auth_header.split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        return None, jsonify({"error": "Token hết hạn hoặc không hợp lệ"}), 401

    user = current_app.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None, jsonify({"error": "Người dùng không tồn tại!"}), 401

    return user, None, None
    
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user, error_response, status = get_current_user_from_token()
        if error_response:
            return error_response, status

        return f(current_user=user, *args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user, error_response, status = get_current_user_from_token()
        if error_response:
            return error_response, status

        if not user.get("is_admin", False):
            return jsonify({"error": "Bạn không có quyền quản trị"}), 403

        return f(current_user=user, *args, **kwargs)
    return decorated_function
