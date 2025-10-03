"""FastAPI application for serving educational analytics data from Google Sheets."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import gspread

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
    """Create and return a Google Sheets worksheet connection.
    
    Args:
        workbook_id: ID of the Google Sheets workbook
        worksheet_name: Name of the worksheet to access
        
    Returns:
        A Google Sheets worksheet object
    """
    gc = gspread.service_account_from_dict(json_credentials)
    sh = gc.open_by_key(workbook_id)
    worksheet = sh.worksheet(worksheet_name)
    return worksheet

# Get principal data
@app.get("/home")
async def get_home():
    """Get general description data from the home worksheet.
    
    Returns:
        dict: A dictionary mapping section names to their text content
    """
    worksheet = make_credentials(worksheet_name='descripcion_general')
    records = worksheet.get_all_records()
    response = {record['seccion']: record['texto'] for record in records}
    return response

# Get projects
@app.get("/projects")
async def get_projects():
    """Get all visible projects sorted by order.
    
    Returns:
        list: A list of project records, filtered to show only visible projects with IDs
    """
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
    """Get a specific project by its ID.
    
    Args:
        project_id (int): The ID of the project to retrieve
        
    Returns:
        dict: Project record if found, empty dict if not found
    """
    worksheet = make_credentials()
    records = worksheet.get_all_records()
    for record in records:
        if record['id'] == project_id:
            return record
    return {}

# Get project by slug
@app.get("/projects/slug/{slug}")
async def get_project_by_slug(slug: str):
    """Get a specific project by its slug.
    
    Args:
        slug (str): The slug of the project to retrieve
        
    Returns:
        dict: Project record if found, empty dict with error message if not found
    """
    worksheet = make_credentials()
    records = worksheet.get_all_records()
    
    # Buscar por slug (case insensitive para mayor flexibilidad)
    for record in records:
        if record.get('slug', '').lower() == slug.lower():
            # Asegurarse de que el registro tenga un ID
            if not record.get('id'):
                return {"error": "Project found but has no ID", "slug": slug}
            return record
    
    # Si no se encuentra por slug, intentar buscar si el slug es en realidad un ID
    try:
        project_id = int(slug)
        for record in records:
            if record.get('id') == project_id:
                return record
    except ValueError:
        pass  # El slug no es un número, continuar
    
    # No se encontró el proyecto
    return {
        "error": "Project not found",
        "slug": slug,
        "message": f"No project found with slug '{slug}'. Check that the slug exists in Google Sheets."
    }

# Debug endpoint: Get all available slugs
@app.get("/projects/slugs")
async def get_all_slugs():
    """Get all available slugs from projects.
    
    Returns:
        list: List of dictionaries with id, proyecto, and slug
    """
    worksheet = make_credentials()
    records = worksheet.get_all_records()
    
    slugs_info = []
    for record in records:
        if record.get('id'):  # Solo proyectos con ID
            slugs_info.append({
                'id': record.get('id'),
                'proyecto': record.get('proyecto', 'Sin nombre'),
                'slug': record.get('slug', ''),
                'has_slug': bool(record.get('slug', '').strip())
            })
    
    return {
        'total': len(slugs_info),
        'projects': slugs_info
    }

# Get all rows of project by ID_proyecto from worsheet detalle_proyecto filtering by ID_proyecto
@app.get("/project/{project_id}/html")
async def get_project_html(project_id: str):
    """Get HTML content for a specific project.
    
    Args:
        project_id (str): The ID of the project to get HTML content for
        
    Returns:
        dict: Dictionary containing the generated HTML content for the project
    """
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

    # CSS styles para el contenido
    css_styles = """
    <style>
        /* Estilos generales */
        body {
            font-family: 'Merriweather', 'Helvetica Neue', Arial, sans-serif;
            color: #565656;
            line-height: 1.6;
        }
        
        /* Títulos */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Merriweather Sans', 'Helvetica Neue', Arial, sans-serif;
            font-weight: 700;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            color: #333;
        }
        
        h1 { font-size: 2.5rem; }
        h2 { font-size: 2rem; }
        h3 { font-size: 1.75rem; }
        h4 { font-size: 1.5rem; }
        h5 { font-size: 1.25rem; }
        h6 { font-size: 1rem; }
        
        /* Párrafos */
        p {
            margin-bottom: 1rem;
            font-size: 1rem;
        }
        
        /* Enlaces */
        a {
            color: #f4623a;
            text-decoration: none;
            transition: color 0.3s;
        }
        
        a:hover {
            color: #d14521;
            text-decoration: underline;
        }
        
        /* Imágenes */
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1.5rem auto;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        /* Líneas divisoras */
        hr {
            margin: 2rem 0;
            border: 0;
            border-top: 3px solid #f4623a;
            opacity: 0.3;
        }
        
        /* iframes */
        iframe {
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin: 1.5rem 0;
        }
        
        /* Utilidades de texto */
        .text-center { text-align: center; }
        .text-start { text-align: left; }
        .text-end { text-align: right; }
        
        /* Márgenes */
        .mt-0 { margin-top: 0; }
        .my-3 { margin-top: 1rem; margin-bottom: 1rem; }
        .mx-auto { margin-left: auto; margin-right: auto; }
        
        /* Responsive */
        @media (max-width: 768px) {
            h1 { font-size: 2rem; }
            h2 { font-size: 1.75rem; }
            h3 { font-size: 1.5rem; }
            iframe { height: 400px !important; }
        }
    </style>
    """

    html = css_styles
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
            case 'CSS':
                # Permite agregar CSS personalizado desde Google Sheets
                html += f"<style>{row['texto']}</style>"
            case _:
                html += f"<p>{row['texto']}</p>"


    return {'html': html}
