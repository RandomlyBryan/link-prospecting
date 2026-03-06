import streamlit as st
import pandas as pd
import requests
import re

# --- 1. CONFIG & SECRETS ---
st.set_page_config(page_title="Link Building App", layout="wide", page_icon="🔗")

# Logic to handle API Key automatically
if "SERPER_API_KEY" in st.secrets:
    API_KEY = st.secrets["SERPER_API_KEY"]
    api_status = "✅ API Connected via Secrets"
else:
    # Fallback if secrets aren't set up yet
    API_KEY = st.sidebar.text_input("Enter Serper.dev API Key", type="password")
    api_status = "⚠️ Enter API Key to begin"

# --- 2. HELPER FUNCTIONS ---
def clean_domain(url):
    """Extracts root domain for the site: operator."""
    url = url.strip().lower()
    url = re.sub(r"https?://(www\.)?", "", url)
    return url.split('/')[0]

def search_google(domain, keyword, api_key):
    """Hits Serper.dev for broad matching site operators."""
    url = "https://google.serper.dev/search"
    # We use broad site:domain keyword (no quotes) as requested
    payload = {"q": f"site:{domain} {keyword}", "num": 5}
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json().get('organic', [])
    except Exception as e:
        st.error(f"Error searching {domain}: {e}")
        return []

# --- 3. SIDEBAR UI ---
with st.sidebar:
    st.title("Settings")
    st.info(api_status)
    
    st.divider()
    
    domains_input = st.text_area(
        "Prospect Domains", 
        placeholder="ivyrx.com\nmorgen.so\nportainer.io", 
        height=200,
        help="Paste one domain or URL per line."
    )
    
    keywords_input = st.text_area(
        "Keywords / Topics", 
        placeholder="weight loss\ntime management\ncontainer security", 
        height=150,
        help="Broad keywords to find relevant articles."
    )
    
    st.divider()
    
    # The primary action button
    search_button = st.button("Find Opportunities", type="primary", use_container_width=True)

# --- 4. MAIN DASHBOARD ---
st.title("🚀 Link Building Opportunity Finder")
st.markdown("Find relevant articles on target domains for link insertions or guest post ideas.")

if search_button:
    if not API_KEY:
        st.error("Please provide a Serper.dev API key in the sidebar or Secrets.")
    elif not domains_input or not keywords_input:
        st.warning("Please fill in both the Domains and Keywords fields.")
    else:
        # Process Inputs
        raw_domains = [d.strip() for d in domains_input.split('\n') if d.strip()]
        target_domains = [clean_domain(d) for d in raw_domains]
        keywords = [k.strip() for k in keywords_input.split('\n') if k.strip()]
        
        results_list = []
        
        # Progress UI
        total_tasks = len(target_domains) * len(keywords)
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        count = 0
        for domain in target_domains:
            for kw in keywords:
                count += 1
                status_text.text(f"Searching {domain} for '{kw}'... ({count}/{total_tasks})")
                
                organic_results = search_google(domain, kw, API_KEY)
                
                if organic_results:
                    for res in organic_results:
                        results_list.append({
                            "Domain": domain,
                            "Keyword": kw,
                            "Page Title": res.get('title'),
                            "URL": res.get('link'),
                            "Snippet": res.get('snippet')
                        })
                
                progress_bar.progress(count / total_tasks)

        status_text.empty()
        
        # Display Results
        if results_list:
            df = pd.DataFrame(results_list)
            st.success(f"Successfully found {len(df)} relevant pages!")
            
            # Interactive Dataframe
            st.dataframe(
                df, 
                use_container_width=True,
                column_config={
                    "URL": st.column_config.LinkColumn("Article Link")
                }
            )
            
            # Download Section
            st.divider()
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Opportunities CSV",
                data=csv,
                file_name="link_opportunities.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No relevant articles found. Try using broader keywords.")

# --- 5. INITIAL STATE ---
if not search_button:
    st.write("---")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Status", "Ready")
    col_b.metric("Mode", "Broad Match")
    col_c.metric("Engine", "Serper API")