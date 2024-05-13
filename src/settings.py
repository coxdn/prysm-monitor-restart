import os
from dotenv import load_dotenv

load_dotenv()

working_directory = os.getenv('GETH_DIR', r'C:\Node')
