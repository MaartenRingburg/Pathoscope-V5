# backend/modules/auth.py
import firebase_admin
from firebase_admin import credentials, auth as fb_auth
from flask import session, redirect, url_for

def init_firebase(app):
    cred_path = app.config['FIREBASE_CRED_PATH']
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

# Simple decorator for protected routes
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('serve_react'))
        return f(*args, **kwargs)
    return decorated