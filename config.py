import os
import sys

FILE_PATH = os.path.abspath(__file__)
FILE_DIR = os.path.dirname(FILE_PATH)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

LOGS_DIR = os.path.join(ROOT_DIR, "logs")
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR, exist_ok=True)

import dotenv
dotenv.load_dotenv(override=True)

## Environment variables
PYTHONPATH = os.getenv("PYTHONPATH", FILE_DIR)
os.environ["PYTHONPATH"] = PYTHONPATH

# OpenAI API Project Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORG_NAME = os.getenv("OPENAI_ORG_NAME")
OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID")
OPENAI_PROJECT_ID = os.getenv("OPENAI_PROJECT_ID")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

# Bearer Token
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
DEFAULT_HEADER = {"Authorization": f"Bearer {BEARER_TOKEN}"}

## Global variables

# OpenAI Models
DEFAULT_MODEL = "gpt-4o"
