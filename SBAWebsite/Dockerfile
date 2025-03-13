FROM python:3.11-slim


# Met à jour les dépôts et installe les dépendances de base, y compris le support ODBC pour Azure SQL
# Mettre à jour les paquets et installer les dépendances nécessaires pour ODBC
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    unixodbc \
    unixodbc-dev \
    odbcinst \
    lsb-release \
    ca-certificates \
    apt-transport-https \
    && curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/$(lsb_release -rs)/prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Définit l'encodage et les locales pour éviter les erreurs ODBC
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /app

# Copie et installe les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copie le reste du code de l'application dans le conteneur
COPY . .

# Copier le fichier .env dans le conteneur
COPY .env /app/.env

# Installer Gunicorn
RUN pip install gunicorn

RUN python manage.py collectstatic --noinput

# Définition de l'environnement
# ENV DATABASE_URL=${DATABASE_URL}

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "SBAWebsite.wsgi:application"]

