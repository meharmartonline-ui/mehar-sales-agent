"""Mehar Super Agent v2 — hardened Streamlit prototype.

This is not a production payment service, PWA, or webhook server. See README.md.
"""
from __future__ import annotations

import hmac
import os
import re
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

import store_manager

st.set_page_config(page_title="Mehar Super Agent v2", page_icon="🚀", layout="wide", initial_sidebar_state="collapsed")

NAVY, GOLD = "#0A1931", "#D4AF37"
DB_PATH = Path(os.getenv("MEHAR_DB_PATH", "leads.db")).expanduser()
RATE_LIMIT = 5
RATE_WINDOW_SECONDS = 60
LOGIN_LIMIT = 5
LOGIN_WINDOW_SECONDS = 300

st.markdown(
f"""<style>
.stApp {{background:{NAVY}; color:#fff}}
.stApp h1,.stApp h2,.stApp h3,.stApp label,.stApp p,.stApp li {{color:#fff}}
[data-testid="stSidebar"] {{background:#081427}}
.stButton>button {{background:{GOLD};color:{NAVY};font-weight:700;width:100%;min-height:2.75rem}}
@media(max-width:768px) {{
  .block-container {{padding:1rem 0.8rem}}
  [data-testid="stHorizontalBlock"] {{flex-wrap:wrap;gap:0.75rem}}
  [data-testid="stColumn"] {{min-width:100%!important;flex:1 1 100%!important}}
  input,textarea {{font-size:16px!important}}
  [data-baseweb="tab-list"] {{overflow-x:auto}}
}}
</style>""",
    unsafe_allow_html=True,
)


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def db_connect() -> sqlite3.Connection:
    """Open a short-lived SQLite connection; do not share connections across sessions."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(DB_PATH), timeout=10, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 10000")
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def db_session():
    """Yield a connection and always close it, including on exceptions."""
    conn = db_connect()
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with db_session() as conn:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("""CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 100),
            phone TEXT NOT NULL CHECK(length(phone) BETWEEN 3 AND 20),
            niche TEXT NOT NULL CHECK(length(niche) BETWEEN 1 AND 100),
            created_at TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS usage_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            action TEXT NOT NULL,
            ts REAL NOT NULL
        )""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_user_ts ON usage_log(user, ts)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at)")


def check_and_log_rate_limit(user: str, action: str, limit: int = RATE_LIMIT, window: int = RATE_WINDOW_SECONDS) -> bool:
    """Atomically enforce a per-user rolling-window limit across app sessions/processes using SQLite."""
    now = time.time()
    cutoff = now - window
    with db_session() as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            conn.execute("DELETE FROM usage_log WHERE action = ? AND ts < ?", (action, cutoff - window))
            count = conn.execute(
                "SELECT COUNT(*) FROM usage_log WHERE user = ? AND action = ? AND ts > ?",
                (user, action, cutoff),
            ).fetchone()[0]
            if count >= limit:
                conn.execute("COMMIT")
                return False
            conn.execute("INSERT INTO usage_log(user, action, ts) VALUES (?, ?, ?)", (user, action, now))
            conn.execute("COMMIT")
            return True
        except Exception:
            conn.execute("ROLLBACK")
            raise


def get_secret(name: str) -> str:
    """Read from environment first, then Streamlit secrets; tolerate missing secrets file."""
    value = os.getenv(name, "").strip()
    if value:
        return value
    try:
        return str(st.secrets.get(name, "")).strip()
    except Exception:
        return ""


def groq_generate(description: str) -> str:
    api_key = get_secret("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY configured nahi hai. Environment variable ya Streamlit secrets mein set karein.")
    try:
        from groq import Groq
    except ImportError as exc:
        raise RuntimeError("Groq package installed nahi. requirements.txt install karein.") from exc

    client = Groq(api_key=api_key, timeout=30.0, max_retries=1)
    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        messages=[
            {"role": "system", "content": (
                "Write useful, honest SEO copy. Do not invent product specifications, certifications, "
                "warranties, discounts, medical claims, or performance claims. If facts are missing, "
                "avoid stating them. Return a short title, meta description, and keywords."
            )},
            {"role": "user", "content": f"Create SEO copy from this product description:\n{description}"},
        ],
        temperature=0.4,
        max_tokens=700,
    )
    result = response.choices[0].message.content if response.choices else None
    if not result or not result.strip():
        raise RuntimeError("AI service ne empty response diya. Dobara try karein.")
    return result.strip()


init_db()
store_manager.init_tables(db_session)

# Fail closed: no built-in admin username or password.
admin_user = get_secret("ADMIN_USER")
admin_pass = get_secret("ADMIN_PASS")
if not admin_user or not admin_pass:
    st.title("🔐 Mehar Super Agent v2")
    st.error("Admin login configured nahi hai. ADMIN_USER aur ADMIN_PASS environment variables ya Streamlit secrets mein set karein.")
    st.code('ADMIN_USER="your-admin-user"\nADMIN_PASS="use-a-long-unique-password"\nGROQ_API_KEY="your-groq-api-key"', language="toml")
    st.stop()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "auth_user" not in st.session_state:
    st.session_state.auth_user = ""

if not st.session_state.authenticated:
    st.title("🔐 Login — Mehar Super Agent v2")
    with st.form("login_form"):
        username = st.text_input("Username", max_chars=100)
        password = st.text_input("Password", type="password", max_chars=256)
        login_clicked = st.form_submit_button("Login")
    if login_clicked:
        if not check_and_log_rate_limit("__login__", "login", LOGIN_LIMIT, LOGIN_WINDOW_SECONDS):
            st.error("Bohat zyada login attempts. 5 minute baad dobara try karein.")
        else:
            valid_user = hmac.compare_digest(username.encode("utf-8"), admin_user.encode("utf-8"))
            valid_pass = hmac.compare_digest(password.encode("utf-8"), admin_pass.encode("utf-8"))
            if valid_user and valid_pass:
                st.session_state.authenticated = True
                st.session_state.auth_user = username
                st.rerun()
            else:
                st.error("Credentials ghalat hain.")
    st.caption("Single-admin prototype authentication. Public production deployment requires stronger identity, session and access controls.")
    st.stop()

