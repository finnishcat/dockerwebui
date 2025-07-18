# DockerWebUI

![CI](https://github.com/finnishcat/dockerwebui/actions/workflows/ci.yml/badge.svg)

## Requirements
- Docker
- Docker Compose
- Node.js (for frontend development)
- Python 3.10+

## Environment Variables
- `DOCKERWEBUI_SECRET_KEY`: secret key for JWT (required in production).

## Quick Start with Docker Compose

```sh
docker-compose up --build
```

## Manual Start

### Backend
```sh
cd backend
pip install -r requirements.txt
set DOCKERWEBUI_SECRET_KEY=your-secret-key  # Windows
export DOCKERWEBUI_SECRET_KEY=your-secret-key  # Linux/macOS
uvicorn main:app --reload
```

### Frontend
```sh
cd frontend
npm install
npm start
```

## Tests

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

## Contributing

Contributions, bug reports, and suggestions are welcome!  
To contribute:

1. Fork the repository.
2. Create a branch for your feature or fix (`git checkout -b feature/your-feature`).
3. Commit your changes.
4. Push the branch and open a Pull Request.

For questions or ideas, open an Issue!
