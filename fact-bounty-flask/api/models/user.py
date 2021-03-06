from datetime import datetime, timedelta

from flask import current_app
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
# from passlib.apps import custom_app_context as pwd_context
import jwt


from ...app import db

auth = HTTPBasicAuth()


class User(db.Model):
    """
    This model holds information about a user registered
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    date = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, name, email, password):
        """
        Initializes the user instance
        """
        self.name = name
        self.email = email
        self.password = Bcrypt().generate_password_hash(password).decode()

    def __repr__(self):
        """
        Returns the object reprensentation
        """
        return '<User %r>' % self.name

    def generate_auth_token(self, expiration, user_id):
        """
        Generate authorization token

        """
        try:
            # set up a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(seconds=expiration),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            # create the byte string token using the payload and the SECRET key
            jwt_string = jwt.encode(
                payload,
                current_app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
            return jwt_string

        except Exception as e:
            # return an error in string format if an exception occurs
            return str(e)


    def to_json(self):
        """
        Returns a JSON object

        :return: user JSON object
        """
        user_json = {
            'name': self.name,
            'password': self.password,
            'email': self.email,
            'date': self.date
        }
        return user_json

    @staticmethod
    def verify_auth_token(token):
        """
        Verification of authorization token

        :param token: token for verification
        """
        try:
            # try to decode the token using our SECRET variable
            payload = jwt.decode(token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return "Invalid token. Please register or login"

    def verify_password(self, password):
        """
        Verify the password

        :param password: password for verification
        """
        return Bcrypt().check_password_hash(self.password, password)

    def save(self):
        """
        Save a user to the database.
        This includes creating a new user and editing one.
        """
        db.session.add(self)
        db.session.commit()