from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship
from sqlalchemy import Integer, String, Text, ForeignKey, create_engine, select, inspect
from werkzeug.security import check_password_hash, generate_password_hash
import os
import termcolor
from datetime import datetime, timedelta
import random
import threading
import socket
import argparse
import sys
import time

COLORS = {
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'reset': '\033[0m'
}

# List of colors that can be assigned to users (excluding 'reset')
USER_COLOR_NAMES = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']

# Function to color text
def colored(text, color_name):
    """Return colored text using ANSI color codes."""
    if color_name in COLORS:
        return f"{COLORS[color_name]}{text}{COLORS['reset']}"
    return text  # If color not found, return plain text

