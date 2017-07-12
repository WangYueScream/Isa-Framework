from isafk.view import Blueprint
from .urls import url_maps


user_print = Blueprint('index', url_maps)
