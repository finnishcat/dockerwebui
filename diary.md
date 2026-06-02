# Diary - Registro Modifiche DockerWebUI

## [2026-06-02] Revisione completa del progetto

### Stato iniziale
Il progetto DockerWebUI è un'interfaccia web per gestire container Docker.
All'avvio della revisione, il backend risultava **incompleto**: `docker_api.py`
conteneva solo import e router, senza alcun endpoint implementato.
Il frontend e i test facevano riferimento a endpoint inesistenti.

---

### Modifica 1: docker_api.py — Implementazione completa API Docker
- **File**: `backend/docker_api.py`
- **Cosa**: Aggiunti tutti gli endpoint mancanti per container, immagini, stats
- **Perché**: Il file era uno stub vuoto — il progetto non funzionava
- **Dettagli**: 10 endpoint implementati:
  - `GET /docker/containers/{node}` — lista container
  - `GET /docker/images/{node}` — lista immagini
  - `GET /docker/stats/{node}/{container_id}` — stats CPU/RAM/Net
  - `POST /docker/container/restart/{node}/{id}` — restart
  - `POST /docker/container/stop/{node}/{id}` — stop
  - `POST /docker/container/remove/{node}/{id}` — remove
  - `POST /docker/image/pull/{node}` — pull
  - `DELETE /docker/image/remove/{node}/{id}` — remove image
  - `GET /docker/image/save/{node}/{id}` — **save/export** (nuovo)
  - `POST /docker/image/load/{node}` — **load/import** (nuovo)

### Modifica 2: Docker Save/Load (Export/Import Immagini)
- **File**: `backend/docker_api.py`
- **Cosa**: Aggiunti endpoint per scaricare e caricare immagini Docker
- **Perché**: Richiesta esplicita dell'utente
- **Come**:
  - `save`: usa `docker.APIClient.get_image()` che restituisce un tar.
    StreamingResponse con media type `application/x-tar` e header
    `Content-Disposition: attachment` per forzare il download.
  - `load`: usa `docker.APIClient.load_image()` che accetta un file tar
    multipart. Estrae il nome immagine dalla risposta per feedback.

### Modifica 3: Compatibilità Podman
- **File**: `backend/docker_api.py`
- **Cosa**: Refactor del dizionario `clients` per accettare URL arbitrari
- **Perché**: Permette di connettersi a Podman o Docker remoto
- **Come**: Introdotta variabile d'ambiente `DOCKERWEBUI_NODES` in formato
  JSON che mappa nome nodo -> URL Docker (es. `tcp://podman:2375`).
  Podman è API-compatibile con Docker, quindi lo stesso client SDK funziona.

### Modifica 4: Fix WebSocket URL
- **File**: `frontend/src/pages/ContainerDetails.tsx`
- **Cosa**: Sostituito `ws://localhost:8000` con URL derivato da API_URL
- **Perché**: In produzione il backend non è su localhost
- **Come**: Aggiunta variabile `REACT_APP_WS_URL` con fallback a
  `ws://localhost:8000`. Usa la stessa logica API_URL convertendo http->ws.

### Modifica 5: Fix Register URL hardcoded
- **File**: `frontend/src/pages/Register.tsx`
- **Cosa**: Sostituito `http://localhost:8000` con `process.env.REACT_APP_API_URL`
- **Perché**: In produzione l'URL è diverso

### Modifica 6: Logout funzionalità + navigazione
- **File**: Tutti i componenti frontend
- **Cosa**: Aggiunto pulsante logout che cancella token e redirect a login
- **Perché**: Manca completamente la possibilità di uscire

### Modifica 7: Validazione JWT in RequireAuth
- **File**: `frontend/src/components/RequireAuth.tsx`
- **Cosa**: Decodifica JWT, verifica scadenza, redirect se expired/invalido
- **Perché**: Prima controllava solo esistenza token in localStorage

### Modifica 8: Rate limiting su login/register
- **File**: `backend/auth.py`
- **Cosa**: Aggiunto rate limiting usando `slowapi`
- **Perché**: Prevenire brute force su login

### Modifica 9: Rimozione Unsplash deprecato
- **File**: `frontend/src/pages/Login.tsx`
- **Cosa**: Sostituito sfondo Unsplash con gradiente CSS nativo
- **Perché**: Unsplash source API è stata deprecata

### Modifica 10: Menu navigazione
- **File**: `frontend/src/App.tsx` e pagine
- **Cosa**: Aggiunta barra di navigazione globale
- **Perché**: Necessario per navigare tra Dashboard, Images, Logout

### Modifica 11: UI export/import immagini
- **File**: `frontend/src/pages/Images.tsx`
- **Cosa**: Aggiunti pulsanti download (save) e upload (load) per immagini
- **Perché**: Richiesta esplicita utente
- **Come**: Download via blob URL, upload via file input + FormData

### Modifica 12: Versione dipendenze pinneggiate
- **File**: `backend/requirements.txt`
- **Cosa**: Specificate versioni minime per tutte le dipendenze
- **Perché**: Garantire riproducibilità e sicurezza

### Modifica 13: docker-compose migliorato
- **File**: `docker-compose.yaml`
- **Cosa**: Aggiunti healthcheck e volumi per persistenza
- **Perché**: Migliore gestione del ciclo di vita

### Modifica 14: Aggiunta env per nodi custom
- **File**: `docker-compose.yaml`
- **Cosa**: Aggiunta variabile DOCKERWEBUI_NODES per configurazione nodi
- **Perché**: Supporto Podman e nodi remoti

---

## Stato Finale
- Tutti gli endpoint Docker implementati e funzionanti
- Export/import immagini via docker save/load
- Supporto Podman via configurazione nodi
- Rate limiting su auth
- Logout e validazione token
- UI navigabile e completa
