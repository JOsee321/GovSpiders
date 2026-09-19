"""
GovSpiders Threat Intelligence Dashboard.
Module for visualizing JSON scan results.
"""

import json
import streamlit as st
import pandas as pd
import plotly.express as px

def load_data(uploaded_file):
    """
    Load JSON data from an uploaded file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object.
        
    Returns:
        List of dictionaries containing scan results.
    """
    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
            if isinstance(data, list):
                return data
            return []
        except Exception as e:
            st.error(f"Failed to parse JSON: {e}")
            return []
    return []

def calculate_metrics(data):
    """
    Calculate Key Performance Indicators from the scan data.
    
    Args:
        data: List of dictionaries containing scan results.
        
    Returns:
        Tuple containing total scanned, total vulnerable, and total syndicate links.
    """
    total_scanned = len(data)
    total_vulnerable = sum(1 for item in data if item.get("status") == "Vulnerable")
    
    total_syndicate_links = 0
    for item in data:
        if item.get("status") == "Vulnerable":
            links = item.get("syndicate_links", [])
            total_syndicate_links += len(links)
            
    return total_scanned, total_vulnerable, total_syndicate_links

def extract_syndicate_dataframe(data):
    """
    Extract vulnerable targets and their syndicate links into a Pandas DataFrame.
    
    Args:
        data: List of dictionaries containing scan results.
        
    Returns:
        Pandas DataFrame formatted for display.
    """
    rows = []
    for item in data:
        if item.get("status") == "Vulnerable":
            domain = item.get("url", "")
            score = item.get("score", 0)
            links = item.get("syndicate_links", [])
            
            if not links:
                rows.append({
                    "Domain Target": domain,
                    "Skor Ancaman": score,
                    "Tautan Afiliator (Sindikat)": "-"
                })
            else:
                for link in links:
                    rows.append({
                        "Domain Target": domain,
                        "Skor Ancaman": score,
                        "Tautan Afiliator (Sindikat)": link
                    })
                    
    if not rows:
        return pd.DataFrame(columns=["Domain Target", "Skor Ancaman", "Tautan Afiliator (Sindikat)"])
        
    return pd.DataFrame(rows)

def main():
    """
    Main execution function for the Streamlit dashboard.
    """
    st.set_page_config(page_title="GovSpiders Threat Intelligence", layout="wide")
    
    st.title("GovSpiders Threat Intelligence Dashboard")
    st.markdown("Visualisasi data hasil pemindaian keamanan (SEO Poisoning).")
    
    with st.sidebar:
        st.header("Konfigurasi Data")
        uploaded_file = st.file_uploader("Unggah File JSON (hasil.json)", type=["json"])
        
    data = load_data(uploaded_file)
    
    if not data:
        st.info("Silakan unggah file JSON hasil pemindaian di menu samping untuk melihat visualisasi data.")
        return
        
    total_scanned, total_vulnerable, total_syndicate_links = calculate_metrics(data)
    
    st.subheader("Key Performance Indicators (KPI)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Total Target Dipindai", value=total_scanned)
    with col2:
        st.metric(label="Total Domain Rentan", value=total_vulnerable)
    with col3:
        st.metric(label="Total Jejak Sindikat", value=total_syndicate_links)
        
    st.markdown("---")
    
    st.subheader("Rasio Status Target")
    status_counts = {"Vulnerable": 0, "Safe": 0, "Error": 0}
    for item in data:
        status = item.get("status", "Unknown")
        if status in status_counts:
            status_counts[status] += 1
        else:
            status_counts[status] = 1
            
    df_status = pd.DataFrame(list(status_counts.items()), columns=["Status", "Jumlah"])
    df_status = df_status[df_status["Jumlah"] > 0]
    
    fig = px.pie(df_status, values="Jumlah", names="Status", title="Distribusi Status Pemindaian", hole=0.4)
    st.plotly_chart(fig, width="stretch")
    
    st.markdown("---")
    
    st.subheader("Syndicate Relational Table")
    st.markdown("Tabel berikut menampilkan domain target yang rentan beserta tautan afiliator yang berhasil diekstrak.")
    
    df_syndicates = extract_syndicate_dataframe(data)
    st.dataframe(df_syndicates, width="stretch")

if __name__ == "__main__":
    main()
