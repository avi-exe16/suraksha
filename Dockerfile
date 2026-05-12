FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir pandas numpy scikit-learn fastapi uvicorn sqlalchemy \
    psycopg2-binary redis python-dotenv pydantic shap torch torchvision \
    pyod reportlab python-multipart joblib faker

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]