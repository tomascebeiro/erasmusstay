FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY src .

# Normalizar line endings (Windows y Linux compatible)
RUN python << 'EOF'
with open('entrypoint.sh', 'rb') as f:
    content = f.read()
with open('entrypoint.sh', 'wb') as f:
    f.write(content.replace(b'\r\n', b'\n').replace(b'\r', b'\n'))
EOF
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]