import uuid
import qrcode
from PIL import Image
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pandas as pd
from datetime import date

scope = ['https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive']

creds = ServiceAccountCredentials.from_json_keyfile_name(st.secrets["google_creds"],scope)
client = gspread.authorize(creds)

sheet = client.open('Voucher Database').worksheet("database")
data = sheet.get_all_values()
column_names = data[0]
data = data[1:]
db_df = pd.DataFrame(data, columns=column_names)


#Ask for voucher details
st.title("Voucher Generator")
with st.form("my_form"):
    st.markdown("### Masukkan Detail Voucher")
    col1,col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Masa Berlaku Awal Voucher")
    with col2:
        end_date = st.date_input("Masa Akhir Voucher")
    with st.container(border=True):
        date_range = end_date - start_date
        date_range = date_range.days
        st.markdown(f"###### Masa berlaku voucher `{date_range}` hari")

    
    discount_amount = st.text_input("Jumlah Diskon",
                                    placeholder="Diskon atau jumlah potongan")
    discount_amount = discount_amount.title()
    

    submitted = st.form_submit_button("Buat id dan QR")
    if submitted:
        if not start_date or not end_date or not discount_amount:
            st.warning("Ada kolom yang belum diisi")
            st.stop()
        
        #Generate ID
        while True:
            id = uuid.uuid4()
            uuid_str = str(id)
            if uuid_str in list(db_df.voucher_id):
                pass
            else:
                break
        
        #Create row
        new_df = pd.DataFrame({"voucher_id":[uuid_str],
                               "release_date":[str(date.today())],
                               "start_date":[str(start_date)],
                               "end_date":[str(end_date)],
                               "discount_amount":[str(discount_amount)]})
        
        #Generate QR Code
        img = qrcode.make(uuid_str)
        img.save("qr.png")
        
        qr = Image.open("qr.png")
        #Store image in session state
        st.session_state["image"] = qr

        #show qr and id
        db_df = pd.concat([db_df,new_df])
        
        sheet.update([db_df.columns.values.tolist()] + db_df.values.tolist(), value_input_option="RAW")

        col1,col2,col3 = st.columns([1,3,1])
        with col1:
            st.write("")
        with col2:
            st.markdown(f"<h3 style='text-align: center;'>Screenshot QR Code di Bawah</h3>", unsafe_allow_html=True)
            st.markdown(f"<h6 style='text-align: center;'>{uuid_str}</h6>", unsafe_allow_html=True)
            st.image(st.session_state["image"])
        with col3:
            st.write("")



# #Decode QR Code
# b = decode(Image.open("C:/Projects Work and Such/Python/Voucher Manager/443c6541-52c1-442d-99ef-52602da37c6e.png"))
# code = b[0].data.decode('utf-8')

# st.title("Generator")
# st.write(uuid_str)
# st.image(Image.open("C:/Projects Work and Such/Python/Voucher Manager/443c6541-52c1-442d-99ef-52602da37c6e.png"))