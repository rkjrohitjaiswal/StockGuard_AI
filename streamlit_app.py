import streamlit as st
import pandas as pd
from datetime import date
from snowflake.snowpark.context import get_active_session

# ================= CONFIG =================
DB = "STOCKGUARD_DB"
SCHEMA = "PUBLIC"
USERS = f"{DB}.{SCHEMA}.USERS"
BASIC = f"{DB}.{SCHEMA}.BASIC"

session = get_active_session()

# ================= SESSION =================
for k in ["logged_in", "username", "role", "org_type", "dark_mode"]:
    if k not in st.session_state:
        st.session_state[k] = False if k == "dark_mode" else ""

# ================= THEME =================
if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
        body { background-color: #0e1117; color: white; }
        </style>
        """,
        unsafe_allow_html=True
    )

# ================= AUTH =================
def login(u, p):
    return session.sql(
        f"""SELECT username, role, org_type
            FROM {USERS}
            WHERE username='{u}' AND password='{p}'"""
    ).collect()

def signup(u, p, r, o):
    if session.sql(
        f"SELECT COUNT(*) c FROM {USERS} WHERE username='{u}'"
    ).collect()[0]["C"] > 0:
        return False

    session.sql(
        f"""INSERT INTO {USERS}
            VALUES ('{u}','{p}','{r}','{o}',CURRENT_TIMESTAMP())"""
    ).collect()

    st.session_state.logged_in = True
    st.session_state.username = u
    st.session_state.role = r
    st.session_state.org_type = o
    return True

# ================= LOGIN / SIGNUP =================
if not st.session_state.logged_in:
    st.title("🔐 StockGuard AI")
    st.caption("Secure inventory intelligence for Hospitals, PDS & NGOs")

    t1, t2 = st.tabs(["Sign In", "Sign Up"])

    with t1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Sign In"):
            res = login(u, p)
            if res:
                st.session_state.logged_in = True
                st.session_state.username = res[0]["USERNAME"]
                st.session_state.role = res[0]["ROLE"]
                st.session_state.org_type = res[0]["ORG_TYPE"]
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")

    with t2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        org = st.selectbox(
            "Organization Type",
            ["Hospital","Public Distribution System","NGO"]
        )
        role = st.selectbox("Role", ["ADMIN","STAFF"])

        if st.button("Create Account"):
            if signup(nu, np, role, org):
                st.success("Account created")
                st.experimental_rerun()
            else:
                st.warning("Username exists")

    st.stop()

# ================= MAIN APP =================
ORG_PREFIX = {
    "Hospital":"HOSPITAL",
    "Public Distribution System":"PDS",
    "NGO":"NGO"
}[st.session_state.org_type]

# ---------- TOP BAR ----------
left, right = st.columns([8, 2])

with left:
    st.markdown("# 📦 StockGuard AI")
    st.caption("AI-for-Good inventory monitoring")

with right:
    with st.expander("👤"):
        st.markdown(f"**User:** {st.session_state.username}")
        st.markdown(f"**Org:** {st.session_state.org_type}")
        st.markdown(f"**Role:** {st.session_state.role}")
        st.checkbox("🌙 Dark Mode", key="dark_mode")
        if st.button("🚪 Logout"):
            for k in st.session_state:
                st.session_state[k] = ""
            st.experimental_rerun()

# ================= LOAD DATA =================
df = session.sql(
    f"""SELECT location_id,item_id,opening_stock,
               received,issued,closing_stock,exd
        FROM {BASIC}"""
).to_pandas()

if not df.empty:
    df["TOTAL"] = df["OPENING_STOCK"] + df["RECEIVED"]
    df["PERCENT"] = (df["CLOSING_STOCK"] / df["TOTAL"].replace(0,1))*100
    df["DAYS_TO_EXP"] = (pd.to_datetime(df["EXD"]) - pd.Timestamp.today()).dt.days

# ================= DASHBOARD =================
st.markdown("## 📊 Overview")

if not df.empty:
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🏥 Branches", df["LOCATION_ID"].nunique())
    c2.metric("📦 Items", df["ITEM_ID"].nunique())
    c3.metric("⚠️ Reorder", (df["PERCENT"]<30).sum())
    c4.metric("🚨 Critical", (df["PERCENT"]<10).sum())

# ================= ADMIN ONLY =================
if st.session_state.role == "ADMIN":

    st.markdown("---")
    st.markdown(f"## ➕ Add {st.session_state.org_type} Branch")

    branch = st.text_input("Branch name")
    if st.button("Add Branch"):
        session.sql(
            f"""INSERT INTO {BASIC}
                VALUES (CURRENT_DATE(),
                        DATEADD(day,365,CURRENT_DATE()),
                        '{ORG_PREFIX}_{branch}',
                        'INIT',0,0,0,0,3)"""
        ).collect()
        st.success("Branch added")
        st.experimental_rerun()

    st.markdown("---")
    st.markdown("## ➕ Add Inventory")

    branches = sorted(df["LOCATION_ID"].unique()) if not df.empty else []
    loc = st.selectbox("Branch", branches)
    item = st.text_input("Item")
    opening = st.number_input("Opening",0)
    received = st.number_input("Received",0)
    issued = st.number_input("Issued",0)
    exd = st.date_input("Expiry Date")

    if st.button("Save Inventory"):
        closing = max(opening+received-issued,0)
        session.sql(
            f"""INSERT INTO {BASIC}
                VALUES (CURRENT_DATE(),'{exd}','{loc}',
                        '{item}',{opening},{received},
                        {issued},{closing},3)"""
        ).collect()
        st.success("Inventory saved")
        st.experimental_rerun()

# ================= ALERTS =================
st.markdown("---")
st.markdown("## 🚨 Alerts")

for _,r in df.iterrows():
    if r["PERCENT"] < 10:
        st.error(f"🆘 {r['ITEM_ID']} at {r['LOCATION_ID']} is CRITICAL")
    elif r["PERCENT"] < 20:
        st.warning(f"🚨 {r['ITEM_ID']} at {r['LOCATION_ID']} is VERY LOW")
    if r["DAYS_TO_EXP"] <= 30:
        st.warning(f"⏰ {r['ITEM_ID']} at {r['LOCATION_ID']} expires soon")

# ================= HEATMAP =================
st.markdown("---")
st.markdown("## 📊 Risk Heatmap")

def icon(p):
    if p>=40: return "🟢"
    if p>=30: return "🟡"
    if p>=20: return "🔴"
    if p>=10: return "🚨"
    return "🆘"

df["RISK"] = df["PERCENT"].apply(icon)

heatmap = df.pivot_table(
    index="LOCATION_ID",
    columns="ITEM_ID",
    values="RISK",
    aggfunc="first",
    fill_value="🟢"
)

st.dataframe(heatmap, use_container_width=True)

# ================= REORDER EXPORT (ADMIN ONLY) =================
if st.session_state.role == "ADMIN":
    st.markdown("---")
    st.markdown("## 📤 Reorder List")

    reorder = df[(df["PERCENT"]<30) | (df["DAYS_TO_EXP"]<=30)]
    if not reorder.empty:
        reorder["REORDER_QTY"] = reorder["TOTAL"] - reorder["CLOSING_STOCK"]
        st.dataframe(reorder[
            ["LOCATION_ID","ITEM_ID","PERCENT","REORDER_QTY"]
        ])
        st.download_button(
            "⬇️ Download CSV",
            reorder.to_csv(index=False).encode(),
            "reorder_list.csv"
        )
    else:
        st.success("No reorder needed")

st.caption("🌙 Dark Mode • 👥 Role-based UI • All features preserved")
