import requests
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import requests
import csv
import os

import google.generativeai as genai
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Get API keys from environment
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# genai.configure(api_key=f"{GEMINI_API_KEY}")
# for model in genai.list_models():
#     print(f"Model Name: {model.name}")
#     print(f"Supported Methods: {model.supported_generation_methods}\n")




# Configure API Key
# genai.configure(api_key="YOUR_API_KEY")  # Replace with your key

# # Initialize the model
# model = genai.GenerativeModel('gemini-pro')

# # Send a prompt
# response = model.generate_content("Write a Danish greeting.")
# print(response.text)
# Test DeepSeek
def test_deepseek():
    DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_API_KEY = "sk-83fefc05fa134b6bad5c48813067e48f"  # Get it from https://platform.deepseek.com/
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",  # Optional (default)
        "messages": [{"role": "user", "content": "Write a Danish poem about AI."}]
    }

    response = requests.post(DEEPSEEK_URL, headers=headers, json=payload)
    print(response.json())

# Test Gemini
def test_gemini():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": "Skriv en dansk hilsen."}]}]
    }
    response = requests.post(url, headers=headers, json=payload)
    print("Gemini Response:", response.json())

if __name__ == "__main__":
    test_deepseek()  # Uncomment to test
    # test_gemini()   # Uncomment to test