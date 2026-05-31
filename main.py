import os
from dotenv import load_dotenv

# Load key-value pairs from the .env file into the environment
load_dotenv()

# Retrieve the variables
api_key = os.getenv("API_KEY")

print(f"API Key: {api_key}")