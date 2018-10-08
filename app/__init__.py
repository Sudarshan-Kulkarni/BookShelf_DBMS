from flask import Flask

app = Flask(__name__)

from app import queries

from app import routes