FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# We can expose 5000 for local clarity, but Heroku ignores EXPOSE anyway
EXPOSE 5000

# Use Heroku's assigned port
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "main:app"]
