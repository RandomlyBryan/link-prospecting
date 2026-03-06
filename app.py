import streamlit as st
import pandas as pd
import requests
import re

# --- 1. CONFIG & SECRETS ---
st.set_page_config(page_title="Link Building App", layout="wide", page_icon="🔗")

# Logic to handle API Key automatically
if "SERPER_API_KEY" in st.secrets:
    API_KEY = st.secrets["SERPER_API_KEY"]
else:
    API_KEY = st.sidebar.text_input("Enter Serper.dev API Key", type="password")

# --- 2. HELPER FUNCTIONS ---
def clean_domain(url):
    url = url.strip().lower()
    url = re.sub(r"https?://(www\.)?", "", url)
    return url.split('/')[0]

def check_api_health(api_key):
    """Briefly pings the API to ensure the key is active."""
    if not api_key:
        return "Missing"
    url = "https://google.serper.dev/search"
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    try:
        # Minimal query to test connection
        response = requests.post(url, json={"q": "test", "num": 1}, headers=headers, timeout=5)
        if response.status_code == 200:
            return "Connected"
        else:
            return "Invalid Key"
    except:
        return "Offline"

# --- 3. SIDEBAR UI ---
with st.sidebar:
    st.title("Settings")
    
    # Input Area
    domains_input = st.text_area("Prospect Domains", placeholder="example.com", height=150)
    keywords_input = st.text_area("Keywords / Topics", placeholder="SEO tips", height=120)
    
    st.divider()
    
    # The primary action button
    search_button = st.button("Find Opportunities", type="primary", use_container_width=True)

    # --- STATUS CHECK SECTION ---
    st.write("### System Status")
    status = check_api_health(API_KEY)
    
    if status == "Connected":
        st.success("● API Connected")
    elif status == "Invalid Key":
        st.error("● Invalid API Key")
    elif status == "Missing":
        st.warning("● Waiting for Key")
    else:
        st.error("● Connection Failed")

# --- 4. MAIN DASHBOARD ---
st.title("🚀 Link Building Opportunity Finder")

if search_button:
    if status != "Connected":
        st.error("Please ensure your API key is correct before searching.")
    elif not domains_input or not keywords_input:
        st.warning("Please provide both domains and keywords.")
    else:
        # Process Inputs
        target_domains = [clean_domain(d) for d in domains_input.split('\n') if d.strip()]
        keywords = [k.strip() for k in keywords_input.split('\n') if k.strip()]
        
        results_list = []
        progress_bar = st.progress(0)
        
        total = len(target_domains) * len(keywords)
        count = 0
        
        for domain in target_domains:
            for kw in keywords:
                count += 1
                # Search logic
                url = "https://google.serper.dev/search"
                payload = {"q": f"site:{domain} {kw}", "num": 5}
                headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
                
                try:
                    res = requests.post(url, json=payload, headers=headers).json()
                    for item in res.get('organic', []):
                        results_list.append({
                            "Domain": domain,
                            "Keyword": kw,
                            "Title": item.get('title'),
                            "URL": item.get('link')
                        })
                except:
                    pass
                progress_bar.progress(count / total)

        if results_list:
            st.dataframe(pd.DataFrame(results_list), use_container_width=True)
            csv = pd.DataFrame(results_list).to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "opps.csv", "text/csv", use_container_width=True)
        else:
            st.info("No articles found.")
