import sys
from dotenv import load_dotenv
import os

import logging

# Suppress Python bytecode creation (.pyc files)
sys.dont_write_bytecode = True

load_dotenv()

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
