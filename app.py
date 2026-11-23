import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dynamic Price Advisor", layout="wide")

# ---------- Load data ----------
@st.cache_data
def load():
    data = pd.read_csv("advisor_data.csv")
    data["demand"] = pd.cut(data["trend"], [-0.01, 0.9999, 1.0001, 1e9],
                            labels=["Falling", "Stable", "Rising"])
    data["stock_label"] = data["in_stock"].map({1: "In stock", 0: "Out of stock"})
    data["activity"] = data["recent"] + data["older"]
    return data

items = load()

# ---------- Header and summary cards ----------
st.title("Explainable Dynamic Price Advisor")
st.caption("Price suggestions with plain-language reasons")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Items", f"{len(items):,}")
c2.metric("Rising", f"{(items['demand'] == 'Rising').sum():,}")
c3.metric("Falling", f"{(items['demand'] == 'Falling').sum():,}")
c4.metric("Out of stock", f"{(items['in_stock'] == 0).sum():,}")

# ---------- Item lookup ----------
st.subheader("Look up an item")

pool = items.sort_values("activity", ascending=False)
item_id = st.selectbox("Item ID", pool["itemid"].head(1000).tolist())
r = items[items["itemid"] == item_id].iloc[0]

m1, m2, m3 = st.columns(3)
m1.metric("Suggested change", f"{r['suggested_change'] * 100:+.1f}%")
m2.metric("Demand trend", f"{r['trend']:.2f}")
m3.metric("Stock", r["stock_label"])
st.info(r["explanation"])

# ---------- Table and download ----------
st.subheader("Top suggestions")
top = (items.assign(abs_change=items["suggested_change"].abs())
            .sort_values(["abs_change", "activity"], ascending=False)
            .head(50))
st.dataframe(top[["itemid", "trend", "activity", "stock_label",
                  "suggested_change", "explanation"]],
             use_container_width=True)
st.download_button("Download CSV", items.to_csv(index=False), "suggestions.csv")

# ---------- About ----------
with st.expander("About and limitations"):
    st.write("Trend = events in recent half / events in older half. "
             "Trend above 1 is rising, below 1 is falling, equal to 1 is stable.")
    st.write("One store-wide elasticity (from Online Retail II) scales every change. "
             "Thresholds and price steps are assumptions.")
