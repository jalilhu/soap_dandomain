# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env
DANDOMAIN_WSDL = os.getenv("DANDOMAIN_WSDL")
DANDOMAIN_USER = os.getenv("DANDOMAIN_USERNAME")
DANDOMAIN_PASS = os.getenv("DANDOMAIN_PASSWORD")
DANDOMAIN_LANGUAGE = os.getenv("DANDOMAIN_LANGUAGE", "DK")
