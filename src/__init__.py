"""
Package principal de l'application LUMEN
"""

from .models.app import GrippeAlertApp
from .models.chatbot import GrippeChatbot
from .utils.helpers import *
from .config.settings import config

__version__ = "2.0.0"
__author__ = "Équipe LUMEN"
