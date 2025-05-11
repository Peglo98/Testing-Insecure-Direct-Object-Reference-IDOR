import datetime
import jwt
from flask import current_app, request, abort, g
from functools import wraps
from models import User
from werkzeug.security import check_password_hash, generate_password_hash

def hash_password(password):
    return generate_password_hash(password)

def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        payload = {
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        return token
    return None

def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            abort(401)
        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            abort(401)
        token = parts[1]
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.PyJWTError:
            abort(401)
        user = User.query.get(payload['user_id'])
        if not user:
            abort(401)
        g.current_user = user
        return func(*args, **kwargs)
    return wrapper
