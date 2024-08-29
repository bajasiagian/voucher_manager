import streamlit as st


generator = st.Page("generator.py",title="QR Generator", icon="🎟️")
checker = st.Page("checker.py",title="QR Checker", icon="🔍")

pg = st.navigation({"Voucher Manager":[generator,checker]})
st.set_page_config(page_title="Voucher Manager", page_icon="🎫")
pg.run()