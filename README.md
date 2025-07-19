# 🚢 DockerWebUI

![CI](https://github.com/finnishcat/dockerwebui/actions/workflows/ci.yml/badge.svg)

**DockerWebUI** is a modern webapp to manage Docker containers with a graphical interface, designed to be simple, fast, and ready to use both locally and in production.

---

## 🚀 Technologies Used

- **Frontend:** React 18 + TypeScript, React Router, Testing Library, Tailwind CSS (optional)
- **Backend:** FastAPI, Uvicorn, Docker SDK for Python, JWT Auth
- **Realtime:** WebSocket for live container logs
- **Testing:** Pytest (backend), Testing Library (frontend)
- **DevOps:** Docker, Docker Compose, GitHub Actions CI

---

## ⚙️ How it Works & Architecture

- **Frontend:** Single Page Application (SPA) React, built and served by Nginx in production.
- **Backend:** REST API + WebSocket, JWT authentication, user and Docker container management.
- **Communication:** The frontend communicates with the backend via API and WebSocket, using the Docker hostname (`http://backend:8000`) in production.
- **Security:** The admin user is automatically created on first run if `users.json` does not exist. Change the password in production!

---

## 🛠️ Environment Variables & Configuration

### Backend (`backend/.env` or environment variables)

- `DOCKERWEBUI_SECRET_KEY` **(required in production):** secret key for JWT signing.
- (Optional) Other standard FastAPI/Uvicorn variables.

### Frontend (`frontend/.env.production`)

- `REACT_APP_API_URL`  
  Backend URL (default for Docker Compose: `http://backend:8000`).

---

## 📦 How to Start the Application

### 🔥 Quick Start with Docker Compose

1. **Clone the repository**
   ```sh
   git clone https://github.com/finnishcat/dockerwebui.git
   cd dockerwebui
   ```

2. **(Optional) Set the secret key**
   - Edit `docker-compose.yaml` or export the `DOCKERWEBUI_SECRET_KEY` variable for the backend.

3. **Start everything**
   ```sh
   docker-compose up --build
   ```
   - Frontend: [http://localhost:3080](http://localhost:3080)
   - Backend API: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 🧑‍💻 Manual Start (Development)

#### Backend

```sh
cd backend
pip install -r requirements.txt
export DOCKERWEBUI_SECRET_KEY=your-secret-key  # Linux/macOS
# or
set DOCKERWEBUI_SECRET_KEY=your-secret-key     # Windows
uvicorn main:app --reload
```

#### Frontend

```sh
cd frontend
npm install
npm start
```
- The frontend in dev mode calls the backend at `localhost:8000` by default.

---

## 🧪 Testing

### Backend

```sh
cd backend
pytest
```

### Frontend

```sh
cd frontend
npm test
```

---

## ℹ️ Useful Information

- **First access:** The admin user is automatically created with username `admin` and password `admin` if `users.json` does not exist.
- **User management:** After the first login, change the admin password!
- **WebSocket:** Container logs are streamed in real time via WebSocket.
- **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome!  
To contribute:

1. Fork the repository.
2. Create a branch for your feature or fix (`git checkout -b feature/your-feature`).
3. Commit your changes.
4. Push the branch and open a Pull Request.

For questions or ideas, open an Issue!

---

**Happy hacking with DockerWebUI! 🚀**
