import pandas as pd
from sqlalchemy import create_engine
import os
import time
import psycopg2

# ===========================
# Wait for Postgres to be ready
# ===========================
max_retries = 30  # ~1 minute
retries = 0

while retries < max_retries:
    try:
        conn = psycopg2.connect(
            dbname=os.environ["PGDATABASE"],
            user=os.environ["PGUSER"],
            password=os.environ["PGPASSWORD"],
            host=os.environ["PGHOST"],
            port=os.environ["PGPORT"]
        )
        conn.close()
        print("✅ Postgres is ready! Starting ETL...")
        break
    except psycopg2.OperationalError:
        retries += 1
        print("Waiting for Postgres... attempt", retries)
        time.sleep(2)
else:
    print("❌ Postgres did not become ready in time. Exiting ETL.")
    exit(1)

# ===========================
# Load CSV and clean data
# ===========================
df = pd.read_csv('sample_logs/readings.csv')
df.dropna(inplace=True)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# ===========================
# Connect to Postgres
# ===========================
user = os.environ.get("PGUSER")
password = os.environ.get("PGPASSWORD")
host = os.environ.get("PGHOST")
port = os.environ.get("PGPORT")
db = os.environ.get("PGDATABASE")

engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")

# ===========================
# Load data into Postgres
# ===========================
df.to_sql('readings', engine, if_exists='replace', index=False)

print("✅ ETL completed successfully and data loaded into PostgreSQL!")
