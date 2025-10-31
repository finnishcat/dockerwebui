# Software Bill of Materials (SBOM)

## DockerWebUI - Version 1.0.0
**Generated:** 2025-10-31  
**Format:** SPDX-like plain text

## Project Information
- **Name:** DockerWebUI
- **Version:** 1.0.0
- **Description:** Modern web application for managing Docker containers
- **License:** See LICENSE file
- **Repository:** https://github.com/finnishcat/dockerwebui

---

## Backend Dependencies (Python)

### Core Framework & API
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| fastapi | 0.120.3 | Web framework for building APIs | MIT |
| uvicorn | 0.38.0 | ASGI server | BSD |
| starlette | 0.49.1 | ASGI framework (FastAPI dependency) | BSD |
| pydantic | 2.12.3 | Data validation | MIT |
| pydantic-core | 2.41.4 | Core validation logic | MIT |

### Authentication & Security
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| python-jose | 3.5.0 | JWT token handling | MIT |
| passlib | 1.7.4 | Password hashing | BSD |
| python-multipart | 0.0.20 | Form data parsing | Apache-2.0 |

### Docker Integration
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| docker | 7.1.0 | Docker SDK for Python | Apache-2.0 |

### Testing
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| pytest | 8.4.2 | Testing framework | MIT |
| pytest-cov | 6.0.0 | Coverage plugin | MIT |
| pytest-asyncio | 0.25.2 | Async testing support | Apache-2.0 |
| httpx | 0.28.1 | HTTP client for testing | BSD |

---

## Frontend Dependencies (JavaScript/TypeScript)

### Core Framework
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| react | 18.3.1 | UI library | MIT |
| react-dom | 18.3.1 | React DOM renderer | MIT |
| react-router-dom | 6.28.0 | Client-side routing | MIT |
| react-scripts | 5.0.1 | Build tooling | MIT |

### UI Components & Icons
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| react-icons | 5.4.0 | Icon library | MIT |

### Development & Testing
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| typescript | 4.9.5 | Type system | Apache-2.0 |
| @testing-library/react | 14.3.1 | React testing utilities | MIT |
| @testing-library/jest-dom | 6.6.3 | Jest DOM matchers | MIT |
| @testing-library/user-event | 14.5.2 | User interaction simulation | MIT |
| @types/react | 18.3.17 | TypeScript types for React | MIT |
| @types/react-dom | 18.3.5 | TypeScript types for React DOM | MIT |

### Monitoring
| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| web-vitals | 4.2.4 | Performance monitoring | Apache-2.0 |

---

## Infrastructure

### Container Runtime
- **Docker:** Latest compatible version
- **Docker Compose:** v3 specification

### Web Server (Production)
- **Nginx:** alpine variant (used in frontend container)

### Base Images
- **Backend:** python:3.10-slim
- **Frontend Build:** node:20-alpine
- **Frontend Runtime:** nginx:alpine

---

## Security Considerations

### Known Vulnerabilities Status
- **Backend:** ✅ No known vulnerabilities in direct dependencies
- **Frontend:** ⚠️ 9 vulnerabilities in transitive dependencies from react-scripts
  - 3 moderate, 6 high severity
  - Related to: nth-check, postcss, webpack-dev-server
  - **Mitigation:** These are development dependencies and not included in production build
  - **Action:** Monitoring for react-scripts updates

### Security Features Implemented
1. JWT-based authentication with configurable secret keys
2. Bcrypt password hashing
3. Input validation on all endpoints
4. CORS configuration with environment-based origins
5. Request validation using Pydantic models
6. WebSocket authentication
7. Container ID and image name validation
8. Rate limiting considerations (ready for implementation)

### Security Best Practices
1. Use strong SECRET_KEY in production (not default)
2. Configure ALLOWED_ORIGINS appropriately
3. Set TRUSTED_HOSTS for production deployment
4. Change default admin password immediately
5. Run containers with minimal privileges
6. Keep dependencies updated regularly

---

## Deployment Requirements

### Backend Requirements
- Python 3.10+
- Access to Docker socket (`/var/run/docker.sock`)
- Environment variables:
  - `DOCKERWEBUI_SECRET_KEY` (required in production)
  - `ALLOWED_ORIGINS` (optional, comma-separated)
  - `TRUSTED_HOSTS` (optional, comma-separated)

### Frontend Requirements
- Node.js 20+ (for building)
- Nginx (for serving in production)
- Environment variables:
  - `REACT_APP_API_URL` (backend URL)

### Network Requirements
- Backend exposed on port 8000
- Frontend exposed on port 3080 (or 80 in container)
- WebSocket support required

---

## Compliance & Licenses

### License Summary
- **Primary Licenses:** MIT, BSD, Apache-2.0
- **All dependencies:** Open source with permissive licenses
- **No GPL or restrictive licenses** in production dependencies

### License Obligations
- **MIT/BSD:** Attribution required, permissive use
- **Apache-2.0:** Attribution + patent grant, permissive use

---

## Maintenance & Updates

### Update Strategy
1. Monitor security advisories for all dependencies
2. Regular dependency updates (monthly recommended)
3. Automated testing before updates
4. Pinned versions for stability

### Support Channels
- GitHub Issues: https://github.com/finnishcat/dockerwebui/issues
- Security Reports: See SECURITY.md

---

**Note:** This SBOM should be regenerated when dependencies are updated. Always verify current versions match production deployments.

**Last Updated:** 2025-10-31
**SBOM Version:** 1.0
