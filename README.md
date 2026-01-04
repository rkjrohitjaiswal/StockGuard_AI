# StockGuard AI 🚑📦

## Inventory Heatmap & Early Stock-Out Alerts for Essential Goods

### 🧩 Problem
Hospitals, Public Distribution Systems, and NGOs struggle to keep essential goods
available at the right place and time. Inventory data is fragmented, leading to
stock-outs or over-stocking.

### 💡 Solution
StockGuard AI is a Snowflake-native Streamlit application that:
- Monitors inventory across organizations and branches
- Detects low stock and near-expiry risks
- Generates early alerts and reorder recommendations
- Visualizes risk using heatmaps
- Enforces role-based access (Admin vs Staff)

### 🏗️ Architecture
- **Frontend:** Snowflake Streamlit
- **Backend:** Snowflake Snowpark
- **Database:** Snowflake Tables
- **Security:** Role-based access control
- **AI Logic:** Rule-based explainable intelligence

### 🚀 Running the App
This application is designed to run **inside Snowflake Streamlit Apps**.

1. Create tables using `schema.sql`
2. Deploy `streamlit_app.py` inside Snowflake
3. Share app using Snowflake role-based access

### 🔐 Access Note
Due to Snowflake security architecture, public sign-up is not supported.
A demo video is provided for full walkthrough.

### 🌍 AI for Good Impact
- Prevents medicine and food stock-outs
- Reduces wastage due to expiry
- Supports healthcare and public welfare programs
