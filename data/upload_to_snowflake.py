import os
import snowflake.connector
from dotenv import load_dotenv

# Load secret environment parameters from the local .env file
load_dotenv()

# Enforce a safety check to ensure credentials are populated
required_secrets = ["SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "SNOWFLAKE_ACCOUNT"]
for secret in required_secrets:
    if not os.getenv(secret):
        raise ValueError(f"❌ Missing critical configuration secret variable: {secret}. Please check your root .env file configuration layout.")

# Connect dynamically using your environment configuration
conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
    role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN")
)
cursor = conn.cursor()

try:
    print("⏳ Auto-generating cloud database environment securely...")
    cursor.execute("CREATE DATABASE IF NOT EXISTS FINAI_AUDIT_DB;")
    cursor.execute("CREATE SCHEMA IF NOT EXISTS FINAI_AUDIT_DB.PUBLIC;")
    cursor.execute("USE DATABASE FINAI_AUDIT_DB;")
    cursor.execute("USE SCHEMA PUBLIC;")
    
    # Recreate target physical staging and storage table environments
    cursor.execute("CREATE OR REPLACE STAGE finai_audit_stage;")
    cursor.execute("""
        CREATE OR REPLACE TABLE BANK_LEDGER (
            TX_ID STRING, ACCOUNT_ID STRING, TX_TIMESTAMP TIMESTAMP, 
            AMOUNT NUMBER, CURRENCY STRING, DIRECTION STRING, MERCHANT STRING, STATUS STRING
        );
    """)

    # Upload local data files up to your cloud internal stage
    print("⏳ Staging files to Snowflake data cloud...")
    cursor.execute("PUT file://data/bank_ledger.csv @finai_audit_stage AUTO_COMPRESS=FALSE;")
    cursor.execute("PUT file://data/regulatory_handbook.txt @finai_audit_stage AUTO_COMPRESS=FALSE;")

    # Process structured staging chunks directly into database matrices
    print("⏳ Processing copy pipelines...")
    cursor.execute("COPY INTO BANK_LEDGER FROM @finai_audit_stage/bank_ledger.csv FILE_FORMAT = (TYPE = csv SKIP_HEADER = 1);")
    
    print("🚀 App database fully initialized and loaded in the data cloud!")

finally:
    cursor.close()
    conn.close()
