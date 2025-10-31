# 🚢 DockerWebUI

![CI](https://github.com/finnishcat/dockerwebui/actions/workflows/ci.yml/badge.svg)

**DockerWebUI** is a modern, secure web application for managing Docker containers with a graphical interface. Built with security best practices, comprehensive testing, and production-ready features.

---

## ✨ Features

- 🔐 **Secure Authentication:** JWT-based auth with bcrypt password hashing
- 🐳 **Docker Management:** List, start, stop, restart, and remove containers
- 📊 **Real-time Monitoring:** Live container logs via WebSocket
- 🖼️ **Image Management:** Pull and manage Docker images
- 📈 **Container Stats:** CPU, memory, and network usage monitoring
- 🧪 **Comprehensive Testing:** 49 total tests (27 backend + 22 frontend)
- 🔒 **Security First:** Input validation, CORS configuration, security headers
- 📦 **Production Ready:** Docker Compose deployment with best practices

---

## 🚀 Technologies Used

- **Frontend:** React 18.3 + TypeScript, React Router 6.28, Testing Library, Tailwind CSS
- **Backend:** FastAPI 0.120, Uvicorn 0.38, Docker SDK 7.1, JWT Auth
- **Realtime:** WebSocket for live container logs with authentication
- **Testing:** Pytest 8.4 (backend), Jest + Testing Library (frontend)
- **DevOps:** Docker, Docker Compose, GitHub Actions CI
- **Security:** Pydantic validation, bcrypt hashing, environment-based configuration

---

## ⚙️ How it Works & Architecture

- **Frontend:** Single Page Application (SPA) in React, built and served by Nginx in production
- **Backend:** REST API + WebSocket, JWT authentication, Docker container management
- **Communication:** Frontend ↔ Backend via HTTP API + WebSocket (authenticated)
- **Security:** JWT tokens, password hashing, input validation, CORS configuration
- **Testing:** Comprehensive test suite with 49 tests covering all major functionality

---

## 🔒 Security Features

- ✅ JWT-based authentication with configurable secret keys
- ✅ Bcrypt password hashing for user credentials
- ✅ Input validation on all endpoints (Pydantic models)
- ✅ CORS configuration with environment-based origins
- ✅ WebSocket authentication required for log streaming
- ✅ Container ID and image name validation (prevents injection)
- ✅ Environment variable validation with security warnings
- ✅ All dependencies scanned for vulnerabilities
- ✅ Comprehensive security documentation (see [SECURITY.md](SECURITY.md))

> ⚠️ **Important:** Change the default admin credentials (admin/admin) immediately in production!

---

## 🛠️ Environment Variables & Configuration

### Backend (`backend/.env` or environment variables)

- **`DOCKERWEBUI_SECRET_KEY`** *(required in production):* Secret key for JWT signing
  ```bash
  # Generate a secure key:
  openssl rand -hex 32
  ```
- **`ALLOWED_ORIGINS`** *(optional):* Comma-separated list of allowed CORS origins
  ```bash
  export ALLOWED_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"
  ```
- **`TRUSTED_HOSTS`** *(optional):* Comma-separated list of trusted host headers

### Frontend (`frontend/.env.production`)

- **`REACT_APP_API_URL`:** Backend URL  
  Default for Docker Compose: `http://backend:8000`

---

## 📦 How to Start the Application

### 🔥 Quick Start with Docker Compose

1. **Clone the repository**
   ```sh
   git clone https://github.com/finnishcat/dockerwebui.git
   cd dockerwebui
   ```

2. **Set the secret key (IMPORTANT for production)**
   ```sh
   export DOCKERWEBUI_SECRET_KEY=$(openssl rand -hex 32)
   # Or edit docker-compose.yaml
   ```

3. **Start everything**
   ```sh
   docker-compose up --build
   ```
   - Frontend: [http://localhost:3080](http://localhost:3080)
   - Backend API: [http://localhost:8000/docs](http://localhost:8000/docs)

4. **Login with default credentials**
   - Username: `admin`
   - Password: `admin`
   - **⚠️ Change immediately after first login!**

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

## 🧪 Testing

DockerWebUI includes comprehensive test coverage for both backend and frontend:

### Backend Tests (27 tests)

```sh
cd backend
pip install -r requirements.txt
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html
```

**Test Coverage:**
- ✅ Authentication (login, registration, JWT validation)
- ✅ Docker API (containers, images, stats, operations)
- ✅ Input validation and error handling
- ✅ Protected endpoint authorization

### Frontend Tests (22 tests)

```sh
cd frontend
npm install
npm test

# Run in CI mode
CI=true npm test
```

**Test Coverage:**
- ✅ Login component (form validation, authentication flow)
- ✅ Dashboard (container listing, loading states, navigation)
- ✅ Register component (user creation, error handling)
- ✅ RequireAuth guard (route protection)
- ✅ App routing

### Continuous Integration

Tests run automatically on every push and pull request via GitHub Actions:
- Backend: pytest on Python 3.10
- Frontend: Jest/Testing Library on Node 20
- Build verification for Docker images

---

## 📚 Documentation

- **[SECURITY.md](SECURITY.md)** - Security policy, best practices, and vulnerability reporting
- **[SBOM.md](SBOM.md)** - Software Bill of Materials with complete dependency list
- **[API Docs](http://localhost:8000/docs)** - Interactive API documentation (Swagger UI)

---

## 🔍 API Endpoints

### Authentication
- `POST /auth/login` - User login (returns JWT token)
- `POST /auth/register` - Create first admin user (only if no users exist)

### Docker Management
- `GET /docker/nodes` - List available Docker nodes
- `GET /docker/containers/{node}` - List all containers
- `GET /docker/images/{node}` - List all images
- `GET /docker/stats/{node}/{container_id}` - Get container statistics
- `POST /docker/container/restart/{node}/{container_id}` - Restart container
- `POST /docker/container/stop/{node}/{container_id}` - Stop container
- `POST /docker/container/remove/{node}/{container_id}` - Remove container
- `POST /docker/image/pull/{node}` - Pull Docker image
- `DELETE /docker/image/remove/{node}/{image_id}` - Remove image

### Health Check
- `GET /` - API health status

### WebSocket
- `WS /ws/logs/{node}/{container_id}?token={jwt}` - Stream container logs in real-time

All endpoints except health check and auth require JWT authentication via `Authorization: Bearer {token}` header.

---

## ℹ️ Useful Information

- **First access:** Admin user (admin/admin) is created automatically if no users exist
- **User management:** Change the admin password immediately after first login
- **WebSocket:** Container logs are streamed in real-time with authentication
- **API Docs:** Interactive Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs)
- **Security:** See [SECURITY.md](SECURITY.md) for production deployment best practices

---

## 🏗️ Project Structure

```
dockerwebui/
├── backend/
│   ├── auth.py              # JWT authentication logic
│   ├── docker_api.py        # Docker operations API
│   ├── websocket_logs.py    # WebSocket log streaming
│   ├── main.py              # FastAPI app entry point
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Backend container image
│   ├── test_auth.py         # Authentication tests
│   ├── test_docker_api.py   # Docker API tests
│   └── test_main.py         # Integration tests
├── frontend/
│   ├── src/
│   │   ├── pages/          # React page components
│   │   ├── components/     # Reusable React components
│   │   └── App.tsx         # Main app component
│   ├── package.json        # Node.js dependencies
│   ├── Dockerfile          # Frontend container image
│   └── *.test.tsx          # Component tests
├── docker-compose.yaml     # Multi-container orchestration
├── SECURITY.md             # Security documentation
├── SBOM.md                 # Software Bill of Materials
└── README.md               # This file
```

---

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome!  
To contribute:

1. Fork the repository
2. Create a branch for your feature or fix (`git checkout -b feature/your-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest` for backend, `npm test` for frontend)
5. Commit your changes
6. Push the branch and open a Pull Request

For security vulnerabilities, please see [SECURITY.md](SECURITY.md) for responsible disclosure.

---

## 📝 Changelog

### Version 1.0 (2025-10-31)
- ✨ Initial release with comprehensive features
- 🔒 Enhanced security (JWT auth, input validation, CORS configuration)
- 🧪 Comprehensive test suite (49 tests total)
- 📚 Complete documentation (README, SECURITY, SBOM)
- 🐳 Production-ready Docker deployment
- 📊 Real-time container monitoring and log streaming
- 🔧 Environment-based configuration
- ⚡ Performance optimizations

---

## 📄 License

See [LICENSE](LICENSE) file for details.

---

**Happy hacking with DockerWebUI! 🚀**

For questions or support, please open an issue on GitHub.
