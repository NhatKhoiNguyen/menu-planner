from flask import Blueprint, request, jsonify, current_app
from app.models.user import User
from app.utils.password_utils import hash_password, check_password
from app.utils.auth_decorator import login_required
from bson import ObjectId
from app.utils.token_utils import generate_token
from functools import wraps
from itsdangerous import URLSafeTimedSerializer
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

load_dotenv()

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    is_admin = data.get("is_admin", False)

    if not username or not email or not password:
        return jsonify({"error": "Thiếu thông tin!"}), 400

    existing_user = current_app.db.users.find_one({"email": email})
    if existing_user:
        return jsonify({"error": "Email đã tồn tại!"}), 409

    hashed_pw = hash_password(password)
    user = {
        "username": username,
        "email": email,
        "password": hashed_pw,
        "is_admin": is_admin,
    }

    inserted = current_app.db.users.insert_one(user)
    user["_id"] = str(inserted.inserted_id)
    del user["password"]  # Không trả về password
    return jsonify(user), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Thiếu thông tin đăng nhập"}), 400

    user = current_app.db.users.find_one({"email": email})
    if not user:
        return jsonify({"error": "Email không tồn tại"}), 404

    if not check_password(password, user["password"]):
        return jsonify({"error": "Sai mật khẩu"}), 401

    user_obj = User(user)
    user_dict = user_obj.to_dict()
    user_dict["_id"] = str(user["_id"])
    del user_dict["password"]

    token = generate_token(user["_id"])
    return jsonify({
        "user": user_dict,
        "token": token
    }), 200


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user(current_user):
    return jsonify({
        "_id": str(current_user["_id"]),
        "username": current_user["username"],
        "email": current_user["email"],
        "is_admin": current_user.get("is_admin", False),
        "role": "admin" if current_user.get("is_admin", False) else "user"
    })


def get_serializer():
    return URLSafeTimedSerializer("SECRET_KEY")

def create_reset_token(user_id):
    return get_serializer().dumps(user_id, salt="reset-password")

def verify_reset_token(token, max_age=600):
    try:
        return get_serializer().loads(token, salt="reset-password", max_age=max_age)
    except:
        return None

# def send_email(to_email, subject, body):
#     msg = MIMEMultipart()
#     msg["Subject"] = subject
#     msg["From"] = os.getenv("EMAIL_APP")
#     msg["To"] = to_email
#     msg.attach(MIMEText(body, 'html'))

#     server = smtplib.SMTP(os.getenv("EMAIL_SMTP_SERVER"), int(os.getenv("EMAIL_SMTP_PORT")))
#     server.starttls()
#     server.login(os.getenv("EMAIL_APP"), os.getenv("EMAIL_APP_PASSWORD"))
#     server.sendmail(msg["From"], to_email, msg.as_string())
#     server.quit()

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = os.getenv("EMAIL_APP")
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    # Gmail SMTP
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.getenv("EMAIL_APP"), os.getenv("GENERATED_APP_PASSWORD"))
        server.sendmail(msg["From"], to_email, msg.as_string())

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")
    user = current_app.db.users.find_one({"email": email})
    if not user:
        return jsonify({"message": "Không tìm thấy người dùng."}), 404

    token = create_reset_token(str(user["_id"])) 
    reset_link = f"{os.getenv('FRONTEND_URL')}/reset-password/{token}" 

    send_email(
        to_email=email,
        subject="Đặt lại mật khẩu của bạn",
        body=f"Nhấn vào liên kết sau để đặt lại mật khẩu: {reset_link}"
    )

    return jsonify({"message": "Liên kết đặt lại đã được gửi qua email."}), 200

@auth_bp.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    data = request.get_json()
    new_password = data.get("password")

    user_id = verify_reset_token(token)
    if not user_id:
        return jsonify({"message": "Token không hợp lệ hoặc đã hết hạn"}), 400

    hashed_pw = hash_password(new_password)
    current_app.db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password": hashed_pw}}
    )

    return jsonify({"message": "Mật khẩu đã được cập nhật."}), 200
