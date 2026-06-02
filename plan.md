# DockerWebUI - Piano di Revisione e Miglioramento

## Stato Attuale
DockerWebUI è un progetto per la gestione di container Docker via web (FastAPI + React).
**Problema critico**: `backend/docker_api.py` è uno stub vuoto — gli endpoint Docker non sono implementati.

---

## Fasi di Lavoro

### Fase 1: Audit e Diagnostica
- [x] Analisi completa del codice backend (main.py, auth.py, docker_api.py, websocker.py)
- [x] Analisi completa del codice frontend (App.tsx, Dashboard, ContainerDetails, Images, Login, Register)
- [x] Analisi infrastruttura (docker-compose, Dockerfile, CI)
- [x] Identificazione criticità software e di sicurezza

### Fase 2: Implementazione API Docker Mancanti
- [x] GET /docker/containers/{node} — Elenco container
- [x] GET /docker/images/{node} — Elenco immagini
- [x] GET /docker/stats/{node}/{container_id} — Statistiche container
- [x] POST /docker/container/restart/{node}/{id} — Riavvio container
- [x] POST /docker/container/stop/{node}/{id} — Arresto container
- [x] POST /docker/container/remove/{node}/{id} — Rimozione container
- [x] POST /docker/image/pull/{node} — Pull immagine
- [x] DELETE /docker/image/remove/{node}/{id} — Rimozione immagine
- [x] Validazione input (sanitizzazione) su tutti gli endpoint

### Fase 3: Docker Save / Load (Export/Import Immagini)
- [x] GET /docker/image/save/{node}/{image_id} — Download immagine (docker save -> streaming tar)
- [x] POST /docker/image/load/{node} — Upload/import immagine (tar -> docker load)
- [x] UI per export (pulsante download in Images.tsx)
- [x] UI per import (file picker + pulsante upload in Images.tsx)

### Fase 4: Compatibilità Podman
- [x] Refactor `clients` dict per supportare URL Docker/Podman configurabili via env
- [x] Aggiunta variabile d'ambiente `DOCKERWEBUI_NODES` per configurare nodi
- [x] Podman è API-compatibile con Docker — stesso client SDK

### Fase 5: Fix Frontend
- [x] WebSocket URL da `ws://localhost:8000` a dinamico basato su API_URL
- [x] Register.tsx: usa REACT_APP_API_URL invece di localhost hardcoded
- [x] Logout funzionalità (cancella token, redirect a login)
- [x] Validazione token JWT in RequireAuth (decodifica, scadenza)
- [x] Menu navigazione tra Dashboard / Images / Logout

### Fase 6: Security Hardening
- [x] Rate limiting su /auth/login e /auth/register
- [x] Logout esplicito con invalidazione lato frontend
- [x] Validazione JWT scaduto in RequireAuth
- [x] Versione dependencies pinneggiate in requirements.txt

### Fase 7: Miglioramenti Minori
- [x] Login.tsx: rimossa dipendenza da unsplash.com (deprecato), sfondo locale
- [x] Aggiunta variabile d'ambiente per WebSocket (REACT_APP_WS_URL)
- [x] Aggiunta HEALTHCHECK nel docker-compose per tutti i servizi
- [x] Aggiunta logging strutturato su tutti gli endpoint

### Fase 8: CI Pipeline Fix
- [x] Fix bcrypt/passlib incompatibility (rimosso `[bcrypt]` extra)
- [x] Aggiornato Node.js 20→22, Python 3.10→3.11
- [x] Aggiunto `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` env
- [x] Aggiunto `pip install --upgrade pip` step
- [x] Aggiunto pytest.ini per filtrare deprecation warning
- [x] React Router v7 future flags in BrowserRouter
- [x] Login.test.tsx — heading regex corretto (`/sign in/i`)
- [x] Login.tsx — rimosso Unsplash deprecato

### Fase 9: Test e Verifica
- [x] Verifica che i test backend passino `pytest` (10/10)
- [ ] Verifica build frontend `npm run build` (richiede Node.js)
- [ ] Test manuale import/export immagini

---

## API Endpoints (Completi)

| Metodo | Endpoint | Descrizione | Auth |
|--------|----------|-------------|------|
| POST | /auth/login | Login utente | No |
| POST | /auth/register | Registrazione admin | No |
| GET | /docker/containers/{node} | Lista container | JWT |
| GET | /docker/images/{node} | Lista immagini | JWT |
| GET | /docker/stats/{node}/{cid} | Stats container | JWT |
| POST | /docker/container/restart/{node}/{cid} | Riavvia container | JWT |
| POST | /docker/container/stop/{node}/{cid} | Ferma container | JWT |
| POST | /docker/container/remove/{node}/{cid} | Rimuovi container | JWT |
| POST | /docker/image/pull/{node} | Pull immagine | JWT |
| DELETE | /docker/image/remove/{node}/{iid} | Rimuovi immagine | JWT |
| GET | /docker/image/save/{node}/{iid} | **Export immagine (save)** | JWT |
| POST | /docker/image/load/{node} | **Import immagine (load)** | JWT |
| WS | /ws/logs/{node}/{cid} | Log realtime | JWT (query) |

## Problematiche Identificate (Originali)

1. **CRITICO**: `docker_api.py` è uno stub — nessun endpoint implementato
2. **ALTO**: WebSocket URL hardcoded `ws://localhost:8000`
3. **ALTO**: Register.tsx con `http://localhost:8000` hardcoded
4. **MEDIO**: Nessun logout — token persiste in localStorage per sempre
5. **MEDIO**: RequireAuth controlla solo esistenza token, non validità/scadenza
6. **MEDIO**: Unsplash API deprecata per sfondo login
7. **MEDIO**: Nessun rate limiting su login/register
8. **BASSO**: shared/ directory vuota
9. **BASSO**: styles.css vuoto

## Note Podman
Podman è API-compatibile con Docker Engine. L'unico requisito è che il socket
di Podman sia esposto via TCP o mount. Il docker-socket-proxy funziona solo con
Docker Engine. Per Podman serve o:
- Montare `/run/podman/podman.sock` direttamente
- Usare `podman system service --time=0 tcp://0.0.0.0:2375`
La configurazione via `DOCKERWEBUI_NODES` permette di specificare URL arbitrari.
