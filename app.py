# app.py
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

def format_date(iso_str):
    try:
        dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%d-%m-%Y %H:%M:%S")
    except:
        return iso_str

st.title("🔄 Freshdesk Export Tool")

api_key = st.text_input("🔑 Enter your Freshdesk API Key", type="password")
domain = st.text_input("🌐 Freshdesk Domain (e.g., rattanindia.freshdesk.com)", value="rattanindia.freshdesk.com")

export_type = st.selectbox("📦 Select Export Type", ["Automations", "Groups", "Agents"])
pages = st.number_input("🔢 Enter number of pages to fetch", min_value=1, value=1)

if st.button("🚀 Run Export"):
    headers = {"Content-Type": "application/json"}
    all_data = []

    for page in range(1, pages + 1):
        if export_type == "Automations":
            url = f"https://{domain}/api/v2/automations/1/rules?page={page}&per_page=100"
        elif export_type == "Groups":
            url = f"https://{domain}/api/v2/groups?page={page}"
        else:
            url = f"https://{domain}/api/v2/agents?page={page}"

        res = requests.get(url, auth=(api_key, 'X'), headers=headers)

        if res.status_code != 200:
            st.error(f"Failed to fetch page {page}: {res.status_code}")
            break

        items = res.json()

        for item in items:
            if export_type == "Automations":
                all_data.append({
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "created_at": format_date(item.get("created_at")),
                    "active": item.get("active")
                })
            elif export_type == "Groups":
                all_data.append({
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "group_type": item.get("group_type"),
                    "created_at": format_date(item.get("created_at"))
                })
            elif export_type == "Agents":
                contact = item.get("contact", {})
                all_data.append({
                    "id": item.get("id"),
                    "name": contact.get("name"),
                    "phone": contact.get("phone"),
                    "email": contact.get("email"),
                    "created_at": format_date(item.get("created_at")),
                    "active": contact.get("active")
                })

    if all_data:
        df = pd.DataFrame(all_data)
        st.success(f"✅ Fetched {len(df)} records.")
        st.dataframe(df)

        # Download button
        st.download_button(
            label="⬇ Download Excel",
            data=df.to_excel(index=False, engine='openpyxl'),
            file_name=f"{export_type.lower()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )