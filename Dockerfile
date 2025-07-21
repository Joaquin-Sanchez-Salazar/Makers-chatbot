# 1) Etapa de build: instalar dependencias
FROM python:3.10-slim AS builder

# Variables de entorno para no generar archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copiamos sólo lo necesario para instalar deps
COPY requirements.txt .

# Instala dependencias sin caches
RUN pip install --no-cache-dir -r requirements.txt

# 2) Etapa final: copia la app y ejecutable
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copiamos deps instaladas
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiamos el código de la aplicación
COPY . .

# Expone el puerto de FastAPI/Uvicorn
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
