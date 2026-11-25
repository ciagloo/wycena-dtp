# Obraz kontenera z aplikacją. Uruchomienie:
#   docker build -t wycena-dtp .
#   docker run -p 8501:8501 wycena-dtp
# Aplikacja będzie dostępna pod adresem http://localhost:8501

FROM python:3.12-slim

WORKDIR /app

# Najpierw same biblioteki: Docker zapamięta ten krok i nie powtórzy go przy zmianie kodu.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
