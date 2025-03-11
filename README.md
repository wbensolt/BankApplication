# BankApplication

## Django Application

### 🏦 BankApplication & APIBancaire
Ce projet est une application bancaire complète comprenant :

- **BankApplication (Frontend Django + Backend Django)** : Interface utilisateur développée avec Django et Tailwind CSS.
- **APIBancaire (FastAPI)** : API gérant les transactions et les calculs de prédictions.

> 🚨 **FastAPI doit être démarré avant Django** pour garantir le bon fonctionnement des appels API.

## 📌 Prérequis
Avant de commencer, assurez-vous d'avoir installé :

- Python 3.9+
- Node.js 16+ (pour Tailwind CSS)
- Docker & Docker Compose
- Git
- Un compte Azure avec une base de données Azure SQL configurée

---

## 🌞 APIBancaire (FastAPI - Calcul de Prédictions)

### 📂 Structure du projet
```
APIBancaire/
│── app/              # Code source FastAPI
│── models/           # Modèles de données
│── services/         # Algorithmes de prédiction
│── tests/            # Tests unitaires
│── .env              # Variables d'environnement
│── Dockerfile        # Image Docker de l'API
│── README.md         # Documentation
```

### 🚀 Installation et lancement (Local)

Cloner le projet :
```bash
git clone https://github.com/wbensolt/APIBancaire.git
cd APIBancaire
```

Créer un environnement virtuel et installer les dépendances :
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Configurer la connexion à Azure SQL dans **.env** :
```env
DATABASE_URL=mssql+pyodbc://USERNAME:PASSWORD@server.database.windows.net/DATABASE?driver=ODBC+Driver+17+for+SQL+Server
```

Démarrer l'API :
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Tester l'API :
- Documentation Swagger : [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🎨 BankApplication (Frontend Django + Tailwind CSS)

### 📂 Structure du projet
```
BankApplication/
│── bankapp/         # Code source Django
│── static/          # Fichiers statiques (CSS, JS)
│── templates/       # Templates HTML Django
│── .env             # Variables d'environnement
│── Dockerfile       # Image Docker de Django
│── README.md        # Documentation
```

### 🚀 Installation et lancement (Local)

Cloner le projet :
```bash
git clone https://github.com/wbensolt/BankApplication.git
cd BankApplication
```

Créer un environnement virtuel et installer les dépendances :
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Configurer la connexion à Azure SQL dans **.env** :
```env
DATABASE_URL=mssql+pyodbc://USERNAME:PASSWORD@server.database.windows.net/DATABASE?driver=ODBC+Driver+17+for+SQL+Server
```

Appliquer les migrations :
```bash
python manage.py migrate
```

Démarrer le serveur Django :
```bash
python manage.py runserver 0.0.0.0:8001
```

Démarrer Tailwind CSS :
```bash
npm install
npm run build
```

Accéder à l'application : [http://127.0.0.1:8001/](http://127.0.0.1:8001/)

---

## 🐓 Déploiement avec Docker

### 1. APIBancaire (FastAPI) - Port 8000

Créer l’image Docker :
```bash
docker build -t api-bancaire .
```

Démarrer le conteneur :
```bash
docker run -p 8000:8000 --env-file .env api-bancaire
```

Tester l'API : [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. BankApplication (Django) - Port 8001

> 🚨 **ATTENTION :** Lancer FastAPI avant Django !

Créer l’image Docker :
```bash
docker build -t bank-application .
```

Démarrer le conteneur :
```bash
docker run -p 8001:8001 --env-file .env bank-application
```

Accéder à l'application : [http://localhost:8001/](http://localhost:8001/)

---

## 🔧 Déploiement sur Azure

Voir le fichier **deploy.sh** pour déployer FastAPI et Django sur Azure avec Docker.

------------------------------------------------------------------------------------------------

## 🔑 Comment fonctionnent les deux applications: Gestion des utilisateurs et authentification

### 1️⃣ Création d'un administrateur FastAPI
```json
{
  "username": "TestBanque103",
  "email": "admin31test103@example.com",
  "password": "admin123",
  "role": "admin"
}
```

### 2️⃣ Obtention du token administrateur
```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer"
}
```

### 3️⃣ Création d’un utilisateur Django avec le token admin
```json
{
  "username": "admindjangoCloud20",
  "email": "admindjangoCloud20@admindjango.com",
  "password": "admin123",
  "role": "user"
}
```

### 4️⃣ Activation de l'utilisateur
```json
{
  "email": "admindjangoCloud20@admindjango.com",
  "old_password": "motdepasse_temporaire",
  "new_password": "motdepassefort"
}
```

✅ L’utilisateur est activé et peut faire des prédictions.

🎨 Création de l'utilisateur sur Django (Register)
{
  "email": "admindjangoCloud20@admindjango.com",
  "password": "motdepassefort"
}
💡 L’email doit être identique à celui de FastAPI pour que l’utilisateur puisse faire des prédictions.
📊 Faire une prédiction (Loan Applications)
---

## 💎 Technologies utilisées
| Technologie | Utilisation |
|-------------|------------|
| Django | Frontend et gestion utilisateur |
| FastAPI | Backend, authentification, prédictions |
| Tailwind CSS | Design UI |
| Azure SQL | Base de données |
| Docker | Conteneurisation |

---

## 📢 Contact & Support

📧 Email : wbensolt@example.com  
🌐 GitHub : BankApplication | APIBancaire  
N’hésitez pas à contribuer au projet et à ouvrir une issue en cas de problème ! 🚀

