# SecureBank - Banking Loan Application

## 📌 Project Overview
SecureBank is a web-based banking platform that allows businesses to request loans, communicate with advisors, and stay informed with the latest banking news. The platform provides role-based dashboards for advisors and clients, offering a streamlined experience for managing loan applications and customer interactions.

## ✨ Features
- **User Authentication**: Secure registration and login system with email-based authentication.
- **Role-Based Dashboards**: Separate dashboards for clients and advisors.
- **Loan Application Management**: Clients can submit loan requests and view their status.
- **Real-Time Messaging**: Advisors and clients can communicate via an integrated messaging system.
- **Canned Messages**: Advisors can use predefined messages for quick responses.
- **News Management**: Advisors can create, update, and delete news articles for clients.
- **Loan Prediction**: The system predicts loan outcomes using an AI model integrated via FastAPI.
- **Azure Deployment**: The platform is containerized with Docker and deployed on Azure.

## 🚀 Installation Guide
### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Azure CLI (for deployment)
- Microsoft SQL Server (Configured for Django)

### Local Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/securebank.git
   cd securebank
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Create and configure the `.env` file:
   ```sh
   cp .env.example .env
   nano .env  # Edit with your environment variables
   ```
5. Apply database migrations:
   ```sh
   python manage.py migrate
   ```
6. Run the development server:
   ```sh
   python manage.py runserver
   ```
7. Access the platform at: `http://127.0.0.1:8000`

## 📦 Docker Deployment
To run the application in a Docker container:
```sh
docker build -t securebank .
docker run -p 8000:8000 securebank
```

## 🌍 Azure Deployment
To deploy the application on **Azure Container Instances (ACI)**:
1. Ensure you're logged into Azure:
   ```sh
   az login
   ```
2. Run the deployment script:
   ```sh
   chmod +x deploy.sh
   ./deploy.sh
   ```
3. Once deployed, access the application via the provided public IP.

## 📷 Screenshots
Below are some UI previews of SecureBank:

- Home page when not logged-in
![home page not logged in](<Capture d’écran du 2025-03-14 10-19-27.png>)

- Home Page when Logged in (visual changes depending on role)
![advisor exemple](<Capture d’écran du 2025-03-14 10-18-48.png>)

- Secured login and register page 
![alt text](<Capture d’écran du 2025-03-14 10-19-13.png>)
![alt text](<Capture d’écran du 2025-03-14 10-19-19.png>)
- Dashboard (Depends on role, in this example we'll use an advisor)
![alt text](<Capture d’écran du 2025-03-14 10-18-31.png>)
- Loan application approve or reject incoming loan requests
![alt text](<Capture d’écran du 2025-03-14 10-18-18.png>)
![alt text](<Capture d’écran du 2025-03-14 11-29-48.png>)
- Messages View (Choose a client from the conversations bar, search bar activated if more than 5 clients, find quick response to help you answer your clients request as a service representative in the quick response bar)
![alt text](<Capture d’écran du 2025-03-14 10-18-06.png>)
- News management (Create, Edit and Delete client news)
![alt text](<Capture d’écran du 2025-03-14 10-17-30.png>)
- In the client side they can send and see messages but not quick response, and they can see the news the bank posted. For the loan prediction once they fill out a form this is their view 
![alt text](<Capture d’écran du 2025-03-14 11-23-43.png>) 
![alt text](<Capture d’écran du 2025-03-14 11-23-56.png>)
## 📡 API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/register/` | POST | User registration |
| `/login/` | POST | User authentication |
| `/dashboard/` | GET | User dashboard |
| `/client/loans/create/` | POST | Create a new loan request |
| `/client/loans/<id>/` | GET | View a loan request |
| `/advisor/loans/` | GET | List all client loans |
| `/advisor/loans/<id>/approve/` | POST | Approve a loan request |
| `/advisor/loans/<id>/reject/` | POST | Reject a loan request |

## ⚙️ Technologies Used
- **Backend**: Django, FastAPI (loan prediction API)
- **Database**: Microsoft SQL Server
- **Frontend**: Tailwind CSS, Django Templates
- **Containerization**: Docker
- **Deployment**: Azure Container Instances (ACI), Azure File Storage

## 📝 License
This project is licensed under the MIT License. Feel free to modify and use it according to your needs.

## 📩 Contact
For inquiries, please reach out at [rymer.eliandy@gmail.com](mailto:rymer.eliandy@gmail.com).


