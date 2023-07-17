from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import gspread
import os

# Create FastAPI instance
app = FastAPI(title='Datos Analitica Eductiva API')

# CORS
origins = [
    "http://localhost",
    "http://localhost:8080",
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load .env
load_dotenv()

# Load GCM credentials from .env to json object
json_credentials = {
    "type": os.getenv('TYPE'),
    "project_id": os.getenv('PROJECT_ID'),
    "private_key_id": os.getenv('PRIVATE_KEY_ID'),
    "private_key": os.getenv('PRIVATE_KEY'),
    "client_email": os.getenv('CLIENT_EMAIL'),
    "client_id": os.getenv('CLIENT_ID'),
    "auth_uri": os.getenv('AUTH_URI'),
    "token_uri": os.getenv('TOKEN_URI'),
    "auth_provider_x509_cert_url": os.getenv('AUTH_PROVIDER_X509_CERT_URL'),
    "client_x509_cert_url": os.getenv('CLIENT_X509_CERT_URL'),
    "universe_domain": os.getenv('UNIVERSE_DOMAIN'),
}

SHEET_ID = os.getenv('SHEET_ID')
PROJECT_SHEET_NAME = os.getenv('PROJECT_SHEET_NAME')

print(json_credentials)

# Get projects
@app.get("/dae/projects")
async def get_projects():
    gc = gspread.service_account_from_dict(json_credentials)
    sh = gc.open_by_key(SHEET_ID)
    worksheet = sh.worksheet(PROJECT_SHEET_NAME)
    records = worksheet.get_all_records()
    return records
