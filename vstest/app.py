import streamlit as st
import pandas as pd
from openai import OpenAI
import io

# Λειτουργία καθαρισμού μέσω AI
def clean_data_with_ai(dirty_text, client):
    if pd.isna(dirty_text) or str(dirty_text).strip() == "":
        return dirty_text
    
    prompt = f"""
    Είσαι ένας Data Expert. Πάρε την παρακάτω τιμή από ένα Excel και:
    1. Αφαίρεσε περιττά κενά (TRIM).
    2. Διόρθωσε την ορθογραφία και την κεφαλαιοποίηση (Proper Case).
    3. Αν είναι όνομα, γράψτο σωστά. Αν είναι κατηγορία, τυποποίησέ τη.
    
    Τιμή: '{dirty_text}'
    Απάντησε ΜΟΝΟ με την καθαρή τιμή, χωρίς επεξηγήσεις.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except:
        return dirty_text

# Interface Εφαρμογής
st.set_page_config(page_title="AI Data Cleaner", layout="wide")
st.title("🧼 AI Data Cleaner & Formatter")
st.write("Ανέβασε το αρχείο σου και άσε το AI να διορθώσει τα δεδομένα σου για σωστά Lookups και Pivot Tables.")

# Sidebar για ρυθμίσεις
st.sidebar.header("Ρυθμίσεις")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

uploaded_file = st.file_uploader("Ανέβασε αρχείο Excel ή CSV", type=["xlsx", "csv"])

if uploaded_file:
    # Διάβασμα αρχείου
    if uploaded_file.name.endswith('xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)
    
    st.write("### Προεπισκόπηση Δεδομένων", df.head())
    
    column_to_clean = st.selectbox("Επίλεξε τη στήλη που χρειάζεται καθαρισμό:", df.columns)
    
    if st.button("🚀 Έναρξη Καθαρισμού με AI"):
        if not api_key:
            st.error("Παρακαλώ βάλε το OpenAI API Key στο μενού αριστερά.")
        else:
            client = OpenAI(api_key=api_key)
            
            with st.spinner('Το AI επεξεργάζεται τα δεδομένα...'):
                # Εφαρμογή καθαρισμού
                df[f'{column_to_clean}_Cleaned'] = df[column_to_clean].apply(lambda x: clean_data_with_ai(x, client))
            
            st.success("Έτοιμο!")
            st.write(df.head())
            
            # Μετατροπή σε Excel για κατέβασμα
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='CleanedData')
            
            st.download_button(
                label="📥 Λήψη Καθαρισμένου Αρχείου",
                data=output.getvalue(),
                file_name="cleaned_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )