FROM python:3.11-slim

RUN useradd --create-home appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python create_db.py && chown appuser:appuser database.db

USER appuser

EXPOSE 5000

CMD ["python", "app.py"]