with st.sidebar:
    st.write(f"👤 {st.session_state.auth_user} | Admin session")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.auth_user = ""
        st.rerun()
    st.divider()
    st.caption("SQLite: local database | SEO limit: 5 attempts / rolling 60 seconds")

st.title("Mehar Super Agent v2")
st.caption("Hardened prototype — live payment verification, production webhooks, and installable PWA are not included.")

tab1, tab2, tab3, tab4, *store_tabs = st.tabs(["📦 Leads DB", "🔎 SEO (Rate Limited)", "💳 Easypaisa", "🔗 Webhooks / PWA",
                                               "🛍️ Store", "🧺 Products", "🎨 Theme", "📊 Orders", "🚀 Publish"])

with tab1:
    st.subheader("Leads — SQLite database")
    with st.form("lead_form", clear_on_submit=True):
        name = st.text_input("Name", max_chars=100).strip()
        phone = st.text_input("Phone", max_chars=20).strip()
        niche = st.text_input("Niche", max_chars=100).strip()
        submitted = st.form_submit_button("Save Lead to DB")
    if submitted:
        if not name or not phone or not niche:
            st.error("Name, phone aur niche teenon zaroori hain.")
        elif not re.fullmatch(r"\+?[0-9 \-]+", phone) or not 7 <= len(re.sub(r"\D", "", phone)) <= 15:
            st.error("Phone number check karein (7-15 digits, sirf digits/+/space/-).")
        else:
            try:
                with db_session() as conn:
                    conn.execute(
                        "INSERT INTO leads(name, phone, niche, created_at) VALUES (?, ?, ?, ?)",
                        (name, phone, niche, utc_iso()),
                    )
                st.success("Lead local SQLite database mein save ho gayi.")
            except sqlite3.Error:
                st.error("Database mein save nahi ho saka. Server logs check karein.")
    try:
        with db_session() as conn:
            rows = conn.execute("SELECT id, name, phone, niche, created_at FROM leads ORDER BY id DESC LIMIT 1000").fetchall()
        st.dataframe(pd.DataFrame([dict(row) for row in rows]), use_container_width=True, hide_index=True)
        st.caption("Showing latest 1,000 leads. Database file local disk par hai; deployment par persistent storage/backup separately verify karein.")
    except sqlite3.Error:
        st.error("Leads read nahi ho sake. Server logs check karein.")

with tab2:
    st.subheader("SEO copy generator")
    st.caption("Limit: maximum 5 attempts per signed-in admin in a rolling 60-second window. Description Groq ko bheji jayegi jab aap generate press karenge.")
    description = st.text_area("Product Description", max_chars=2000, height=150, placeholder="Product ki asli details yahan likhein...")
    if st.button("Generate SEO", key="generate_seo"):
        if not description.strip():
            st.warning("Pehle product description enter karein.")
        elif not check_and_log_rate_limit(st.session_state.auth_user, "seo"):
            st.error("Rate limit reached: 60 seconds wait karein.")
        else:
            st.session_state.pop("last_seo_result", None)  # no stale result under a new error
            with st.spinner("SEO copy generate ho rahi hai..."):
                try:
                    st.session_state.last_seo_result = groq_generate(description.strip())
                except RuntimeError as exc:
                    st.error(str(exc))
                except Exception:
                    st.error("AI provider request fail hui. API key/model/network configuration check karein; sensitive provider details hide ki gayi hain.")
            if st.session_state.get("last_seo_result"):
                st.markdown(st.session_state.last_seo_result)
    elif st.session_state.get("last_seo_result"):
        st.markdown(st.session_state.last_seo_result)

with tab3:
    st.subheader("Easypaisa payment verification")
    st.warning("Not connected: yeh app Easypaisa transaction ko verify, charge, refund, ya approve nahi karti.")
    st.write("Real verification ke liye Easypaisa ke official merchant/API access, server-side credentials, signed callback or authenticated verification flow, duplicate-transaction protection, aur reconciliation required hain.")
    trx_id = st.text_input("Transaction reference (demo only)", max_chars=100)
    if st.button("Check reference (demo only)"):
        if not trx_id.strip():
            st.error("Reference enter karein.")
        else:
            st.info("Reference sirf input hua hai; payment status verify nahi hua. Isay paid/approved na samjhein.")

with tab4:
    st.subheader("Webhook and PWA status")
    st.info("Webhook endpoints is Streamlit app mein implemented nahi hain. Neeche sirf implementation checklist hai.")
    st.markdown("""
**WhatsApp webhook production checklist**
- Separate backend endpoint (e.g. FastAPI) with provider verification challenge.
- Validate request signature against the raw request body using the official provider secret.
- Enforce idempotency/deduplication on provider message ID; use database transactions.
- Authenticate admin actions, validate payload schemas, rate-limit abuse, and avoid logging secrets/PII.
- Return provider-required HTTP status codes and configure retries/monitoring.

**PWA status**
- `manifest.json` and `sw.js` generated inside a Streamlit Python process are not automatically served or linked by Streamlit.
- A proper installable PWA needs a supported frontend/static hosting setup, HTTPS, valid manifest/icons, and a carefully scoped service worker.
- The unsafe `fetch`-everything service worker pattern from the submitted code is intentionally removed; it is not a safe offline cache.
""")

store_manager.render(store_tabs, db_session, utc_iso)
