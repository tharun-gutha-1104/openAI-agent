import streamlit as st
import asyncio
from agent import process_customer_query  

# Streamlit UI
st.set_page_config(page_title="📦 E-Commerce Query Analyzer", layout="centered")

st.title("🛍️ E-Commerce Query Analyzer")
st.markdown("Enter a customer query to extract useful metadata and validate it using an AI Guardrail.")

query = st.text_area("Customer Query", height=150, placeholder="e.g., I ordered a Kindle two weeks ago, but it hasn't arrived...")

if st.button("Analyze"):
    if not query.strip():
        st.warning("Please enter a customer query.")
    else:
        with st.spinner("Analyzing query..."):
            result = asyncio.run(process_customer_query(query))

        if result["success"]:
            st.success("✅ Query is valid. Metadata extracted:")
            metadata = result["data"]
            st.json(metadata.model_dump()) 
        else:
            st.error(f"❌ {result['error']}")
