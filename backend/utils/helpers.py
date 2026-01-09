import os
import base64
import streamlit as st

def save_uploaded_file(uploaded_file,save_dir="Uploaded_Resumes"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    file_path=os.path.join(save_dir,uploaded_file.name)

    with open(file_path,"wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

#Displaying pdf in streamlit
def show_pdf(file_path):
    with open(file_path,"rb") as f:
        base64_pdf=base64.b64encode(f.read()).decode("utf-8")

    pdf_display= f"""
        <iframe
            src="data:application/pdf;base64,{base64_pdf}"
            width="800" height="1000" type="application/pdf">
        </iframe>
    """

    st.markdown(pdf_display,unsafe_allow_html=True)