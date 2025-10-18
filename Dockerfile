FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ETL and CSV files
COPY batch_pipeline/ETL.py .
COPY sample_logs ./sample_logs

# Run ETL
CMD ["python", "ETL.py"]
