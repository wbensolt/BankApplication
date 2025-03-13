#!/bin/bash

# Création du dossier de logs s'il n'existe pas
mkdir -p logs

# Charger les variables depuis le fichier .env
if [ -f .env ]; then
    echo "🔵 Chargement des variables d'environnement depuis .env..."
    export $(grep -v '^#' .env | xargs)  # Charge toutes les variables de .env
else
    echo "⚠️ Fichier .env introuvable ! Assurez-vous qu'il est dans le même dossier."
    exit 1
fi


# Variables
RESOURCE_GROUP="adelvoyeRG"
LOCATION="francecentral"
ACR_NAME="adelvoyeregistry"  # Registry name
# IMAGE_NAME="fastapi-app"
IMAGE_NAME="adelvoyedjangov1"

TAG="latest"
CONTAINER_NAME="djangocontainer"  #Container name
PORT=8000
DNS_LABEL="djangoazure$(date +%s)"
CPU="2"
MEMORY="4"




# Connexion à Azure
echo "🔵 Connexion à Azure..."
az login

# Vérification du groupe de ressources
echo "🔵 Vérification du groupe de ressources..."
if az group show --name $RESOURCE_GROUP &>/dev/null; then
    echo "✅ Groupe de ressources '$RESOURCE_GROUP' trouvé."
else
    echo "⚠️ Groupe de ressources '$RESOURCE_GROUP' introuvable. Création..."
    az group create --name $RESOURCE_GROUP --location $LOCATION | tee logs/group_create.log
fi


# Vérification du registre ACR et création si nécessaire
echo "🔵 Vérification du registre ACR..."
if az acr show --name $ACR_NAME &>/dev/null; then
    echo "✅ Registre ACR '$ACR_NAME' trouvé."
else
    echo "⚠️ Registre ACR '$ACR_NAME' introuvable. Création..."
    az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true | tee logs/acr_create.log
fi

# Activation de l'administrateur ACR
echo "🔵 Activation de l'administrateur ACR..."
az acr update -n $ACR_NAME --admin-enabled true | tee logs/acr_update.log

# Connexion au registre ACR
echo "🔵 Connexion au registre ACR..."
az acr login --name $ACR_NAME | tee logs/acr_login.log

#Vérification de l'IP
echo "🔵 Vérification de l'adresse IP publique..."
IP_PUBLIC=$(curl -s ifconfig.me)
echo "Votre adresse IP publique est : $IP_PUBLIC" | tee logs/public_ip.log

#Construction de l'image
echo "🔵 Construction de l'image Docker..."
docker build --build-arg ENV_FILE=.env -t $IMAGE_NAME . | tee logs/docker_build.log

#TAG de l'image
echo "🔵 Tag de l'image Docker..."
docker tag $IMAGE_NAME $ACR_NAME.azurecr.io/$IMAGE_NAME:latest | tee logs/docker_tag.log

# Push de l'image
echo "🔵 Push de l'image Docker..."
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:latest | tee logs/docker_push.log

# Suppression de 'lancien conteneur'
echo "🔵 Suppression de l'ancien conteneur (si existant)..."
az container delete --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --yes | tee logs/container_delete.log

# Déploiement sur Azure Container Instances (ACI)
echo "🔵 Déploiement du conteneur..."
echo "🔍 Vérification des variables utilisées dans la commande az container create..."
echo "RESOURCE_GROUP: $RESOURCE_GROUP"
echo "CONTAINER_NAME: $CONTAINER_NAME"
echo "ACR_NAME: $ACR_NAME"
echo "IMAGE_NAME: $IMAGE_NAME"
echo "PORT: $PORT"
echo "DNS_LABEL: $DNS_LABEL"
echo "CPU: $CPU"
echo "MEMORY: $MEMORY"
echo "server: $server"
echo "port: $port"
echo "username: $username"
echo "password: $password"
echo "driver: $driver"
echo "database: $database"
echo "SECRET_KEY: $SECRET_KEY"
echo "ALGORITHM: $ALGORITHM"
echo "ACCESS_TOKEN_EXPIRE_MINUTES: $ACCESS_TOKEN_EXPIRE_MINUTES"

az container create \
  --resource-group $RESOURCE_GROUP \
  --name $CONTAINER_NAME \
  --image $ACR_NAME.azurecr.io/$IMAGE_NAME:latest \
  --ports $PORT \
  --dns-name-label $DNS_LABEL \
  --ip-address Public \
  --registry-username $(az acr credential show --name $ACR_NAME --query "username" -o tsv) \
  --registry-password $(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv) \
  --os-type Linux \
  --cpu $CPU \
  --memory $MEMORY \
  --output json\
  --environment-variables \
      server="$serverdj" \
      port="$portdj" \
      username="$usernamedj" \
      password="$passworddj" \
      driver="$driverdj" \
      database="$databasedj" \
      SECRET_KEY="$SECRET_KEY" \
      ALGORITHM="$ALGORITHM" \
      ACCESS_TOKEN_EXPIRE_MINUTES="$ACCESS_TOKEN_EXPIRE_MINUTES" | tee logs/container_create.log\
  


# Attendre que le conteneur soit créé et obtenir l'IP  | Check dispo
echo "🔵 Attente que le conteneur soit déployé..."
until IP=$(az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query "ipAddress.ip" --output tsv); do
  echo "⏳ En attente du déploiement du conteneur..."
  sleep 10
done
echo "IP récupérée : $IP"


#Récuperation de l'IP publique
echo "🔵 Récupération de l'IP publique..."
IP=$(az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query "ipAddress.ip" --output tsv | tee logs/container_ip.log)

echo "✅ Déploiement terminé !"
echo "🌍 Accédez à votre API sur : http://$IP:$PORT/docs"