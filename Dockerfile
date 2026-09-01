FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py db.py .
COPY org_structure/ org_structure/
COPY sql/ sql/
COPY data/ data/

ENTRYPOINT ["python", "main.py"]
