import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pandas as pd
from datetime import date
import datetime
import toml
import json

# Data Uploader
scope = ['https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive']

#Get Creds from secrets
with open(st.secrets, 'r') as f:
    toml_data = toml.load(f)

json_data = json.dumps(toml_data, indent=4)

creds = ServiceAccountCredentials.from_json_keyfile_name(json_data,scope)

client = gspread.authorize(creds)

#Database
db = client.open('Voucher Database').worksheet("database")
data_db = db.get_all_values()
column_names_db = data_db[0]
data_db = data_db[1:]
db_df = pd.DataFrame(data_db, columns=column_names_db)

#Used Voucher
used = client.open('Voucher Database').worksheet("used_voucher")
data_used = used.get_all_values()
column_names_used = data_used[0]
data_used = data_used[1:]
used_df = pd.DataFrame(data_used, columns=column_names_used)

#Expired
expired = client.open('Voucher Database').worksheet("expired_voucher")
data_expired = expired.get_all_values()
column_names_expired = data_expired[0]
data_expired = data_expired[1:]
expired_df = pd.DataFrame(data_expired, columns=column_names_expired)

st.title("Voucher Checker ✅")
# -------------------------------------------------#
with st.container(border=True):
    st.markdown("### Foto dengan kamera 📸")
    img_file_buffer = st.camera_input("")

    if img_file_buffer is not None:
        # To read image file buffer as a PIL Image:
        img = Image.open(img_file_buffer)
        #Check if picture is good
        try:
            #Read code
            b = decode(img)
            code = b[0].data.decode('utf-8')
            
            if code in db_df.voucher_id.tolist() and code not in used_df.voucher_id.tolist() and code not in expired_df.voucher_id.tolist():
                date_diff = (datetime.datetime.strptime(db_df[db_df.voucher_id==code]['end_date'].iloc[0],"%Y-%m-%d") - datetime.datetime.today()).days
                discount = db_df[db_df.voucher_id==code]['discount_amount'].iloc[0]
            
                # Check if still valid
                if date_diff <= 0:
                    st.write("Expired")
                    #Update expired
                    expire_update = pd.DataFrame({"voucher_id":[code],"triggered_date":[str(date.today())]})
                    expired_df = pd.concat([expired_df,expire_update])
                    expired.update([expired_df.columns.values.tolist()] + expired_df.values.tolist(), value_input_option="RAW")

                elif date_diff > 0:
                    st.success(f"Voucher bisa digunakan! Diskon : {discount}")
                    #Update used_voucher
                    use_update = pd.DataFrame({"voucher_id":[code],"used_at":[str(date.today())]})
                    used_df = pd.concat([used_df,use_update])
                    used.update([used_df.columns.values.tolist()] + used_df.values.tolist(), value_input_option="RAW")

            elif code not in db_df.voucher_id.tolist():
                st.warning("Data tidak ditemukan")
            
            elif code in used_df.voucher_id.tolist():
                st.warning(f"Voucher ini telah digunakan pada {used_df[used_df.voucher_id==code]['used_at'].iloc[0]}")
            
        except:
            st.warning("Gagal membaca QR Code, ulang pengecekan")
# -------------------------------------------------#
with st.container(border=True):
    st.markdown("### Upload File 📂")
    uploaded_files = st.file_uploader("", accept_multiple_files=False)

    if uploaded_files is not None:
        img = Image.open(uploaded_files)
        #Check if picture is good
        try:
            #Read code
            b = decode(img)
            code = b[0].data.decode('utf-8')
            
            if code in db_df.voucher_id.tolist() and code not in used_df.voucher_id.tolist() and code not in expired_df.voucher_id.tolist():
                date_diff = (datetime.datetime.strptime(db_df[db_df.voucher_id==code]['end_date'].iloc[0],"%Y-%m-%d") - datetime.datetime.today()).days
                discount = db_df[db_df.voucher_id==code]['discount_amount'].iloc[0]
            
                # Check if still valid
                if date_diff <= 0:
                    st.write("Expired")
                    #Update expired
                    expire_update = pd.DataFrame({"voucher_id":[code],"triggered_date":[str(date.today())]})
                    expired_df = pd.concat([expired_df,expire_update])
                    expired.update([expired_df.columns.values.tolist()] + expired_df.values.tolist(), value_input_option="RAW")

                elif date_diff > 0:
                    st.success(f"Voucher bisa digunakan! Diskon : {discount}")
                    #Update used_voucher
                    use_update = pd.DataFrame({"voucher_id":[code],"used_at":[str(date.today())]})
                    used_df = pd.concat([used_df,use_update])
                    used.update([used_df.columns.values.tolist()] + used_df.values.tolist(), value_input_option="RAW")

            elif code not in db_df.voucher_id.tolist():
                st.warning("Data tidak ditemukan")
            
            elif code in used_df.voucher_id.tolist():
                st.warning(f"Voucher ini telah digunakan pada {used_df[used_df.voucher_id==code]['used_at'].iloc[0]}")
            
        except:
            st.warning("Gagal membaca QR Code, ulang pengecekan")
