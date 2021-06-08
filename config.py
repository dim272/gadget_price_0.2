import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

e_db = os.getenv('e_db')
p_db = os.getenv('p_db')
s_db = os.getenv('s_db')
proxy = os.getenv('proxy')

user = os.getenv('u')
pwd = os.getenv('p')
host = os.getenv('h')

email = os.getenv('email_from')
email_to = os.getenv('email_to')
email_pwd = os.getenv('email_pwd')
email_host = os.getenv('email_host')
