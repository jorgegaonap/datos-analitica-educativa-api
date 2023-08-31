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

WORKBOOK_ID = os.getenv('WORKBOOK_ID')
WORKSHEET_NAME = os.getenv('WORKSHEET_NAME')

def make_credentials(workbook_id = WORKBOOK_ID, worksheet_name = WORKSHEET_NAME):
    gc = gspread.service_account_from_dict(json_credentials)
    sh = gc.open_by_key(workbook_id)
    worksheet = sh.worksheet(worksheet_name)
    return worksheet

# Get projects
@app.get("/projects")
async def get_projects():
    worksheet = make_credentials()
    records = worksheet.get_all_records()
    # Order by column orden
    records.sort(key=lambda x: x['orden'])

    # Show only column visible has'n value 'no'
    records = list(filter(lambda x: x['visible'] != 'no', records))

    # Show only column id has value
    records = list(filter(lambda x: x['id'], records))
    return records

# Get project by id
@app.get("/projects/{project_id}")
async def get_project(project_id: int):
    worksheet = make_credentials()
    records = worksheet.get_all_records()
    for record in records:
        if record['id'] == project_id:
            return record
    return {}

# Get all rows of project by ID_proyecto from worsheet detalle_proyecto filtering by ID_proyecto
@app.get("/project/{project_id}/html")
async def get_project_html(project_id: str):
    worksheet = make_credentials(worksheet_name='detalle_proyecto')
    records = worksheet.get_all_records()
    rows = []
    for record in records:
        if record['ID_proyecto'] == project_id:
            # Show only column nivel_texto has value and column visibilidad has'n value 'no'
            if record['nivel_texto'] and record['visibilidad'] != 'no':
                rows.append(record)
                # Order by column orden
                rows.sort(key=lambda x: x['orden'])
    
    html = ''
    for row in rows:
        nivel_texto = row['nivel_texto'].strip().upper()

        # Case of nivel_texto
        match nivel_texto:
            case 'H1' | 'H1_CENTRO':
                html += f"<h1 class='text-center mt-0'>{row['texto']}</h1>"
            case 'H1_IZQUIERDA':
                html += f"<h1 class='text-start mt-0'>{row['texto']}</h1>"
            case 'H1_DERECHA':
                html += f"<h1 class='text-end mt-0'>{row['texto']}</h1>"
            case 'H2' | 'H2_CENTRO':
                html += f"<h2 class='text-center mt-0'>{row['texto']}</h2>"
            case 'H2_IZQUIERDA':
                html += f"<h2 class='text-start mt-0'>{row['texto']}</h2>"
            case 'H2_DERECHA':
                html += f"<h2 class='text-end mt-0'>{row['texto']}</h2>"
            case 'H3' | 'H3_CENTRO':
                html += f"<h3 class='text-center mt-0'>{row['texto']}</h3>"
            case 'H3_IZQUIERDA':
                html += f"<h3 class='text-start mt-0'>{row['texto']}</h3>"
            case 'H3_DERECHA':
                html += f"<h3 class='text-end mt-0'>{row['texto']}</h3>"
            case 'H4' | 'H4_CENTRO':
                html += f"<h4 class='text-center mt-0'>{row['texto']}</h4>"
            case 'H4_IZQUIERDA':
                html += f"<h4 class='text-start mt-0'>{row['texto']}</h4>"
            case 'H4_DERECHA':
                html += f"<h4 class='text-end mt-0'>{row['texto']}</h4>"
            case 'H5' | 'H5_CENTRO':
                html += f"<h5 class='text-center mt-0'>{row['texto']}</h5>"
            case 'H5_IZQUIERDA':
                html += f"<h5 class='text-start mt-0'>{row['texto']}</h5>"
            case 'H5_DERECHA':
                html += f"<h5 class='text-end mt-0'>{row['texto']}</h5>"
            case 'H6' | 'H6_CENTRO':
                html += f"<h6 class='text-center mt-0'>{row['texto']}</h6>"
            case 'H6_IZQUIERDA':
                html += f"<h6 class='text-start mt-0'>{row['texto']}</h6>"
            case 'H6_DERECHA':
                html += f"<h6 class='text-end mt-0'>{row['texto']}</h6>"
            case 'P':
                html += f"<p>{row['texto']}</p>"
            case 'IMG':
                html += f"<img class='img-fluid mx-auto' src='{row['texto']}' alt='{row['texto']}' />"
            case 'A':
                html += f"<a href='{row['texto']}' target='_blank' class='text-center'>{row['texto']}</a>"
            case 'BR':
                html += "<br />"
            case 'HR':
                html += "<hr class='divider' />"
            case 'IFRAME_LINK':
                html += f"<iframe width='100%' height='600px' class='text-center my-3' src='{row['texto']}' frameborder='0' allowfullscreen></iframe>"
            case 'HTML_RAW':
                html += f"<span class='my-3'>{row['texto']}</span>"
            case _:
                html += f"<p>{row['texto']}</p>"
    



        # If of nivel_texto
        # if nivel_texto == 'H1':
        #     html += f"<h1 class='text-center mt-0'>{row['texto']}</h1>"
        
        # if nivel_texto == 'H2':
        #     html += f"<h2 class='text-center mt-0'>{row['texto']}</h2>"

        # if nivel_texto == 'H3':
        #     html += f"<h3 class='text-center mt-0'>{row['texto']}</h3>"

        # if nivel_texto == 'H4':
        #     html += f"<h4 class='text-center mt-0'>{row['texto']}</h4>"

        # if nivel_texto == 'H5':
        #     html += f"<h5 class='text-center mt-0'>{row['texto']}</h5>"
        
        # if nivel_texto == 'H6':
        #     html += f"<h6 class='text-center mt-0'>{row['texto']}</h6>"

        # if nivel_texto == 'P':
        #     html += f"<p>{row['texto']}</p>"

        # if nivel_texto == 'IMG':
        #     html += f"<img class='img-fluid mx-auto' src='{row['texto']}' alt='{row['texto']}' />"
        
        # if nivel_texto == 'A':
        #     html += f"<a href='{row['texto']}' target='_blank' class='text-center'>{row['texto']}</a>"

        # if nivel_texto == 'BR':
        #     html += "<br />"

        # if nivel_texto == 'HR':
        #     html += "<hr class='divider' />"

        # if nivel_texto == 'IFRAME_LINK':
        #     html += f"<iframe width='100%' height='600px' class='text-center' src='{row['texto']}' frameborder='0' allowfullscreen></iframe>"

        # if nivel_texto == 'HTML_RAW':
        #     html += f"{row['texto']}"

    return {'html': html}
        
