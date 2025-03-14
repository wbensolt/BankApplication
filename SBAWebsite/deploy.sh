#!/bin/bash

set -e

# Chargement des variables d'environnement depuis .env
if [ -f .env ]; then
    echo "🔵 Chargement des variables d'environnement depuis .env..."
    set -o allexport
    source .env
    set +o allexport
else
    echo "⚠️ Fichier .env introuvable ! Assurez-vous qu'il est dans le même dossier."
    exit 1
fi

# Variables nécessaires (adaptées depuis ton script FastAPI)
RESOURCE_GROUP="erymerRG"
LOCATION="francecentral"
ACR_NAME="erymerregistry"
IMAGE_NAME="django-app"
TAG="latest"
CONTAINER_NAME="django-app-instance"
PORT=8000
DNS_LABEL="django-app-$(date +%s)"
CPU="2"
MEMORY="4"

# Vérification de la connexion Azure
echo "🔵 Vérification de la connexion Azure..."
if ! az account show &>/dev/null; then
    echo "🔵 Connexion à Azure requise..."
    az login
fi

# Connexion au registre ACR
echo "🔵 Connexion au registre ACR..."
az acr login --name $ACR_NAME

# Suppression de l'ancien conteneur (si existant)
echo "🔵 Suppression de l'ancien conteneur (si existant)..."
if az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME &>/dev/null; then
    az container delete --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --yes
    echo "⏳ Attente de 10 secondes avant de créer un nouveau conteneur..."
    sleep 10
fi

# Déploiement sur Azure Container Instances (ACI)
echo "🚀 Déploiement du conteneur Django..."
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_NAME \
  --image $ACR_NAME.azurecr.io/django-app:latest \
  --ports $PORT \
  --dns-name-label $CONTAINER_NAME \
  --ip-address Public \
  --registry-username $(az acr credential show --name $ACR_NAME --query "username" -o tsv) \
  --registry-password $(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv) \
  --os-type Linux \
  --cpu 2 \
  --memory 4 \
  --environment-variables \
      DJANGO_SETTINGS_MODULE="$DJANGO_SETTINGS_MODULE" \
      DEBUG="$DEBUG" \
      REDIS_HOST="$REDIS_HOST" \
      REDIS_PORT="$REDIS_PORT" \
  --secure-environment-variables \
      DJANGO_DB_NAME="$DJANGO_DB_NAME" \
      DJANGO_DB_USERNAME="$DJANGO_DB_USERNAME" \
      DJANGO_DB_PASSWORD="$DJANGO_DB_PASSWORD" \
      DJANGO_DB_SERVER="$DJANGO_DB_SERVER" \
      SECRET_KEY="$SECRET_KEY"\
  --azure-file-volume-account-name $AZURE_STORAGE_ACCOUNT_NAME \
  --azure-file-volume-account-key $AZURE_STORAGE_KEY \
  --azure-file-volume-share-name $AZURE_STORAGE_SHARE_NAME \
  --azure-file-volume-mount-path /app/media\
  --exec-command "mkdir -p /tmp/staticfiles && chmod -R 777 /tmp/staticfiles"

# Attente du déploiement
echo "⏳ Attente du déploiement du conteneur..."
until IP=$(az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query "ipAddress.ip" --output tsv); do
  echo "⏳ En attente du déploiement..."
  sleep 10
done
echo "✅ IP récupérée : $IP"

echo "✅ Déploiement terminé !"
echo "🌍 Accédez à votre application Django sur : http://$IP:8000/admin"
