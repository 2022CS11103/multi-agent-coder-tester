"""
config.py
---------
Central settings for the Multi-Agent Coder/Tester project.
"""

import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "3"))
SANDBOX_IMAGE = os.getenv("SANDBOX_IMAGE", "python:3.11-slim")
EXECUTION_TIMEOUT = int(os.getenv("EXECUTION_TIMEOUT", "15"))

GENERATED_DIR = "generated"
