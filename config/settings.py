"""
Configuración global del sistema de monitoreo de SO2 volcánico
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Rutas base
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
WIND_DIR = DATA_DIR / "wind"
RESULTS_DIR = DATA_DIR / "results"

# Crear directorios si no existen
for dir_path in [DATA_DIR, IMAGES_DIR, WIND_DIR, RESULTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Copernicus Data Space (TROPOMI)
COPERNICUS_USERNAME = os.getenv("COPERNICUS_USERNAME", "")
COPERNICUS_PASSWORD = os.getenv("COPERNICUS_PASSWORD", "")
COPERNICUS_API_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1"
COPERNICUS_TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

# ERA5 (CDS API) - Para datos de viento
CDS_API_URL = "https://cds.climate.copernicus.eu/api/v2"
CDS_API_KEY = os.getenv("CDS_API_KEY", "")

# Base de datos PostgreSQL
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "so2_monitoring"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}

# API REST
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# Volcanes predefinidos: coordenadas del cráter y altitud (m s.n.m.).
# La altitud define la ventana de búsqueda del viento (cráter a +2.000 m),
# por lo que debe estar cargada para que el cálculo sea correcto.
# Valores de referencia: Global Volcanism Program (Smithsonian) y Wikipedia;
# verificar con la fuente oficial antes de usarlos en un estudio.
VOLCANES_PREDEFINIDOS = {
    # Argentina y frontera con Chile
    "peteroa": {"lat": -35.242, "lon": -70.574, "altitud_m": 3977, "nombre": "Peteroa", "pais": "Argentina/Chile"},
    "copahue": {"lat": -37.85, "lon": -71.167, "altitud_m": 2997, "nombre": "Copahue", "pais": "Argentina/Chile"},
    "lastarria": {"lat": -25.167, "lon": -68.517, "altitud_m": 5697, "nombre": "Lastarria", "pais": "Argentina/Chile"},
    "socompa": {"lat": -24.396, "lon": -68.246, "altitud_m": 6051, "nombre": "Socompa", "pais": "Argentina/Chile"},
    "llullaillaco": {"lat": -24.720, "lon": -68.537, "altitud_m": 6723, "nombre": "Llullaillaco", "pais": "Argentina/Chile"},
    "ojos_del_salado": {"lat": -27.110, "lon": -68.541, "altitud_m": 6893, "nombre": "Ojos del Salado", "pais": "Argentina/Chile"},
    # Otros volcanes de la región andina
    "sabancaya": {"lat": -15.78, "lon": -71.85, "altitud_m": 5976, "nombre": "Sabancaya", "pais": "Perú"},
    "lascar": {"lat": -23.367, "lon": -67.733, "altitud_m": 5592, "nombre": "Láscar", "pais": "Chile"},
    "villarrica": {"lat": -39.42, "lon": -71.93, "altitud_m": 2847, "nombre": "Villarrica", "pais": "Chile"},
    # Referencias internacionales de gran emisión
    "etna": {"lat": 37.751, "lon": 14.993, "altitud_m": 3357, "nombre": "Etna", "pais": "Italia"},
    "stromboli": {"lat": 38.789, "lon": 15.213, "altitud_m": 924, "nombre": "Stromboli", "pais": "Italia"},
    "kilauea": {"lat": 19.421, "lon": -155.287, "altitud_m": 1222, "nombre": "Kilauea", "pais": "USA"},
    "popocatepetl": {"lat": 19.023, "lon": -98.622, "altitud_m": 5393, "nombre": "Popocatépetl", "pais": "México"},
}

# Parámetros de procesamiento
TROPOMI_PRODUCT = "L2__SO2___"  # Producto de SO2 nivel 2
BBOX_MARGIN_KM = 100  # Margen alrededor del volcán para la búsqueda
DEFAULT_ALTITUDE_M = 3000  # Altitud por defecto para extracción de viento (metros)

# Niveles de presión ERA5 (hPa) para extracción de viento
PRESSURE_LEVELS = [1000, 925, 850, 700, 500, 300, 200, 100]

# ============================================================
# MÉTODO SO2FC (Carbajal et al. - SEGEMAR/OAVV)
# ============================================================

# Franjas horarias para el cálculo de flujo (horas desde el volcán)
SO2FC_FRANJAS_HORAS = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

# Tolerancia para selección de píxeles en cada franja (±horas)
SO2FC_TOLERANCIA_HORA = 0.1

# Tolerancia para el azimut de la pluma (grados)
SO2FC_TOLERANCIA_AZIMUT = 30

# Distancia de referencia para detectar azimut de pluma (metros)
SO2FC_DISTANCIA_REFERENCIA = 60000  # 60 km

# Porcentaje máximo de píxeles sin dato admitido para procesar una imagen
# MATLAB: if (sum(sum(isnan(SO2_Molm2)))*100)/numel(SO2_Molm2) < 40
SO2FC_MAX_PORCENTAJE_SIN_DATO = 40

# Ventana vertical donde se busca el viento de la pluma, medida desde la
# altura del crater hacia arriba (metros). Acota la busqueda al rango
# fisicamente esperable para una pluma de desgasificacion pasiva y evita
# que se seleccionen niveles de la corriente en chorro.
SO2FC_VENTANA_ALTURA_M = 2000

# Radio máximo de búsqueda (AOI - Area of Interest)
# Similar al clip(AOI) de Google Earth Engine
# Debe cubrir al menos 3h de viaje con vientos fuertes (~30 m/s = 324 km)
SO2FC_RADIO_MAXIMO_KM = 400  # km

# Conversiones de unidades (del código MATLAB)
# mol/m² a g/m²: dividir por 0.0156 (masa molar / factor)
# g/m² a kg/m²: multiplicar por 0.001
MOLM2_TO_GM2_FACTOR = 1 / 0.0156  # ≈ 64.1
GM2_TO_KGM2_FACTOR = 0.001

# kg/s a ton/día: multiplicar por 86.4
KGS_TO_TD_FACTOR = 86.4  # 86400 s/día ÷ 1000 kg/ton

# Alturas por nivel de presión (metros) - Del código MATLAB
PRESSURE_TO_HEIGHT = {
    1000: 111,
    975: 323,
    950: 540,
    925: 762,
    900: 988,
    850: 1458,
    800: 1948,
    750: 2465,
    700: 3013,
    650: 3589,
    600: 4204,
    550: 4863,
    500: 5576,
    450: 6341,
    400: 7187,
    350: 8113,
    300: 9166,
    250: 10366,
    200: 11787
}
