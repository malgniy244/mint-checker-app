import streamlit as st
import pandas as pd
import re
from datetime import datetime
import os
from io import BytesIO

# --- YOUR ORIGINAL CLASS (PASTED DIRECTLY IN) ---
class InteractiveMintChecker:
    def __init__(self):
        self.english_to_chinese = {}

    def load_official_mint_database(self, uploaded_db_file):
        try:
            self.official_mints = pd.read_excel(uploaded_db_file)
            for _, row in self.official_mints.iterrows():
                english = str(row['English Mint Name']).strip()
                chinese = str(row['Chinese Mint Name']).strip()
                self.english_to_chinese[english] = chinese
            return f"✅ Loaded {len(self.english_to_chinese)} official mint names."
        except Exception as e:
            st.error(f"❌ Error loading official mint database: {e}")
            return None

    def find_english_mint_in_text(self, text):
        if not text or not isinstance(text, str): return None
        uncertainty_words = ['uncertain', 'likely', 'probably', 'possibly', 'maybe', 'perhaps', 'or', 'either', 'unknown', 'unidentified', 'attributed', 'tentative']
        text_lower = text.lower()
        for word in uncertainty_words:
            if word in text_lower and "uncertain mint" not in text_lower: return None
        segments = text.split('.')
        for i, segment in enumerate(segments):
            segment = segment.strip()
            if not segment: continue
            for official_mint in self.english_to_chinese.keys():
                escaped_mint = re.escape(official_mint)
                pattern = r'\b' + escaped_mint + r'\b'
                if re.search(pattern, segment, re.IGNORECASE):
                    if i > 0:
                        prev_segment = segments[i - 1].strip()
                        year_patterns = [r'(19\d{2})', r'(20\d{2})', r'\((19\d{2})\)', r'\((20\d{2})\)', r'ND\s*\((19\d{2})\)', r'ND\s*\((20\d{2})\)']
                        has_year = any(re.search(p, prev_segment) for p in year_patterns)
                        if not has_year:
                            for j in range(i):
                                if any(re.search(p, segments[j]) for p in year_patterns):
                                    has_year = True
                                    break
                        if has_year: return official_mint
        return None

    def extract_current_chinese_mint(self, chinese_text):
        if not chinese_text or not isinstance(chinese_text, str): return None
        patterns = [r'([^。，\s]{2,15})造幣廠', r'([^。，\s]{2,15})鑄幣廠', r'造幣總廠', r'寶德局']
        for pattern in patterns:
            if match := re.search(pattern, chinese_text): return match.group(0)
        return None

    def smart_add_mint_name(self, chinese_text, mint_name):
        chinese_text = chinese_text.strip()
        return f"{chinese_text}{mint_name}" if chinese_text.endswith('。') else f"{chinese_text}。{mint_name}"

    def process_file(self, df, english_col, chinese_col):
        inventory_col = df.columns[0]
        corrections, checked_count, corrected_count, skipped_uncertain = [], 0, 0, 0
        for index, row in df.iterrows():
            english_text = str(row[english_col]) if pd.notna(row[english_col]) else ""
            chinese_text = str(row[chinese_col]) if pd.notna(row[chinese_col]) else ""
            inventory_id = str(row[inventory_col]) if pd.notna(row[inventory_col]) else f"Row {index + 2}"
            if 'Mint' in english_text or 'mint' in english_text:
                checked_count += 1
                english_mint = self.find_english_mint_in_text(english_text)
                if english_mint is None and any(word in english_text.lower() for word in ['uncertain', 'likely', 'or']) and "uncertain mint" not in english_text.lower():
                    skipped_uncertain += 1
                    continue
                if english_mint and english_mint in self.english_to_chinese:
                    official_chinese = self.english_to_chinese[english_mint]
                    current_chinese_mint = self.extract_current_chinese_mint(chinese_text)
                    if current_chinese_mint != official_chinese:
                        corrected_chinese = chinese_text.replace(current_chinese_mint, official_chinese) if current_chinese_mint else self.smart_add_mint_name(chinese_text, official_chinese)
                        df.at[index, chinese_col] = corrected_chinese
                        if current_chinese_mint is None: change_type = "MISSING"
                        elif current_chinese_mint.replace('鑄幣廠', '造幣廠') == official_chinese: change_type = "MINOR"
                        else: change_type = "MAJOR"
                        corrections.append({'Inventory': inventory_id, 'Row': index + 2, 'Change Type': change_type, 'English Mint Found': english_mint, 'Full English Text': english_text, 'Original Chinese': chinese_text, 'Current Mint': current_chinese_mint or '[無]', 'Corrected To': official_chinese, 'New Chinese Text': corrected_chinese})
                        corrected_count += 1
        return df, {"checked_count": checked_count, "skipped_uncertain": skipped_uncertain, "corrected_count": corrected_count, "corrections": corrections}


# --- THE NEW STREAMLIT UI CODE ---
def main_app():
    st.title("🏭 Interactive Mint Name Checker")
    st.markdown("Upload your Excel file, select the columns, and let the tool automatically correct Chinese mint names.")

    checker = InteractiveMintChecker()

    with st.sidebar:
        st.header("1. Upload Files")
        db_file = st.file_uploader("Upload 'cpun confirmed mint names.xlsx'", type=['xlsx', 'xls'])
        uploaded_file = st.file_uploader("Upload Excel File to Check", type=['xlsx', 'xls'])

    if db_file and uploaded_file:
        message = checker.load_official_mint_database(db_file)
        if not message: st.stop()
        
        df = pd.read_excel(uploaded_file)
        st.header("2. Configure Columns")
        col1, col2 = st.columns(2)
        english_col = col1.selectbox("English Text Column:", df.columns)
        chinese_col = col2.selectbox("Chinese Text Column:", df.columns)
        
        if st.button("🚀 Start Mint Name Processing"):
            with st.spinner("Processing..."):
                corrected_df, summary = checker.process_file(df.copy(), english_col, chinese_col)
                st.header("3. Results")
                st.metric("Corrections Made", summary['corrected_count'])
                if summary['corrections']:
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        corrected_df.to_excel(writer, sheet_name='Corrected_Data', index=False)
                        pd.DataFrame(summary['corrections']).to_excel(writer, sheet_name='Corrections_Log', index=False)
                    output.seek(0)
                    st.download_button(label="📄 Download Corrected File", data=output, file_name=f"MINT_CORRECTED_{uploaded_file.name}", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- Set a simple password ---
PASSWORD = "your_password_here"  # CHANGE THIS!

# --- Password check logic ---
if "password_correct" not in st.session_state:
    st.session_state.password_correct = False

password_guess = st.text_input("Enter Password", type="password")
if password_guess == PASSWORD:
    st.session_state.password_correct = True

if st.session_state.password_correct:
    main_app()
elif password_guess != "":
    st.error("Password incorrect.")
