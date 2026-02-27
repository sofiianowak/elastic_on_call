import streamlit as st
import time
import json
import os
import sys
from datetime import datetime

# --- Elasticsearch Client ---
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

ES_URL = os.environ.get("ELASTICSEARCH_URL")
ES_API_KEY = os.environ.get("ELASTICSEARCH_API_KEY")

es_client = None
if ES_URL and ES_API_KEY:
    try:
        es_client = Elasticsearch(ES_URL, api_key=ES_API_KEY)
        es_client.info()  # Test connection
    except Exception:
        es_client = None

# ──────────────────────────── PAGE CONFIG ────────────────────────────
st.set_page_config(
    page_title="ElasticOnCall",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────── CUSTOM DARK THEME CSS ────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    /* Global */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .main-header h1 {
        color: #ffffff;
        font-size: 2rem;
        margin: 0;
        font-weight: 700;
    }
    .main-header p {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 0.5rem 0 0 0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #1a1a2e 100%);
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    /* Incident card in sidebar */
    .incident-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 0.8rem;
        margin-bottom: 0.6rem;
        transition: all 0.2s;
    }
    .incident-card:hover {
        border-color: #f97316;
        background: rgba(249,115,22,0.08);
    }
    .incident-card .sev-critical {
        color: #ef4444;
        font-weight: 700;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .incident-card .sev-warning {
        color: #f59e0b;
        font-weight: 700;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .incident-card h4 {
        margin: 0.3rem 0 0.2rem 0;
        font-size: 0.85rem;
        color: #f1f5f9 !important;
    }
    .incident-card .time {
        font-size: 0.7rem;
        color: #64748b !important;
    }

    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    .status-live {
        background: rgba(34,197,94,0.15);
        color: #22c55e;
        border: 1px solid rgba(34,197,94,0.3);
    }
    .status-disconnected {
        background: rgba(239,68,68,0.15);
        color: #ef4444;
        border: 1px solid rgba(239,68,68,0.3);
    }

    /* Metric cards */
    .metric-row {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        flex: 1;
        background: linear-gradient(135deg, rgba(15,12,41,0.9), rgba(36,36,62,0.9));
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .metric-card .label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-card .value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #ef4444;
        margin: 0.3rem 0;
    }
    .metric-card .value.ok {
        color: #22c55e;
    }
    .metric-card .delta {
        font-size: 0.75rem;
        color: #ef4444;
    }

    /* Tool call badges */
    .tool-call {
        background: rgba(59,130,246,0.1);
        border: 1px solid rgba(59,130,246,0.3);
        border-radius: 8px;
        padding: 0.6rem 1rem;
        margin: 0.4rem 0;
        font-size: 0.85rem;
        color: #93c5fd;
    }

    /* Action buttons area */
    .action-section {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────── SIDEBAR ────────────────────────────
with st.sidebar:
    st.markdown("## 🖥️ ElasticOnCall")
    st.markdown("**Agent Console**")

    # Connection status
    if es_client:
        st.markdown('<span class="status-badge status-live">● Elastic Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-disconnected">● Elastic Offline</span>', unsafe_allow_html=True)

    st.divider()

    st.markdown("### 📋 Active Incidents")
    # Simulated incident cards
    st.markdown("""
    <div class="incident-card">
        <span class="sev-critical">🔴 SEV-1 CRITICAL</span>
        <h4>Payment API Outage</h4>
        <div class="time">Triggered 15 min ago · payment-api</div>
    </div>
    <div class="incident-card">
        <span class="sev-warning">🟡 SEV-3 WARNING</span>
        <h4>Auth Service High Latency</h4>
        <div class="time">Triggered 2h ago · auth-service</div>
    </div>
    <div class="incident-card">
        <span class="sev-warning">🟡 SEV-3 WARNING</span>
        <h4>CDN Cache Miss Rate Elevated</h4>
        <div class="time">Triggered 4h ago · cdn-edge</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🔧 Agent Capabilities")
    st.markdown("""
    - 🔍 Query Elasticsearch logs
    - 🧠 Semantic ticket search
    - 📊 Live metric analysis
    - 🚀 Execute remediations
    - 📝 Draft Jira tickets
    """)

    st.divider()
    st.caption("ElasticOnCall v0.1 · Hackathon MVP")

# ──────────────────────────── MAIN HEADER ────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🚨 ElasticOnCall — SRE Resolution Agent</h1>
    <p>AI-powered incident triage and resolution. Powered by Elasticsearch Agent Builder.</p>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────── HELPER: REAL ES QUERIES ────────────────────────────
def query_es_logs(service="payment-api", minutes=30):
    """Query real error logs from Elasticsearch"""
    if not es_client:
        return None
    try:
        result = es_client.search(
            index="server-logs-mock",
            body={
                "size": 10,
                "sort": [{"@timestamp": "desc"}],
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"service": service}},
                            {"terms": {"level": ["ERROR", "FATAL"]}}
                        ]
                    }
                }
            }
        )
        return result["hits"]["hits"]
    except Exception:
        return None

def query_es_tickets(keyword="connection pool"):
    """Search historical tickets from Elasticsearch"""
    if not es_client:
        return None
    try:
        result = es_client.search(
            index="incident-tickets-mock",
            body={
                "size": 3,
                "query": {
                    "multi_match": {
                        "query": keyword,
                        "fields": ["title", "root_cause", "resolution", "tags"]
                    }
                }
            }
        )
        return result["hits"]["hits"]
    except Exception:
        return None

def get_es_log_stats():
    """Get aggregated stats from ES"""
    if not es_client:
        return None
    try:
        result = es_client.search(
            index="server-logs-mock",
            body={
                "size": 0,
                "aggs": {
                    "avg_latency": {"avg": {"field": "latency_ms"}},
                    "max_latency": {"max": {"field": "latency_ms"}},
                    "error_count": {
                        "filter": {"terms": {"level": ["ERROR", "FATAL"]}}
                    },
                    "total_count": {"value_count": {"field": "level"}}
                }
            }
        )
        aggs = result["aggregations"]
        return {
            "avg_latency": round(aggs["avg_latency"]["value"] or 0),
            "max_latency": round(aggs["max_latency"]["value"] or 0),
            "error_count": aggs["error_count"]["doc_count"],
            "total_count": aggs["total_count"]["value"]
        }
    except Exception:
        return None


# ──────────────────────────── SCENARIO DEFINITIONS ────────────────────────────

SCENARIOS = {
    "payment": {
        "name": "Payment API Outage",
        "service": "payment-api",
        "keywords": ["payment", "pay", "checkout", "transaction", "billing", "connection pool", "exhausted"],
        "tool_calls": [
            ('es_search_logs', 'index="server-logs-mock", query="payment-api level:ERROR OR FATAL", last="30m"'),
            ('es_semantic_search', 'index="incident-tickets-mock", query="ConnectionPoolExhaustedException"'),
        ],
        "ticket_search": "connection pool",
        "response_template": """
**🔍 Investigation Complete**

**Incident:** The `payment-api` service is experiencing **FATAL** errors — `Connection pool exhausted`. Average latency is **{avg_lat:,} ms** (peak: **{max_lat:,} ms**).

**Root Cause:** The service has exhausted its database connection pool to `prod-db-01.internal`. Current error rate: **{error_rate}%** ({err_count} errors detected).

**Historical Context:** Found matching incident **{ticket_id}** — same root cause occurred during a previous traffic spike. Resolution was to increase connection pool size and restart pods.

**Recommended Remediation:**
1. `kubectl set env deployment/payment-api DB_MAX_CONNECTIONS=200 -n prod`
2. `kubectl rollout restart deployment/payment-api -n prod`
3. Monitor latency recovery via Kibana dashboard.
""",
        "metrics": [
            {"label": "Avg Latency", "key": "avg_lat", "unit": "ms", "delta_fmt": "▲ {delta:,} ms above normal"},
            {"label": "Peak Latency", "key": "max_lat", "unit": "ms", "delta_fmt": "▲ critical threshold exceeded"},
            {"label": "Error Rate", "key": "error_rate", "unit": "%", "delta_fmt": "▲ {err_count} errors / 30 min"},
            {"label": "DB Pool", "key": "fixed", "value": "50/50", "delta_fmt": "⚠️ exhausted"},
        ],
        "actions": [
            {"label": "🚀 Restart Payment Pods", "key": "restart_payment", "type": "primary",
             "spinner": "Executing kubectl rollout restart...", "delay": 1.5,
             "success": "✅ **Action Executed:** `kubectl rollout restart deployment/payment-api -n prod`\n\nLatency is recovering. New pods are healthy.",
             "msg": "✅ Payment pods restarted successfully."},
            {"label": "📝 Create Jira Ticket", "key": "jira_payment", "type": "secondary",
             "spinner": "Creating Jira ticket...", "delay": 1.0,
             "success": "🎟️ **Ticket Created:** [INC-4105] Payment API Outage — Connection Pool Exhaustion\n\n→ Assigned to: **DevOps On-Call Queue**\n→ Priority: **P1 – Critical**",
             "msg": "🎟️ Jira ticket INC-4105 created."},
            {"label": "📈 Scale Up Replicas", "key": "scale_payment", "type": "secondary",
             "spinner": "Scaling deployment replicas...", "delay": 1.5,
             "success": "📈 **Scaled Up:** `kubectl scale deployment/payment-api --replicas=6 -n prod`\n\n6 replicas now running. Load distributed.",
             "msg": "📈 Scaled to 6 replicas."},
        ],
    },

    "cpu": {
        "name": "CPU Spike — Order Processing",
        "service": "order-processor",
        "keywords": ["cpu", "spike", "processor", "order", "high cpu", "load", "throttle", "node", "resource"],
        "tool_calls": [
            ('es_search_metrics', 'index="server-logs-mock", query="order-processor cpu_percent > 90", last="1h"'),
            ('es_semantic_search', 'index="incident-tickets-mock", query="CPU saturation OOM kill runaway loop"'),
        ],
        "ticket_search": "CPU memory OOM",
        "response_template": """
**🔍 Investigation Complete**

**Incident:** The `order-processor` service is hitting **CPU saturation** at **98.2%** across all nodes. Multiple pods are being **OOM-killed** and restarting in a crash loop.

**Root Cause:** A recent deployment (v2.14.3) introduced an infinite retry loop in the order reconciliation worker. When a downstream `inventory-api` call times out, the worker retries without backoff, consuming 100% CPU.

**Historical Context:** Found matching incident **{ticket_id}** — a similar CPU runaway occurred 6 weeks ago after a bad retry policy was deployed. Resolution was to rollback and add exponential backoff.

**Recommended Remediation:**
1. `kubectl rollout undo deployment/order-processor -n prod` (rollback to v2.14.2)
2. `kubectl set resources deployment/order-processor --limits=cpu=500m -n prod`
3. Patch the retry logic with exponential backoff before re-deploying.
""",
        "metrics": [
            {"label": "CPU Usage", "key": "fixed", "value": "98.2%", "delta_fmt": "▲ critical — all cores saturated"},
            {"label": "Pod Restarts", "key": "fixed", "value": "14", "delta_fmt": "▲ OOM-killed, crash loop"},
            {"label": "Memory", "key": "fixed", "value": "3.8 / 4 GB", "delta_fmt": "⚠️ 95% — near OOM"},
            {"label": "Queue Depth", "key": "fixed", "value": "12,847", "delta_fmt": "▲ backlog growing"},
        ],
        "actions": [
            {"label": "⏪ Rollback Deployment", "key": "rollback_cpu", "type": "primary",
             "spinner": "Executing kubectl rollout undo...", "delay": 2.0,
             "success": "✅ **Rollback Executed:** `kubectl rollout undo deployment/order-processor -n prod`\n\nReverted to v2.14.2. CPU dropping to normal levels.",
             "msg": "✅ Deployment rolled back to v2.14.2."},
            {"label": "📝 Create Post-Mortem", "key": "jira_cpu", "type": "secondary",
             "spinner": "Drafting post-mortem...", "delay": 1.0,
             "success": "🎟️ **Post-Mortem Created:** [PM-0089] CPU Runaway — Missing Backoff in Order Processor v2.14.3\n\n→ RCA Owner: **Backend Team**\n→ Follow-up: Add circuit breaker pattern",
             "msg": "🎟️ Post-mortem PM-0089 created."},
            {"label": "🔒 Set CPU Limits", "key": "limit_cpu", "type": "secondary",
             "spinner": "Applying resource limits...", "delay": 1.0,
             "success": "🔒 **Limits Applied:** `kubectl set resources deployment/order-processor --limits=cpu=500m,memory=2Gi -n prod`\n\nResource guardrails in place.",
             "msg": "🔒 CPU/memory limits applied."},
        ],
    },

    "auth": {
        "name": "Auth Service — Login Failures",
        "service": "auth-service",
        "keywords": ["auth", "login", "token", "jwt", "session", "401", "403", "unauthorized", "certificate", "ssl", "tls", "ldap", "sso", "password"],
        "tool_calls": [
            ('es_search_logs', 'index="server-logs-mock", query="auth-service status_code:401 OR 403", last="1h"'),
            ('es_semantic_search', 'index="incident-tickets-mock", query="TLS certificate expiry auth token validation"'),
        ],
        "ticket_search": "certificate TLS auth",
        "response_template": """
**🔍 Investigation Complete**

**Incident:** The `auth-service` is returning **401 Unauthorized** on **94%** of login attempts. Users are reporting they cannot log into the dashboard or mobile app.

**Root Cause:** The internal TLS certificate used by `auth-service` to communicate with the **LDAP/SSO provider** (`idp.internal.corp`) expired **47 minutes ago**. All token validation requests are failing with `SSL: CERTIFICATE_VERIFY_FAILED`.

**Historical Context:** Found matching incident **{ticket_id}** — an identical cert expiry happened 11 months ago. The team resolved it by rotating the cert and adding a 30-day expiry alert to PagerDuty.

**Recommended Remediation:**
1. `kubectl create secret tls auth-tls --cert=new-cert.pem --key=new-key.pem -n prod`
2. `kubectl rollout restart deployment/auth-service -n prod`
3. Add cert-manager auto-renewal: `kubectl apply -f cert-manager-issuer.yaml`
""",
        "metrics": [
            {"label": "Login Success", "key": "fixed", "value": "6%", "delta_fmt": "▼ 94% failure rate"},
            {"label": "401 Errors", "key": "fixed", "value": "8,429", "delta_fmt": "▲ last 60 minutes"},
            {"label": "Cert Expiry", "key": "fixed", "value": "EXPIRED", "delta_fmt": "⚠️ 47 min ago"},
            {"label": "Affected Users", "key": "fixed", "value": "~12,500", "delta_fmt": "▲ all regions"},
        ],
        "actions": [
            {"label": "🔐 Rotate TLS Certificate", "key": "rotate_cert", "type": "primary",
             "spinner": "Generating and applying new TLS certificate...", "delay": 2.5,
             "success": "✅ **Certificate Rotated:** New TLS cert applied via `cert-manager`.\n\nValidity: 365 days. Auto-renewal enabled at 30 days before expiry.",
             "msg": "✅ TLS certificate rotated successfully."},
            {"label": "🔄 Restart Auth Pods", "key": "restart_auth", "type": "secondary",
             "spinner": "Restarting auth-service pods...", "delay": 1.5,
             "success": "✅ **Pods Restarted:** `kubectl rollout restart deployment/auth-service -n prod`\n\nNew pods picking up the fresh certificate. Login success rate recovering.",
             "msg": "✅ Auth pods restarted."},
            {"label": "📝 Incident Report", "key": "jira_auth", "type": "secondary",
             "spinner": "Creating incident report...", "delay": 1.0,
             "success": "🎟️ **Incident Report:** [INC-4112] Auth Service — TLS Certificate Expiry\n\n→ Impact: 12,500 users, 47 min downtime\n→ Action Item: Implement cert-manager auto-renewal",
             "msg": "🎟️ Incident report INC-4112 filed."},
        ],
    },
}

def detect_scenario(user_input):
    """Route the user message to the most relevant scenario based on keywords."""
    text = user_input.lower()
    scores = {}
    for key, scenario in SCENARIOS.items():
        score = sum(1 for kw in scenario["keywords"] if kw in text)
        scores[key] = score
    best = max(scores, key=scores.get)
    # Default to payment if no keywords matched at all
    if scores[best] == 0:
        return "payment"
    return best


# ──────────────────────────── CHAT LOGIC ────────────────────────────

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "🚨 **Multiple Alerts Detected!**\n\n"
                   "• `payment-api` — Latency spiked above **18%** error rate (15 min ago)\n"
                   "• `order-processor` — CPU at **98%**, pods crash-looping (45 min ago)\n"
                   "• `auth-service` — **94%** login failures, possible cert expiry (2h ago)\n\n"
                   "Which incident would you like me to investigate? You can also ask me anything, e.g.:\n"
                   "- *\"Why is the payment service failing?\"*\n"
                   "- *\"Investigate the CPU spike\"*\n"
                   "- *\"Why can't users log in?\"*"
    })

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("E.g., Why is the payment service failing?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ─── Detect which scenario to use ───
    scenario_key = detect_scenario(prompt)
    scenario = SCENARIOS[scenario_key]

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        with st.spinner("🧠 Agent is thinking..."):
            # ─── STEP 1: Query ES Logs ───
            time.sleep(0.8)
            tc1 = scenario["tool_calls"][0]
            st.markdown(f'<div class="tool-call">🛠️ <b>Tool Call:</b> {tc1[0]}({tc1[1]})</div>', unsafe_allow_html=True)

            real_logs = query_es_logs(service=scenario["service"])
            time.sleep(1.0)

            if real_logs:
                with st.expander("📄 Raw Elasticsearch Response (3 sample hits)", expanded=False):
                    for hit in real_logs[:3]:
                        src = hit["_source"]
                        st.code(json.dumps(src, indent=2, default=str), language="json")

            # ─── STEP 2: Search Tickets ───
            tc2 = scenario["tool_calls"][1]
            st.markdown(f'<div class="tool-call">🛠️ <b>Tool Call:</b> {tc2[0]}({tc2[1]})</div>', unsafe_allow_html=True)

            real_tickets = query_es_tickets(keyword=scenario["ticket_search"])
            time.sleep(1.0)

            if real_tickets:
                with st.expander("🎫 Historical Ticket Match", expanded=False):
                    for hit in real_tickets[:2]:
                        src = hit["_source"]
                        st.code(json.dumps(src, indent=2, default=str), language="json")

            # ─── STEP 3: Build the Agent Response ───
            stats = get_es_log_stats()

            if stats:
                avg_lat = stats["avg_latency"]
                max_lat = stats["max_latency"]
                err_count = stats["error_count"]
                total = stats["total_count"]
                error_rate = round((err_count / total * 100), 1) if total > 0 else 0
            else:
                avg_lat, max_lat, err_count, error_rate = 5240, 12450, 28, 18.5

            ticket_id = "INC-4022"
            if real_tickets:
                ticket_id = real_tickets[0]["_source"].get("ticket_id", "INC-4022")

            assistant_response = scenario["response_template"].format(
                avg_lat=avg_lat, max_lat=max_lat,
                err_count=err_count, error_rate=error_rate,
                ticket_id=ticket_id
            )

            # Stream the response
            for chunk in assistant_response.split('\n'):
                full_response += chunk + '\n'
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.04)

            message_placeholder.markdown(full_response)

        # ─── METRICS DASHBOARD ───
        st.divider()
        st.markdown(f"### 📊 Live Incident Metrics — `{scenario['service']}`")

        metrics = scenario["metrics"]
        metric_html = '<div class="metric-row">'
        for m in metrics:
            if m["key"] == "fixed":
                val = m["value"]
            elif m["key"] == "avg_lat":
                val = f"{avg_lat:,} ms"
            elif m["key"] == "max_lat":
                val = f"{max_lat:,} ms"
            elif m["key"] == "error_rate":
                val = f"{error_rate}%"
            else:
                val = "—"

            delta_text = m["delta_fmt"].format(
                delta=avg_lat - 250 if "delta" in m["delta_fmt"] else 0,
                err_count=err_count
            )

            metric_html += f'''
            <div class="metric-card">
                <div class="label">{m["label"]}</div>
                <div class="value">{val}</div>
                <div class="delta">{delta_text}</div>
            </div>'''
        metric_html += '</div>'

        st.markdown(metric_html, unsafe_allow_html=True)
        st.caption(f"Data sourced from `server-logs-mock` index in Elasticsearch · Scenario: **{scenario['name']}**")

        # ─── ACTION BUTTONS ───
        st.markdown("### ⚡ Execute Remediation")
        actions = scenario["actions"]
        cols = st.columns(len(actions))

        for i, act in enumerate(actions):
            with cols[i]:
                btn_type = "primary" if act["type"] == "primary" else "secondary"
                if st.button(act["label"], use_container_width=True, type=btn_type, key=act["key"]):
                    st.session_state.action_taken = act["key"]

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# ─── Handle Action Callbacks ───
if "action_taken" in st.session_state:
    action_key = st.session_state.action_taken
    del st.session_state.action_taken

    # Find the action definition across all scenarios
    action_def = None
    for sc in SCENARIOS.values():
        for act in sc["actions"]:
            if act["key"] == action_key:
                action_def = act
                break
        if action_def:
            break

    if action_def:
        with st.chat_message("assistant"):
            with st.spinner(action_def["spinner"]):
                time.sleep(action_def["delay"])
            if "Ticket" in action_def["success"] or "Post-Mortem" in action_def["success"] or "Report" in action_def["success"]:
                st.info(action_def["success"])
            else:
                st.success(action_def["success"])
            msg = action_def["msg"]

        st.session_state.messages.append({"role": "assistant", "content": msg})
