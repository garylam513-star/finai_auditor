# FinAI-auditor 🛡️

**FinAI-auditor** is an AI-powered Enterprise Risk, Fraud, and Regulatory Copilot built for the **Snowflake CoCo CLI Hackathon (GCC Edition) - Track 1 (Banking, NBFC, and FinTech)**. 

The application integrates unstructured internal policy manuals, structured cross-border transaction ledgers, and external, live-shared infrastructure data feeds straight from the **Snowflake Marketplace** to surface audit-ready compliance evidence on-demand.

---

## 🚀 Key Achievements & Technical Capabilities
* **Data Fusion Insights:** Jointly parses unstructured compliance texts (`regulatory_handbook.txt`) and transactional tables (`BANK_LEDGER`) concurrently via Snowflake Cortex AI.
* **Cross-Border Normalization:** Pulls live global currency exchange conversion matrices directly from the **TraderMade FX Data Share** on Snowflake Marketplace to catch offshore anomalies natively without standard API calls.
* **Automated Risk Flags:** Instantly flags high-velocity structuring alerts (sub-\$10k deposits aggregating to violate Basel restrictions within 24 hours) and Non-Sufficient Funds (NSF) liquidity risk tokens.
* **Audit-Ready Citation Logs:** Generates explainable evidence grids matching transaction logs side-by-side with specific text playbook clauses to construct complete regulatory paper trails.

---

## ⚙️ App Core Functionality & Architectural Flow

FinAI-auditor moves beyond a standard Q&A chatbot by implementing an enterprise-grade agentic workflow. When an investigator inputs an account or compliance query via the Streamlit interface, the application processes the request through four automated internal layers:

```text
 💻 USER DASHBOARD   ➔   🧬 COCO CUSTOM SKILL   ➔   🤖 CORTEX INTERROGATION   ➔   📊 LIVE COMPLIANCE AUDIT
  (Streamlit UI Input)     (fintech_auditor.md)      (Structured + Unstructured)     (Citations + FX Normalized)
```

1. **Natural Language Translation & Intent Parsing:** The Streamlit interface passes the auditor's plain English text directly to the custom CoCo Agent Skill framework (`.cc_skills/fintech_auditor.md`). The skill acts as a strict governance layer, forcing the AI to act exclusively as an expert risk investigator.
2. **Context-Grounded Cortex Search Engine:** Instead of guessing or hallucinating, the application executes a **Cortex Search Service** over the unstructured `regulatory_handbook.txt` file. It extracts the exact semantic meanings of financial crimes (e.g., how the manual legally defines "Structuring" or "Liquidity Defalcation").
3. **Zero-Copy Multi-Source Data Joining:** The agent queries the structured `BANK_LEDGER` table inside the cloud database. Simultaneously, it uses Snowflake's secure data sharing architecture to execute a zero-copy, real-time join with the live **TraderMade FX** marketplace database. 
4. **Currency Normalization & Grounded Reasoning:** The application programmatically evaluates all transactions. If an account has multiple transactions across different foreign currencies (e.g., Euros, Rupees), it applies the live exchange rate to normalize them to a base USD valuation.
5. **Cited Output Compilation:** The agent builds a side-by-side report on the dashboard UI. It presents the violating **Transaction IDs** directly alongside a quote of the specific **Handbook Section/Paragraph Clause** that was breached, giving compliance teams an audit-ready paper trail instantly.

---

## 🌐 Snowflake Marketplace Data Share Integration

To achieve maximum Technical Execution points under the hackathon evaluation rubric, **FinAI-auditor** integrates a zero-copy data share from the Snowflake Marketplace. This enables the CoCo Agent to cross-reference internal transactional data against institutional global currency fluctuations in real time, catching multi-currency velocity fraud without static API parameters or local storage bloat.

### A. How to Mount the Marketplace Feed (Snowsight UI)
1. Log into your assigned Snowflake hackathon sandbox web console.
2. Navigate to **Data Products** ➔ **Marketplace** on the left rail menu.
3. Search for the listing **"Currency Exchange Rates by TraderMade"**.
4. Click **"Get"** on the dataset page.
5. Under the options prompt, configure the destination Database Name to be exactly:
   ```text
   TRADERMADE_FX
   ```
6. Grant query privileges to your active deployment execution role (e.g., `ACCOUNTADMIN`, or your specific team workspace role) and click **Get**.

### B. Marketplace Dataset Schema Reference
The CoCo AI agent's semantic views look up the live timeseries tracking tables mounted from the data share. The application references the following schema structures to process the internal bank statements:

*   **Shared Database Table Target:** `TRADERMADE_FX.PUBLIC.FX_RATES_TIMESERIES`

| Column Name | Data Type | Description / Sample Output |
| :--- | :--- | :--- |
| **`BASE_CURRENCY`** | `STRING` | The core pivot token currency (e.g., `USD`) |
| **`QUOTE_CURRENCY`** | `STRING` | The local evaluated transactional token currency (e.g., `EUR`, `INR`) |
| **`EXCHANGE_RATE`** | `NUMBER(12,6)` | The active multiplier index used to cross-reference (e.g., `1.095400`) |
| **`TIMESTAMP`** | `TIMESTAMP` | The logged update timeline matrix for currency verification |

### C. Live CoCo Ontology Analytics Background Query
When an auditor types an account inquiry on your frontend dashboard, the semantic view background framework automatically fires an integrated query merging local files with the marketplace data share to compute the cross-border base value:

