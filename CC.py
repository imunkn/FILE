import streamlit as st
import pandas as pd
import os
import base64

# Define the CSV file path
CSV_FILE = "documents.csv"

# Function to load data
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=["Document_Name", "Content", "File_Type"])

# Function to save data
def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# Streamlit app
st.title("📄 Document & File Storage App")

# Load existing data
df = load_data()

# Tabs: Upload or Retrieve
tab1, tab2 = st.tabs(["Upload Files", "Retrieve Files"])

# Upload Tab
with tab1:
    upload_option = st.radio("Select upload type:", ["Text", "PDF", "Image"])

    if upload_option == "Text":
        with st.form(key="text_form"):
            doc_name = st.text_input("Document Name (Text)", key="text_doc_name")
            doc_content = st.text_area("Document Content", height=200)
            submit_text = st.form_submit_button("Save Text")
        
        if submit_text:
            if doc_name and doc_content:
                new_data = pd.DataFrame([[doc_name, doc_content, "text"]], columns=["Document_Name", "Content", "File_Type"])
                df = pd.concat([df, new_data], ignore_index=True)
                save_data(df)
                st.success(f"Text document '{doc_name}' saved successfully!")
            else:
                st.error("Please provide both a document name and content.")

    else:
        with st.form(key="file_form"):
            uploaded_file = st.file_uploader(f"Upload a {upload_option} file", type=["pdf", "png", "jpg", "jpeg"])
            doc_name_upload = st.text_input(f"Document Name ({upload_option})", key="upload_doc_name")
            submit_upload = st.form_submit_button("Save File")
        
        if submit_upload and uploaded_file is not None:
            if doc_name_upload:
                # Encode file content as base64
                file_bytes = uploaded_file.read()
                encoded_file = base64.b64encode(file_bytes).decode("utf-8")
                file_type = uploaded_file.type

                new_data = pd.DataFrame([[doc_name_upload, encoded_file, file_type]], columns=["Document_Name", "Content", "File_Type"])
                df = pd.concat([df, new_data], ignore_index=True)
                save_data(df)
                st.success(f"Uploaded {upload_option} '{doc_name_upload}' saved successfully!")
            else:
                st.error("Please provide a document name for the uploaded file.")

# Retrieve Tab
with tab2:
    st.subheader("Stored Documents and Files")
    if not df.empty:
        st.dataframe(df[["Document_Name", "File_Type"]])

        selected_doc = st.selectbox("Select a document to retrieve:", df["Document_Name"])
        if selected_doc:
            record = df[df["Document_Name"] == selected_doc].iloc[0]
            file_type = record["File_Type"]
            content = record["Content"]

            if file_type == "text":
                st.text_area("Document Content", content, height=300, disabled=True)
            else:
                decoded_file = base64.b64decode(content)
                
                if "pdf" in file_type:
                    st.download_button(
                        label="Download PDF",
                        data=decoded_file,
                        file_name=f"{selected_doc}.pdf",
                        mime="application/pdf"
                    )
                elif "image" in file_type:
                    st.image(decoded_file, caption=selected_doc)
                    st.download_button(
                        label="Download Image",
                        data=decoded_file,
                        file_name=f"{selected_doc}.jpg",
                        mime=file_type
                    )
    else:
        st.write("No documents/files stored yet.")

# Option to download complete CSV
if os.path.exists(CSV_FILE):
    with open(CSV_FILE, "rb") as file:
        st.download_button(
            label="Download Full CSV",
            data=file,
            file_name="documents.csv",
            mime="text/csv"
        )
