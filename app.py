import streamlit as st
import os
from groq import Groq
import time

st.set_page_config(page_title="Mehar Super Agent v2", layout="wide")

# --- LOGIN ---
ADMIN_USER = st.secrets.get("ADMIN_USER", "mehar_admin_9x")
ADMIN_PASS = st.secrets.get("ADMIN_PASS", "Strong#2026Pass")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Mehar Super Agent v2 - Locked")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u == ADMIN_USER and p == ADMIN_PASS:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Wrong login Bhai!")
    st.stop()

# --- LOGGED IN ---
st.title("Mehar Mart V5 FINAL JOINT - Catalog + Ad Studio V4.1")
st.success("Logged in Bhai!")

tab1, tab2 = st.tabs(["SEO Generator", "Store Manager"])

with tab1:
    st.subheader("SEO Generator - Groq AI")
    product_title = st.text_input("Product Title *", value="Mehar Sidr Honey 500g")
    features = st.text_area("Features / Details", value="100% pure, cold extracted, from Karak, for winter", height=100)
    
    if st.button("Generate SEO — Groq (timeout 30s, 1 retry)"):
        if not product_title:
            st.warning("Bhai Product Title likho!")
        else:
            try:
                groq_key = st.secrets.get("GROQ_API_KEY")
                if not groq_key:
                    st.error("GROQ_API_KEY secrets me nahi hai Bhai!")
                else:
                    client = Groq(api_key=groq_key)
                    
                    prompt = f"""
You are SEO expert for Mehar Mart Peshawar.
Product: {product_title}
Features: {features}
Task: Generate:
1. SEO Title (max 60 chars, attractive)
2. SEO Description (max 160 chars, for Daraz/Shopify)
3. 5 Bullet Points (benefits)
4. 10 Tags/Keywords

Format in Urdu + English mix for Pakistani customer.
"""
                    with st.spinner("Groq AI soch raha hai Bhai..."):
                        completion = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.7,
                            max_tokens=800,
                        )
                        result = completion.choices[0].message.content
                        st.markdown("### Result:")
                        st.write(result)
                        st.success("Ho gaya Bhai! Copy kar lo!")
            except Exception as e:
                st.error(f"Groq error: {e}")

with tab2:
    st.subheader("Store Manager")
    st.info("Yahan baad me products add karenge Bhai!")
    st.text_input("Test Product Name")
