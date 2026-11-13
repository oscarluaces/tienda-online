# Imagen base ligera de Python
FROM python:3.12-slim

# - Sin ficheros .pyc y con la salida de los logs al momento
# - Configuración de uvicorn por variables de entorno (se pueden cambiar con docker run -e)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UVICORN_HOST=0.0.0.0 \
    UVICORN_PORT=8000 \
    UVICORN_LOG_LEVEL=info

WORKDIR /app

# Usuario sin privilegios para no ejecutar la API como root
RUN useradd --create-home --shell /bin/bash appuser

# 1) Dependencias primero: Docker reutiliza esta capa de caché
#    mientras requirements.txt no cambie
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Código fuente
COPY src/ ./src/

# 3) Permisos: appuser es dueño del código y puede ejecutarlo
RUN chown -R appuser:appuser /app && chmod -R u+rx /app/src
USER appuser

# Puerto en el que escucha la API
EXPOSE 8000

# Comando de inicio: host y puerto se leen de UVICORN_HOST y UVICORN_PORT
CMD ["uvicorn", "main:app", "--app-dir", "src"]
