from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from model_utils import load_model_components, predict_new_data
from scrapper import get_player_data_from_futbin
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI()

@app.get("/api/data")
async def get_data():
    return {"mensaje": "¡Hola desde la API!"}
# ...

# --- Parte para servir el frontend ---

# Define dónde está la carpeta 'build' de tu frontend
# Asume que 'backend' y 'frontend' están al mismo nivel
FRONTEND_BUILD_DIR = Path(__file__).parent.parent / "frontend" / "build"

# Verificación
if not FRONTEND_BUILD_DIR.is_dir():
    print(f"Advertencia: La carpeta 'frontend/build' no se encontró en: {FRONTEND_BUILD_DIR}")
    print("Asegúrate de haber ejecutado 'npm run build' en tu frontend.")
    # raise Exception(...) # Podrías lanzar un error aquí si es crítico

# Monta los archivos estáticos. Cualquier solicitud a /static/ se buscará en FRONTEND_BUILD_DIR/static
# (React suele poner sus assets en /static/ dentro de la carpeta build)
app.mount("/static", StaticFiles(directory=FRONTEND_BUILD_DIR / "static"), name="static")

# Ruta "comodín": Para cualquier otra dirección, sirve el index.html de React
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_frontend(full_path: str):
    index_html_path = FRONTEND_BUILD_DIR / "index.html"
    if not index_html_path.is_file():
        print(f"Advertencia: index.html no se encontró en: {index_html_path}")
        return HTMLResponse(content="<h1>Frontend no encontrado</h1><p>Asegúrate de que index.html esté en la carpeta frontend/build.</p>", status_code=404)
    with open(index_html_path, "r") as f:
        return HTMLResponse(content=f.read())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # o ["*"] para permitir todos
    allow_methods=["*"],
    allow_headers=["*"],
)


# Cargar componentes del modelo
model_components = load_model_components("fifa_model.pkl")

# Entrada esperada
class PlayerNameRequest(BaseModel):
    player_name: str

@app.post("/predict")
def predict_from_name(request: PlayerNameRequest):
    if model_components is None:
        return {"error": "Modelo no cargado"}

    # Obtener datos del scraping
    raw_payload = get_player_data_from_futbin(request.player_name)

    if not raw_payload:
        return {"error": "No se encontraron cartas para ese jugador"}

    # Separar features y meta
    features_df = pd.DataFrame([p["features"] for p in raw_payload])
    meta_df = pd.DataFrame([p["meta"] for p in raw_payload])

    # Predecir
    predictions = predict_new_data(features_df, model_components)
   
    # Combinar todo
    full_df = predictions.merge(meta_df, on="player_id")
    full_df["predicted_price"] =  full_df["predicted_price"].astype(float).round(2)

    return full_df.to_dict(orient="records")
