# Release Notes — DockerWebUI

## v2.0.0 — Major Revision

### Nuove Funzionalità

#### Docker API Completa
- Implementati tutti gli endpoint mancanti: container list, images list, stats, restart/stop/remove, pull/remove.
- `backend/docker_api.py` non è più uno stub — ora espone 10 endpoint REST funzionanti.

#### Export / Import Immagini
- **Download immagine** (`docker save`): GET `/docker/image/save/{node}/{id}` restituisce un file `.tar`.
- **Upload immagine** (`docker load`): POST `/docker/image/load/{node}` accetta un file `.tar` multipart.
- UI dedicata in Images.tsx: pulsante Export su ogni immagine + pulsante Import con file picker.

#### Compatibilità Podman
- Nuova variabile d'ambiente `DOCKERWEBUI_NODES` (JSON) per configurare nodi Docker/Podman arbitrari.
- Podman è API-compatibile: basta specificare l'URL del socket o TCP.

#### Rate Limiting
- `/auth/login`: 10 richieste al minuto.
- `/auth/register`: 5 richieste all'ora.
- Implementato con `slowapi`.

#### Navigazione e Logout
- Aggiunta navbar globale con link a Dashboard, Images e pulsante Logout.
- Logout cancella il token JWT dal localStorage e reindirizza al login.

#### Validazione JWT
- `RequireAuth.tsx` ora decodifica il JWT e verifica la scadenza prima di mostrare contenuti protetti.
- Token scaduto o malformato → redirect automatico al login.

### Security Hardening

- **Fail-fast** su `DOCKERWEBUI_SECRET_KEY` di default (mantenuto).
- **Input sanitization** con regex pattern su tutti gli ID container, immagini, nodi.
- **Password validation**: minimo 8 caratteri su registrazione.
- **Rate limiting** su endpoint sensibili.
- **Dockerignore**: `users.json` escluso dal contesto di build Docker.
- **Dipendenze pinneggiate**: versioni minime e massime in requirements.txt.
- **bcrypt compat fix**: versione pinata a `bcrypt>=4.0.0,<4.1.0` per compatibilità con passlib.

### Fix Bug

- **WebSocket URL**: era hardcoded `ws://localhost:8000`, ora usa `REACT_APP_WS_URL`.
- **Register URL**: era hardcoded `http://localhost:8000`, ora usa `REACT_APP_API_URL`.
- **Unsplash API deprecata**: rimosso sfondo dinamico da `source.unsplash.com`, sostituito con gradiente CSS nativo.
- **CI workflow**: aggiunta variabile `DOCKERWEBUI_SECRET_KEY` mancante nel job backend.
- **Test Login**: aggiornato per matchare il nuovo heading "Sign in to DockerWebUI".

### Infrastruttura

- Tutti i servizi (backend, frontend, docker-socket-proxy) ora hanno `HEALTHCHECK`.
- Aggiunti `.dockerignore` per backend e frontend.
- `docker-compose.yaml` include healthcheck per tutti i servizi.

### Documentazione

- `plan.md`: piano di revisione e registro di avanzamento.
- `diary.md`: diary completo di ogni modifica con motivazioni.
- `README.md` aggiornato con tutte le nuove funzionalità.
- `release.MD`: questo file.

### Lista Completa File Modificati

```
backend/docker_api.py            Riscritto (da stub a 10 endpoint + save/load)
backend/auth.py                  Rate limiting, password validation
backend/main.py                  Integrazione slowapi
backend/requirements.txt         Versioni pinneggiate + bcrypt compat
backend/test_main.py             Test aggiornati + nuovi
backend/.dockerignore            Nuovo
frontend/App.tsx                 Navbar + logout
frontend/components/RequireAuth.tsx  Validazione JWT
frontend/pages/Images.tsx        Export/Import UI
frontend/pages/ContainerDetails.tsx  WS_URL dinamico
frontend/pages/Login.tsx         Rimosso Unsplash
frontend/pages/Register.tsx      URL da env var
frontend/.env                    Aggiunto REACT_APP_WS_URL
frontend/.env.production         Aggiunto REACT_APP_WS_URL
frontend/.dockerignore           Nuovo
docker-compose.yaml              Healthcheck per tutti
.github/workflows/ci.yml         Fix env mancante
README.md                        Aggiornato
plan.md                          Nuovo
diary.md                         Nuovo
release.MD                       Nuovo
```
