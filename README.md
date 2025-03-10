# BankApplication
Django Application
🏦 BankApplication & APIBancaire
Ce projet est une application bancaire complète comprenant :

BankApplication (Frontend Django + Backend Django) : Interface utilisateur développée avec Django et Tailwind CSS.
APIBancaire (FastAPI) : API gérant les transactions et les calculs de prédictions.
🚨 FastAPI doit être démarré avant Django pour garantir le bon fonctionnement des appels API.

📌 Prérequis
Avant de commencer, assurez-vous d'avoir installé :

Python 3.9+
Node.js 16+ (pour Tailwind CSS)
Docker & Docker Compose
Git
Un compte Azure avec une base de données Azure SQL configurée
🔮 APIBancaire (FastAPI - Calcul de Prédictions)
📂 Structure du projet

APIBancaire/
│── app/              # Code source FastAPI
│── models/           # Modèles de données
│── services/         # Algorithmes de prédiction
│── tests/            # Tests unitaires
│── .env              # Variables d'environnement
│── Dockerfile        # Image Docker de l'API
│── README.md         # Documentation
🚀 Installation et lancement (Local)
Cloner le projet :


git clone https://github.com/wbensolt/APIBancaire.git
cd APIBancaire
Créer un environnement virtuel et installer les dépendances :


python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
Configurer la connexion à Azure SQL : Dans .env, ajoutez :


DATABASE_URL=mssql+pyodbc://USERNAME:PASSWORD@server.database.windows.net/DATABASE?driver=ODBC+Driver+17+for+SQL+Server
Démarrer l'API :


uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
Tester l'API : Documentation Swagger : http://localhost:8000/docs

🎨 BankApplication (Frontend Django + Tailwind CSS)
📂 Structure du projet

BankApplication/
│── bankapp/         # Code source Django
│── static/          # Fichiers statiques (CSS, JS)
│── templates/       # Templates HTML Django
│── .env             # Variables d'environnement
│── Dockerfile       # Image Docker de Django
│── README.md        # Documentation
🚀 Installation et lancement (Local)
Cloner le projet :


git clone https://github.com/wbensolt/BankApplication.git
cd BankApplication
Créer un environnement virtuel et installer les dépendances :


python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
Configurer la connexion à Azure SQL : Dans .env, ajoutez :


DATABASE_URL=mssql+pyodbc://USERNAME:PASSWORD@server.database.windows.net/DATABASE?driver=ODBC+Driver+17+for+SQL+Server
Appliquer les migrations :


python manage.py migrate
Démarrer le serveur Django :


python manage.py runserver 0.0.0.0:8001
Démarrer Tailwind CSS :


npm install
npm run build
Accéder à l'application : http://127.0.0.1:8001/

🐳 Déploiement avec Docker
1. APIBancaire (FastAPI) - Port 8000
Créer l’image Docker :

docker build -t api-bancaire .
Démarrer le conteneur :

docker run -p 8000:8000 --env-file .env api-bancaire
Tester l'API : http://localhost:8000/docs

2. BankApplication (Django) - Port 8001
🚨 ATTENTION : Lancer FastAPI avant Django pour que l'API soit disponible !

Créer l’image Docker :

docker build -t bank-application .
Démarrer le conteneur :

docker run -p 8001:8001 --env-file .env bank-application
Accéder à l'application : http://localhost:8001/

🔧 Déploiement sur Azure
📦 Déploiement de FastAPI et Django avec Azure
Voici les étapes pour déployer FastAPI et Django sur Azure avec Docker.

1. Déployer FastAPI (API Bancaire)
Créez le fichier deploy.sh dans le répertoire FastAPI avec les étapes suivantes :


#!/bin/bash

# Création du dossier de logs s'il n'existe pas
mkdir -p logs

# 🔹 Charger les variables depuis le fichier .env
if [ -f .env ]; then
    echo "🔵 Chargement des variables d'environnement depuis .env..."
    export $(grep -v '^#' .env | xargs)  # Charge toutes les variables de .env
else
    echo "⚠️ Fichier .env introuvable ! Assurez-vous qu'il est dans le même dossier."
    exit 1
fi

