import pandas as pd
import os
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import logging
import time

# Configure logging
logging.basicConfig(
    filename="logs/ingestion_db.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

# --- MySQL Connection Configuration ---
MYSQL_USER = "root"
MYSQL_PASSWORD = "yourpassword"  
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DATABASE = "inventory_db"

# Encode the password to handle special characters like @
encoded_password = quote_plus(MYSQL_PASSWORD)

# Create the SQLAlchemy engine
engine = create_engine(
    f'mysql+mysqlconnector://{MYSQL_USER}:{encoded_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
)

'''Ingests a DataFrame into the specified MySQL table'''
def ingest_db(df, table_name, engine):
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)

'''Loads CSV files from the dataset folder and ingests them into the database'''
def load_row_data():
    start = time.time()
    data_dir = 'dataset'

    if not os.path.exists(data_dir):
        logging.error(f"Error: Directory '{data_dir}' not found. Please create it and place your CSV files inside.")
        return

    csv_found = False
    for file in os.listdir(data_dir):
        if file.endswith('.csv'):
            csv_found = True
            file_path = os.path.join(data_dir, file)
            try:
                df = pd.read_csv(file_path)
                table_name = os.path.splitext(file)[0]
                logging.info(f'Ingesting {file} into MySQL table: {table_name}')
                ingest_db(df, table_name, engine)
            except Exception as e:
                logging.error(f"Failed to ingest {file}: {e}")

    if not csv_found:
        logging.warning(f"No CSV files found in the '{data_dir}' directory.")

    end = time.time()
    total_time = (end - start) / 60
    logging.info('----------Ingestion Complete----------')
    logging.info(f'\nTotal Time Taken : {total_time:.2f} minutes')

if __name__ == '__main__':
    # Ensure the 'logs' directory exists
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.info('Starting data ingestion process...')
    load_row_data()
    logging.info('Data ingestion process finished.')