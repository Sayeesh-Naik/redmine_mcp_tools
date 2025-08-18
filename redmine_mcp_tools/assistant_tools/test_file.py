import os
from dotenv import load_dotenv

# Load .env from your app directory
env_path = os.path.join(
    os.path.dirname(__file__),  # assistant_tools/
    "..",                       # up to redmine_mcp_tools/
    ".env"
)
env_path = os.path.abspath(env_path)
load_dotenv(dotenv_path=env_path)

# Now read values
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
USER_EMAIL = os.getenv("USER_EMAIL")
USER_NAME = os.getenv("USER_NAME")

print("URL:", API_URL)
print("Key:", API_KEY)
print("Email:", USER_EMAIL)
print("Name:", USER_NAME)
