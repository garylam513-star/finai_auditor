import os
from datetime import datetime, timedelta
from typing import List

os.makedirs("data", exist_ok=True)

# 1. Generate Unstructured Regulatory Risk Playbook Text
handbook_text = """# FINAI REGULATORY AUDIT PLAYBOOK (v3.2)

SECTION 301: FRAUD AND LIQUIDITY ANOMALIES
Paragraph A: Velocity Round-Tripping (Structuring)
Accounts must be monitored for rapid-succession velocity anomalies designed to bypass internal thresholds.
If an account exhibits more than 2 distinct deposit transactions ('DIRECTION' = 'IN') within a 24-hour window where each transaction is kept below the $10,000 threshold but cumulatively totals greater than $10,000 USD (normalized), it must be flagged as an active Basel Structuring Violation.

SECTION 302: CREDIT RISKS AND LIQUIDITY DEFALCATION
Paragraph B: Non-Sufficient Funds (NSF) Check Stress
Any outbound payment event ('DIRECTION' = 'OUT') carrying a transaction status of 'FAILED' combined with a ledger description containing 'NSF' or 'OVERDRAFT' indicates acute liquidity stress and requires a compliance freeze.
"""

with open("data/regulatory_handbook.txt", "w", encoding="utf-8") as f:
    f.write(handbook_text.strip())

# 2. Generate Structured Multi-Currency Bank Ledger Entries
csv_lines: List[str] = ["TX_ID,ACCOUNT_ID,TX_TIMESTAMP,AMOUNT,CURRENCY,DIRECTION,MERCHANT,STATUS"]
now = datetime.now()

# Anomaly 1: Cross-border Structuring Alert (3 deposits close to €4,500 that break $10,000 USD combined)
csv_lines.append(f"TX_V01,ACC_9988,{(now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')},4500,EUR,IN,Cash Deposit,SUCCESS")
csv_lines.append(f"TX_V02,ACC_9988,{(now - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S')},4500,EUR,IN,Cash Deposit,SUCCESS")
csv_lines.append(f"TX_V03,ACC_9988,{(now - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S')},2000,EUR,IN,Cash Deposit,SUCCESS")

# Anomaly 2: Acute NSF Liquidity Defalcation Stress
csv_lines.append(f"TX_N01,ACC_1122,{(now - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')},850,USD,OUT,Rent Payment - NSF,FAILED")

# Standard Baseline Traffic Rows
for i in range(1, 10):
    tx_time = (now - timedelta(days=i)).strftime('%Y-%m-%d %H:%M:%S')
    csv_lines.append(f"TX_S{i:02d},ACC_1122,{tx_time},120,USD,OUT,Grocery Store,SUCCESS")

with open("data/bank_ledger.csv", "w", encoding="utf-8") as f:
    f.write("\n".join(csv_lines))

print("✅ Local mock database metrics generated successfully.")