# 🔹 Utiliser les variables chargées depuis .env
RESOURCE_GROUP="$AZURE_RESOURCE_GROUP"
LOCATION="$AZURE_LOCATION"
ACR_NAME="$AZURE_ACR_NAME"
CONTAINER_NAME="$AZURE_CONTAINER_NAME"
IMAGE_NAME="$AZURE_IMAGE_NAME"
PORT="$AZURE_PORT"
DNS_LABEL="fastapiazure2"
CPU="2"
MEMORY="4"

echo "🔵 Connexion à Azure..."
az login | tee logs/azure_login.log

echo "🔵 Vérification du groupe de ressources..."
az group show --name $RESOURCE_GROUP | tee logs/group_show.log || az group create --name $RESOURCE_GROUP --location $LOCATION | tee logs/group_create.log

echo "🔵 Vérification du registre ACR..."
az acr show --name $ACR_NAME | tee logs/acr_show.log || az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic | tee logs/acr_create.log

echo "🔵 Connexion au registre ACR..."
az acr login --name $ACR_NAME | tee logs/acr_login.log

echo "🔵 Construction de l'image Docker..."
docker build --build-arg ENV_FILE=.env -t $IMAGE_NAME . | tee logs/docker_build.log

echo "🔵 Push de l'image Docker..."
docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:latest | tee logs/docker_push.log

echo "🔵 Déploiement du conteneur..."
az container create --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --image $ACR_NAME.azurecr.io/$IMAGE_NAME:latest --ports $PORT --dns-name-label $DNS_LABEL --ip-address Public --registry-username $(az acr credential show --name $ACR_NAME --query "username" -o tsv) --registry-password $(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv) --os-type Linux --cpu $CPU --memory $MEMORY | tee logs/container_create.log

echo "✅ Déploiement terminé !"
2. Déployer Django (BankApplication)
Suivez une approche similaire en utilisant un fichier deploy.sh pour déployer Django sur Azure.


🔑 Gestion des utilisateurs et authentification
1️⃣ Création d'un administrateur FastAPI
Méthode : POST
URL : http://172.189.47.235:8000/auth/register
Headers :
Content-Type: application/json
Body (JSON) :

{
  "username": "TestBanque103",
  "email": "admin31test103@example.com",
  "password": "admin123",
  "role": "admin"
}
2️⃣ Obtention du token administrateur
Méthode : POST
URL : http://172.189.47.235:8000/auth/login
Headers :
Content-Type: application/x-www-form-urlencoded
Body (x-www-form-urlencoded) :
makefile

email: admin31test103@example.com
password: admin123
Réponse :

{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer"
}
3️⃣ Création d’un utilisateur (lié à Django) avec le token administrateur
Méthode : POST
URL : http://172.189.47.235:8000/admin/users
Headers :
Authorization: Bearer <TOKEN_ADMINISTRATEUR>
Content-Type: application/json
Body (JSON) :

{
  "username": "admindjangoCloud20",
  "email": "admindjangoCloud20@admindjango.com",
  "password": "admin123",
  "role": "user"
}
Retour : Un mot de passe temporaire sera généré.
4️⃣ Activation de l'utilisateur
Méthode : POST
URL : http://172.189.47.235:8000/auth/activation
Headers :
Content-Type: application/json
Body (JSON) :

{
  "email": "admindjangoCloud20@admindjango.com",
  "old_password": "motdepasse_temporaire",
  "new_password": "motdepassefort"
}
✅ L'utilisateur est maintenant activé et peut faire des prédictions.
🎨 Création de l'utilisateur sur Django (Register)
{
  "email": "admindjangoCloud20@admindjango.com",
  "password": "motdepassefort"
}
💡 L’email doit être identique à celui de FastAPI pour que l’utilisateur puisse faire des prédictions.
📊 Faire une prédiction (Loan Applications)
🚀 Technologies utilisées
Technologie	Utilisation
Django	Frontend et gestion utilisateur
FastAPI	Backend, authentification, prédictions
Tailwind CSS	Design UI
Azure SQL	Base de données
Docker	Conteneurisation


📌 Contact & Support
📧 Email : wbensolt@example.com
🌍 GitHub : BankApplication | APIBancaire
N’hésitez pas à contribuer au projet et à ouvrir une issue en cas de problème ! 🚀

Cela ajoute la section expliquant le fonctionnement de FastAPI et Django pour l'authentification des utilisateurs, leur activation, ainsi que l'utilisation de l'API pour les prédictions.