```sql
SELECT 
    L.ACCOUNT_ID,
    L.TX_ID,
    L.AMOUNT AS LOCAL_AMOUNT,
    L.CURRENCY AS LOCAL_CURRENCY,
    -- Dynamically normalize multi-currency transactions back to a USD base limit metric
    CASE 
        WHEN L.CURRENCY = 'USD' THEN L.AMOUNT
        ELSE L.AMOUNT / COALESCE(M.EXCHANGE_RATE, 1)
    END AS NORMALIZED_AMOUNT_USD,
    L.DIRECTION,
    L.STATUS
FROM FINAI_AUDIT_DB.PUBLIC.BANK_LEDGER L
LEFT JOIN TRADERMADE_FX.PUBLIC.FX_RATES_TIMESERIES M
    ON L.CURRENCY = M.QUOTE_CURRENCY
    AND M.BASE_CURRENCY = 'USD'
ORDER BY L.TX_TIMESTAMP DESC;
```

---

## 🛠️ Project Setup & Installation (Ubuntu / Python 3.11)

### 1. Build Local Workspace Environments
```bash
# Clone the repository and enter workspace path
cd finai-auditor

# Build and activate Python 3.11 Virtual Environment
python3.11 -m venv venv
source venv/bin/activate

# Install secure application dependency modules
pip install --upgrade pip
pip install snowflake-cli snowflake-connector-python pandas streamlit python-dotenv tabulate
```

### 2. Configure Local Secrets Variable Shielding
Create a local `.env` file inside your repository root folder (this path is hidden from Git tracking via `.gitignore` configurations):
```env
SNOWFLAKE_USER=your_real_username
SNOWFLAKE_PASSWORD=your_real_password
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

### 3. Generate Local Datasets & Execute Cloud Seeding Ingestion
```bash
# Synthesize local mock bank statements and handbook manuals
python data/generate_mock_data.py

# Create database architectures and load datasets programmatically into Snowflake Cloud
python data/upload_to_snowflake.py
```

### 4. Build CoCo Index Foundations Natively
```bash
# Initialize application repo parameters
cortex init

# Build search tracking pipelines and configuration structures via non-interactive mode
cortex prompt "Create a cortex search service named finai_handbook_search pointing to the txt documentation files inside @finai_audit_stage."
cortex prompt "Build a semantic configuration view called global_finai_analytics that wraps our local BANK_LEDGER table while allowing access to the external exchange records in TRADERMADE_FX."
```

### 5. Launch the Graphical Presentation Frontend Interface
To review the user dashboard interface externally from your browser layout without system terminal blocking hooks:
```bash
python -m streamlit run app.py
```
Open **`http://localhost:8501`** inside your default browser window to interact with the application.

---

## ☁️ Deploying to the Data Cloud (Streamlit in Snowflake)
To push your dashboard app file smoothly onto the secure cloud infrastructure using the Snowflake CLI tool and temporary session bypass wrappers:
```bash
# Export active parameters to memory to prevent file pathing lookup locks
export SNOWFLAKE_ACCOUNT=\$(grep SNOWFLAKE_ACCOUNT .env | cut -d '=' -f2)
export SNOWFLAKE_USER=\$(grep SNOWFLAKE_USER .env | cut -d '=' -f2)
export SNOWFLAKE_PASSWORD=\$(grep SNOWFLAKE_PASSWORD .env | cut -d '=' -f2)
export SNOWFLAKE_ROLE=\$(grep SNOWFLAKE_ROLE .env | cut -d '=' -f2)
export SNOWFLAKE_WAREHOUSE=\$(grep SNOWFLAKE_WAREHOUSE .env | cut -d '=' -f2)

# Push the frontend app architecture directly to the cloud staging perimeter
./venv/bin/snow streamlit deploy --temporary-connection
```
Once complete, access your application inside the **Snowsight Web console UI** under **Projects ➔ Streamlit ➔ FinAI_Auditor_Dashboard**.

---

## 🧪 Evaluation Script & Test Cases

Use these three core prompts in the chat box to demonstrate the full capabilities of the copilot:

### Test Case 1: Cross-Border Velocity & Structuring Risk Evaluation
*   **Prompt to type:** `"Run a comprehensive compliance audit on account ACC_9988. Check for any cross-border velocity or structuring patterns that violate our regulatory playbook."`
• Expected AI Agent Action: The copilot queries the 3 high-frequency EUR deposit entries (totaling €11,000), references the TRADERMADE_FX live table to convert them to USD (~$12,150), and flags a Section 301, Paragraph A structuring violation because it crossed the statutory $10,000 baseline within 24 hours.
### Test Case 2: Unstructured Text Parsing & Liquidity Stress Detection
• **Prompt to type:** '"Are there any recent violations of Section 302 or accounts showing critical liquidity defalcation stress?"'
• Expected AI Agent Action: The copilot uses Cortex Search over the unstructured guidelines, identifies that Section 302, Paragraph B flags failed items matching NSF tokens, scans the BANK_LEDGER table, and automatically surfaces Account ACC_1122 due to its failed Rent Payment - NSF transaction row.
### Test Case 3: Grounded Baseline Compliance Verification
• **Prompt to type:** '"Analyze account ACC_1122 and evaluate if it complies with our overall financial safety baselines."'
• Expected AI Agent Action: Demonstrates that the AI doesn't hallucinate or flag clean data. The agent notes that while a single isolated NSF flag exists (from Test Case 2), the user's overall historical deposits and supermarket interactions reflect standard, compliant financial activity.