import os
from dotenv import load_dotenv

load_dotenv('.env')

db_name = os.getenv('DB_NAME')
db_password = os.getenv('DB_PASSWORD')
db_user = os.getenv('DB_USER')
db_host = os.getenv('DB_HOST')
token_tg = os.getenv('TELEGRAM_TOKEN')
api_codeforces = os.getenv('API_CODEFORCES')
