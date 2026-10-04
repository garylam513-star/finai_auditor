import os
import json
from typing import Any, Dict, List

import pandas as pd
import requests
import snowflake.connector
import streamlit as st
from dotenv import load_dotenv
from snowflake.core import Root

load_dotenv()

ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT", "")
USER = os.getenv("SNOWFLAKE_USER", "")
PASSWORD = os.getenv("SNOWFLAKE_PASSWORD", "")
WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
ROLE = os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN")
HOST = f"{ACCOUNT}.snowflakecomputing.com"

SEMANTIC_VIEW = "FINAI_AUDIT_DB.PUBLIC.GLOBAL_FINAI_ANALYTICS"
SEARCH_SERVICE = "finai_handbook_search"
SEARCH_DB = "FINAI_AUDIT_DB"
SEARCH_SCHEMA = "PUBLIC"
LLM_MODEL = "llama3.1-70b"

# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def get_connection() -> snowflake.connector.SnowflakeConnection:
    if "conn" not in st.session_state or st.session_state.conn is None:
        st.session_state.conn = snowflake.connector.connect(
            user=USER,
            password=PASSWORD,
            account=ACCOUNT,
            host=HOST,
            port=443,
            warehouse=WAREHOUSE,
            role=ROLE,
        )
    return st.session_state.conn


# ---------------------------------------------------------------------------
# Cortex Analyst  (REST API  ->  semantic view)
# ---------------------------------------------------------------------------

def send_analyst_message(question: str) -> Dict[str, Any]:
    conn = get_connection()
    request_body = {
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": question}]}
        ],
        "semantic_view": SEMANTIC_VIEW,
    }
    resp = requests.post(
        url=f"https://{HOST}/api/v2/cortex/analyst/message",
        json=request_body,
        headers={
            "Authorization": f'Snowflake Token="{conn.rest.token}"',
            "Content-Type": "application/json",
        },
    )
    if resp.status_code >= 400:
        raise Exception(f"Analyst API error {resp.status_code}: {resp.text}")
    return resp.json()


def run_analyst(question: str) -> Dict[str, Any]:
    response = send_analyst_message(question)
    content = response.get("message", {}).get("content", [])
    result = {"text": "", "sql": "", "df": None}
    for block in content:
        if block.get("type") == "text":
            result["text"] += block.get("text", "")
        elif block.get("type") == "sql":
            sql = block.get("statement", "")
            result["sql"] = sql
            if sql:
                conn = get_connection()
                try:
                    cur = conn.cursor()
                    cur.execute(sql)
                    cols = [desc[0] for desc in cur.description]
                    result["df"] = pd.DataFrame(cur.fetchall(), columns=cols)
                    cur.close()
                except Exception as e:
                    result["text"] += f"\n\nSQL execution error: {e}"
        elif block.get("type") == "suggestion":
            suggestions = block.get("suggestions", [])
            if suggestions:
                result["text"] += "\n\nSuggested questions:\n" + "\n".join(
                    f"- {s}" for s in suggestions
                )
    return result


# ---------------------------------------------------------------------------
# Cortex Search  (handbook regulatory citations)
# ---------------------------------------------------------------------------

def search_handbook(query: str, limit: int = 3) -> List[str]:
    conn = get_connection()
    root = Root(conn)
    svc = (
        root.databases[SEARCH_DB]
        .schemas[SEARCH_SCHEMA]
        .cortex_search_services[SEARCH_SERVICE]
    )
    resp = svc.search(query=query, columns=["chunk"], limit=limit)
    results = resp.results if hasattr(resp, "results") else resp.get("results", [])
    return [r.get("chunk", "") if isinstance(r, dict) else str(r) for r in results]


# ---------------------------------------------------------------------------
# LLM synthesis
# ---------------------------------------------------------------------------

def synthesize_report(
    question: str,
    analyst_result: Dict[str, Any],
    citations: List[str],
) -> str:
    data_summary = ""
    if analyst_result.get("text"):
        data_summary += analyst_result["text"] + "\n"
    if analyst_result.get("df") is not None and not analyst_result["df"].empty:
        data_summary += "\nQuery results:\n" + analyst_result["df"].to_markdown(index=False)

    citation_text = "\n---\n".join(citations) if citations else "No matching regulatory text found."

    prompt = f"""You are FinAI-Auditor, an enterprise compliance analyst.
A user asked: "{question}"

DATA FINDINGS (from the bank ledger and FX rates):
{data_summary}

REGULATORY HANDBOOK CITATIONS:
{citation_text}

Instructions:
- Produce a concise Markdown audit report.
- If the data shows a violation, cite the specific Section and Paragraph from the handbook.
- Include a summary table of the relevant transactions if data was returned.
- If no violation is found, state that clearly.
- Do not fabricate data or citations beyond what is provided above."""

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT SNOWFLAKE.CORTEX.COMPLETE(%s, %s)",
        (LLM_MODEL, prompt),
    )
    result = cur.fetchone()[0]
    cur.close()
    return result


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------

st.set_page_config(page_title="FinAI-Auditor", layout="wide")
st.title("FinAI-Auditor: Enterprise Risk & Regulatory Copilot")
st.caption("AI-powered banking compliance platform  |  Cortex Analyst + Cortex Search + LLM")

with st.sidebar:
    st.header("System Controls")
    try:
        conn = get_connection()
        st.success("Cloud Database: Connected")
    except Exception:
        st.error("Cloud Database: Disconnected")

    st.success("Marketplace Share: TRADERMADE FX Active")
    st.success("Cortex Search: finai_handbook_search")
    st.success(f"Semantic View: {SEMANTIC_VIEW}")

    st.subheader("Monitored Accounts")
    try:
        cur = get_connection().cursor()
        cur.execute(
            "SELECT ACCOUNT_ID, COUNT(*) AS FLAGS FROM FINAI_AUDIT_DB.PUBLIC.BANK_LEDGER "
            "WHERE STATUS = 'FAILED' OR DIRECTION = 'IN' "
            "GROUP BY ACCOUNT_ID ORDER BY FLAGS DESC LIMIT 5"
        )
        alerts = pd.DataFrame(cur.fetchall(), columns=["ACCOUNT_ID", "FLAGS"])
        cur.close()
        for _, row in alerts.iterrows():
            st.warning(f"{row['ACCOUNT_ID']}  ({row['FLAGS']} flagged txns)")
    except Exception:
        st.info("No account data available")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Enter your audit investigation inquiry..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Querying semantic view, searching regulatory handbook, synthesizing report..."):
            # 1. Cortex Analyst
            analyst_result = run_analyst(prompt)

            # 2. Cortex Search
            citations = search_handbook(prompt)

            # 3. LLM synthesis
            report = synthesize_report(prompt, analyst_result, citations)

        # Display the report
        st.markdown(report)

        # Show the raw data if available
        if analyst_result.get("df") is not None and not analyst_result["df"].empty:
            with st.expander("Raw Query Results"):
                st.dataframe(analyst_result["df"], use_container_width=True)

        if analyst_result.get("sql"):
            with st.expander("Generated SQL"):
                st.code(analyst_result["sql"], language="sql")

    st.session_state.messages.append({"role": "assistant", "content": report})
