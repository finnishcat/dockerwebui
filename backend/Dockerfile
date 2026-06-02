FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Healthcheck: TCP check to local uvicorn port
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
	CMD python -c "import socket,sys; s=socket.socket(); s.settimeout(2); ret=s.connect_ex(('127.0.0.1',8000)); s.close(); sys.exit(0 if ret==0 else 1)"