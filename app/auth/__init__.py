from flask import Blueprint

#  if you don't understand what this is doing, don't touch it...
bp = Blueprint('auth', __name__)

from app.auth import routes
