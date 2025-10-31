# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in DockerWebUI, please report it responsibly:

1. **DO NOT** open a public GitHub issue
2. Send an email to the repository maintainer or create a private security advisory on GitHub
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will acknowledge your report within 48 hours and provide a timeline for a fix.

---

## Security Measures

### Authentication & Authorization
- **JWT-based authentication** with configurable secret keys
- **Bcrypt password hashing** (cost factor: default)
- **Token expiration:** 30 minutes (configurable)
- **Protected endpoints:** All Docker API endpoints require valid JWT

### Input Validation
- All user inputs are validated using Pydantic models
- Container IDs, image names, and node names are sanitized
- Regex-based validation prevents injection attacks
- Password minimum length: 8 characters
- Username validation: alphanumeric with underscore/hyphen only

### Network Security
- **CORS:** Configurable allowed origins (not wide open by default in production)
- **WebSocket authentication:** Requires valid JWT token
- **Trusted hosts:** Optional middleware to prevent host header attacks
- **Security headers:** Recommended in production (see Production Best Practices)

### Container Security
- **Docker socket access:** Required but should be limited in production
- **User permissions:** Docker API endpoints validate authentication
- **Image validation:** Names are validated before pull/push operations

---

## Security Configuration

### Required Environment Variables (Production)

```bash
# Backend
export DOCKERWEBUI_SECRET_KEY="your-super-secret-key-here"  # REQUIRED!
export ALLOWED_ORIGINS="https://yourdomain.com"              # Restrict CORS
export TRUSTED_HOSTS="yourdomain.com,localhost"              # Optional

# Frontend
export REACT_APP_API_URL="https://api.yourdomain.com"
```

### First-Time Setup

1. **Change default credentials immediately!**
   - Default: `admin` / `admin`
   - Change via application or regenerate `users.json`

2. **Set a strong SECRET_KEY**
   - Generate: `openssl rand -hex 32`
   - Never use the default value in production

3. **Configure CORS properly**
   - Don't use `*` in production
   - List specific allowed origins

4. **Restrict Docker socket access**
   - Consider using Docker API over TCP with TLS
   - Run with minimal container privileges

---

## Production Best Practices

### 1. Use HTTPS
```nginx
# Nginx configuration example
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
    
    location / {
        proxy_pass http://frontend:80;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Container Security
```yaml
# docker-compose.yml hardened example
services:
  backend:
    build: ./backend
    read_only: true  # Make container filesystem read-only
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro  # Read-only if possible
      - ./backend/users.json:/app/users.json  # Persist user data
    environment:
      - DOCKERWEBUI_SECRET_KEY=${SECRET_KEY}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 3. User Management
- Implement user roles and permissions
- Add user management endpoints (create, update, delete users)
- Implement password reset functionality
- Add audit logging for sensitive operations

### 4. Rate Limiting
Consider adding rate limiting to prevent brute force attacks:
```python
# Example using slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")  # 5 login attempts per minute
async def login(request: Request, ...):
    ...
```

### 5. Monitoring & Logging
- Enable access logs for audit trails
- Monitor failed login attempts
- Set up alerts for suspicious activity
- Log all container operations (start, stop, delete)

---

## Vulnerability Management

### Dependency Updates
- **Backend:** Run `pip list --outdated` monthly
- **Frontend:** Run `npm audit` before deployments
- **Check advisories:** Monitor GitHub security advisories

### Current Known Issues
As of 2025-10-31:
- **Backend:** ✅ No known vulnerabilities
- **Frontend:** ⚠️ 9 vulnerabilities in dev dependencies (react-scripts)
  - These affect only development environment
  - Not present in production build
  - Monitoring for react-scripts updates

### Security Scanning
```bash
# Backend security check
pip install safety
safety check --json

# Frontend audit
npm audit

# Container scanning
docker scan dockerwebui-backend:latest
docker scan dockerwebui-frontend:latest
```

---

## Compliance Considerations

### Data Privacy
- **User passwords:** Hashed with bcrypt (never stored in plain text)
- **JWT tokens:** Stored client-side (localStorage)
- **Container data:** Accessed via Docker API (no data persisted by app)

### Access Control
- All Docker operations require authentication
- JWT tokens expire after 30 minutes
- No default user persistence beyond initial setup

### Audit Trail
- Consider implementing audit logging for:
  - User login/logout events
  - Container operations (create, start, stop, delete)
  - Image operations (pull, remove)
  - Configuration changes

---

## Security Checklist for Deployment

- [ ] Changed default admin credentials
- [ ] Set strong `DOCKERWEBUI_SECRET_KEY`
- [ ] Configured `ALLOWED_ORIGINS` properly
- [ ] Using HTTPS/TLS in production
- [ ] Docker socket access minimized
- [ ] Security headers configured
- [ ] Regular backup of `users.json`
- [ ] Monitoring and logging enabled
- [ ] Rate limiting implemented (recommended)
- [ ] Container security options configured
- [ ] Dependencies updated and audited
- [ ] Firewall rules configured
- [ ] Principle of least privilege applied

---

## Contact

For security concerns:
- **GitHub Security Advisories:** Use the "Security" tab on the repository
- **Issues:** Only for non-security bugs
- **Documentation:** See README.md for general usage

---

**Remember:** Security is a continuous process. Regularly review and update your security measures.

**Last Updated:** 2025-10-31
