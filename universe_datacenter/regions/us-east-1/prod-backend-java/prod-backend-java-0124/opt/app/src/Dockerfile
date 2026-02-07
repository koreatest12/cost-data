FROM python:3.9-slim
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
# UPDATED by CI/CD Pipeline
ENV APP_VERSION=2.0.0