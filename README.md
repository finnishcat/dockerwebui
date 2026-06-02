# DockerWebUI

![CI](https://github.com/finnishcat/dockerwebui/actions/workflows/ci.yml/badge.svg)

DockerWebUI is a lightweight web UI to manage Docker containers (REST API + SPA frontend).

## Features

- **Container management**: list, restart, stop, remove containers
- **Image management**: list, pull, remove images
- **Image export/import**: download images as `.tar` via `docker save`, upload images via `docker load`
- **Realtime logs**: WebSocket streaming of container logs
- **Container stats**: live CPU, memory, and network I/O metrics
- **Authentication**: JWT-based login with bcrypt password hashing
- **Rate limiting**: login and registration endpoints protected against brute force
- **Socket proxy**: backend never mounts the Docker socket directly; uses `docker-socket-proxy`
- **Podman compatible**: configurable nodes via `DOCKERWEBUI_NODES` environment variable
- **Healthchecks**: all services include Docker health checks

## Security

- The backend no longer mounts `/var/run/docker.sock` directly. The stack includes `docker-socket-proxy` and the backend talks to it via `DOCKER_HOST`.
- `DOCKERWEBUI_SECRET_KEY` is required in production (fail-fast on default key).
- CORS is configurable via `ALLOWED_ORIGINS` (no wildcard by default).
- Rate limiting on `/auth/login` (10/min) and `/auth/register` (5/hour).
- Input sanitization on all Docker API endpoints.
- JWT token expiry checked on every request.
- `.dockerignore` excludes `users.json` from the Docker build context.

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DOCKERWEBUI_SECRET_KEY` | Yes | `dev-secret-key` | JWT signing key (fail-fast if default) |
| `ALLOWED_ORIGINS` | No | `http://localhost:3080` | Comma-separated CORS origins |
| `DOCKER_HOST` | No | `unix:///var/run/docker.sock` | Docker daemon URL |
| `DOCKERWEBUI_NODES` | No | `{"local":"unix:///var/run/docker.sock"}` | JSON map of node name to Docker URL (for Podman/remote) |
| `REACT_APP_API_URL` | No | `http://localhost:8000` | Backend API URL (frontend build-time) |
| `REACT_APP_WS_URL` | No | `ws://localhost:8000` | WebSocket URL (frontend build-time) |

## Quick start

```bash
git clone https://github.com/finnishcat/dockerwebui.git
cd dockerwebui

export DOCKERWEBUI_SECRET_KEY="$(openssl rand -hex 32)"
export ALLOWED_ORIGINS="http://localhost:3080"

docker compose -f docker-compose.yaml up -d --build
```

The frontend will be available on port `3080` and the backend on `8000`.

## Admin user / bootstrap

- On first run, if `users.json` does not exist, a default `admin` user is created. **Change the password immediately**.
- Safer workflow: register via API (only allowed if no users exist):

```sh
curl -X POST -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"StrongPa$$w0rd"}' \
  http://localhost:8000/auth/register
```

## API endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/login` | User login | No |
| POST | `/auth/register` | Register first admin | No (rate limited) |
| GET | `/docker/containers/{node}` | List containers | JWT |
| GET | `/docker/images/{node}` | List images | JWT |
| GET | `/docker/stats/{node}/{id}` | Container stats (CPU/RAM/Net) | JWT |
| POST | `/docker/container/restart/{node}/{id}` | Restart container | JWT |
| POST | `/docker/container/stop/{node}/{id}` | Stop container | JWT |
| POST | `/docker/container/remove/{node}/{id}` | Remove container | JWT |
| POST | `/docker/image/pull/{node}` | Pull image from registry | JWT |
| DELETE | `/docker/image/remove/{node}/{id}` | Remove image | JWT |
| GET | `/docker/image/save/{node}/{id}` | **Export image as `.tar`** | JWT |
| POST | `/docker/image/load/{node}` | **Import image from `.tar`** | JWT |
| WS | `/ws/logs/{node}/{id}` | Realtime container logs | JWT (query) |

## Podman support

Podman is API-compatible with Docker. Set `DOCKERWEBUI_NODES` to connect:

```bash
export DOCKERWEBUI_NODES='{"podman":"tcp://podman-host:2375"}'
```

Or use Podman's socket directly:

```bash
export DOCKERWEBUI_NODES='{"local":"unix:///run/podman/podman.sock"}'
```

## Image export/import

- **Export**: click the Export button on any image in the Images page to download it as a `.tar` archive.
- **Import**: use the Import button to upload a `.tar` archive (e.g. from `docker save`). The image is loaded via `docker load`.

## WebSocket logs

```
wscat -c "ws://localhost:8000/ws/logs/local/<container_id>?token=<JWT>"
```

## Contributing

Contributions are welcome. Please open issues or PRs.
