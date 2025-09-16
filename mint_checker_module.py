#!/usr/bin/env python3
"""
Interactive Mint Checker - Streamlit Version
Preserves ALL original script logic exactly as provided
"""

import streamlit as st
import pandas as pd
import re
from datetime import datetime
import io
from typing import Optional, List, Dict, Tuple
import requests

class InteractiveMintChecker:
    def __init__(self):
        """Initialize with official mint names database"""
        self.english_to_chinese = {}
        self.official_mints = None
        
    def load_official_mint_database_from_github(self):
        """Load the official mint database from GitHub (EXACT original logic)"""
        try:
            url = "https://raw.githubusercontent.com/malgniy244/mint-checker-app/main/cpun%20confirmed%20mint%20names.xlsx"
            response = requests.get(url)
            response.raise_for_status()
            db_file = io.BytesIO(response.content)
            return self.load_official_mint_database(db_file)
        except Exception as e:
            raise Exception(f"Could not download database from GitHub: {str(e)}")

    def load_official_mint_database(self, db_source):
        """Load the official mint names from file (EXACT original logic)"""
        try:
            self.official_mints = pd.read_excel(db_source)
            
            # Create exact lookup dictionary (EXACT from original)
            self.english_to_chinese = {}
            
            for _, row in self.official_mints.iterrows():
                english = str(row['English Mint Name']).strip()
                chinese = str(row['Chinese Mint Name']).strip()
                self.english_to_chinese[english] = chinese
            
            return len(self.official_mints), len(self.english_to_chinese)
            
        except Exception as e:
            raise Exception(f"Error loading official mint database: {e}")
    
    def find_english_mint_in_text(self, text: str) -> Optional[str]:
        """Find English mint name in text - ONLY between two periods (EXACT original logic)"""
        if not text or not isinstance(text, str):
            return None
        
        # EXCLUDE uncertain/approximate references (EXACT from original)
        uncertainty_words = [
            'uncertain', 'likely', 'probably', 'possibly', 'maybe', 'perhaps',
            'or', 'either', 'unknown', 'unidentified', 'attributed', 'tentative'
        ]
        
        # Check if text contains uncertainty words (but allow "Uncertain Mint" as it's in database)
        text_lower = text.lower()
        for word in uncertainty_words:
            if word in text_lower and "uncertain mint" not in text_lower:
                return None
        
        # Find all segments between periods (EXACT original logic)
        segments = text.split('.')
        
        for i, segment in enumerate(segments):
            segment = segment.strip()
            
            # Skip empty segments
            if not segment:
                continue
            
            # Check if this segment contains a mint name and appears to be after a year
            for official_mint in self.english_to_chinese.keys():
                # Use word boundaries to ensure exact matching (EXACT from original)
                escaped_mint = re.escape(official_mint)
                pattern = r'\b' + escaped_mint + r'\b'
                
                if re.search(pattern, segment, re.IGNORECASE):
                    # Found a mint in this segment
                    # Check if the previous segment (before this period) contains a year
                    if i > 0:
                        prev_segment = segments[i-1].strip()
                        
                        # Check if previous segment contains a year pattern (EXACT from original)
                        year_patterns = [
                            r'(19\d{2})',  # contains 1900-1999
                            r'(20\d{2})',  # contains 2000-2099  
                            r'\((19\d{2})\)',  # contains (1940)
                            r'\((20\d{2})\)',  # contains (2000)
                            r'ND\s*\((19\d{2})\)',  # contains ND (1889)
                            r'ND\s*\((20\d{2})\)',  # contains ND (2000)
                        ]
                        
                        has_year = False
                        for year_pattern in year_patterns:
                            if re.search(year_pattern, prev_segment):
                                has_year = True
                                break
                        
                        # Also check for year patterns anywhere in the previous segments (EXACT from original)
                        if not has_year:
                            # Check if any earlier segment has year info
                            for j in range(i):
                                earlier_segment = segments[j]
                                for year_pattern in [r'(19\d{2})', r'(20\d{2})', r'\((19\d{2})\)', r'\((20\d{2})\)', r'ND\s*\((19\d{2})\)', r'ND\s*\((20\d{2})\)']:
                                    if re.search(year_pattern, earlier_segment):
                                        has_year = True
                                        break
                                if has_year:
                                    break
                        
                        if has_year:
                            return official_mint
        
        return None
    
    def extract_current_chinese_mint(self, chinese_text: str) -> Optional[str]:
        """Extract current Chinese mint name from text (EXACT original logic)"""
        if not chinese_text or not isinstance(chinese_text, str):
            return None
            
        # Look for mint patterns (EXACT from original)
        patterns = [
            r'([^。，\s]{2,15})造幣廠',
            r'([^。，\s]{2,15})鑄幣廠',
            r'造幣總廠',
            r'寶德局'  # Special case for Chengde
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, chinese_text)
            for match in matches:
                if pattern in [r'造幣總廠', r'寶德局']:
                    return match.group(0)
                else:
                    return match.group(0)  # Return full match including suffix
        
        return None
    
    def smart_add_mint_name(self, chinese_text: str, mint_name: str) -> str:
        """Smartly add mint name without creating double periods (EXACT original logic)"""
        chinese_text = chinese_text.strip()
        
        # If text already ends with period, just add mint name (no extra period)
        if chinese_text.endswith('。'):
            return f"{chinese_text}{mint_name}"
        
        # If text doesn't end with period, add period then mint name
        else:
            return f"{chinese_text}。{mint_name}"
    
    def classify_change_type(self, current_chinese_mint: Optional[str], official_chinese: str) -> str:
        """Classify the type of change (EXACT original logic)"""
        if current_chinese_mint is None:
            return "MISSING"  # No Chinese mint → Added Chinese mint
        elif current_chinese_mint.replace('鑄幣廠', '造幣廠') == official_chinese:
            return "MINOR"    # Only 鑄幣廠 → 造幣廠 change
        else:
            return "MAJOR"    # Other significant changes
    
    def process_mint_corrections(self, df: pd.DataFrame, english_col: str, chinese_col: str) -> Tuple[pd.DataFrame, List[Dict]]:
        """Process mint corrections with all original logic preserved"""
        
        inventory_col = df.columns[0]  # Use first column for inventory
        corrections = []
        checked_count = 0
        corrected_count = 0
        skipped_uncertain = 0
        
        # Process each row (EXACT original logic)
        for index, row in df.iterrows():
            english_text = str(row[english_col]) if pd.notna(row[english_col]) else ""
            chinese_text = str(row[chinese_col]) if pd.notna(row[chinese_col]) else ""
            inventory_id = str(row[inventory_col]) if pd.notna(row[inventory_col]) else f"Row {index + 2}"
            
            # Check if English text contains a mint reference (EXACT from original)
            if 'Mint' in english_text or 'mint' in english_text:
                checked_count += 1
                
                # Find the English mint name (will return None for uncertain cases)
                english_mint = self.find_english_mint_in_text(english_text)
                
                # Skip uncertain references (EXACT original logic)
                if english_mint is None and any(word in english_text.lower() for word in ['uncertain', 'likely', 'or']) and "uncertain mint" not in english_text.lower():
                    skipped_uncertain += 1
                    continue
                
                if english_mint and english_mint in self.english_to_chinese:
                    official_chinese = self.english_to_chinese[english_mint]
                    current_chinese_mint = self.extract_current_chinese_mint(chinese_text)
                    
                    # Check if correction is needed
                    if current_chinese_mint != official_chinese:
                        # Create corrected Chinese text (EXACT original logic)
                        if current_chinese_mint:
                            # Replace existing mint name
                            corrected_chinese = chinese_text.replace(current_chinese_mint, official_chinese)
                        else:
                            # Add mint name smartly (avoiding double periods)
                            corrected_chinese = self.smart_add_mint_name(chinese_text, official_chinese)
                        
                        # Update the DataFrame
                        df.at[index, chinese_col] = corrected_chinese
                        
                        # Determine change type (EXACT original logic)
                        change_type = self.classify_change_type(current_chinese_mint, official_chinese)
                        
                        # Record the correction
                        corrections.append({
                            'Inventory': inventory_id,
                            'Row': index + 2,
                            'Change Type': change_type,
                            'English Mint Found': english_mint,
                            'Full English Text': english_text,
                            'Original Chinese': chinese_text,
                            'Current Mint': current_chinese_mint or '[無]',
                            'Corrected To': official_chinese,
                            'New Chinese Text': corrected_chinese
                        })
                        
                        corrected_count += 1
        
        # Return statistics with corrections
        stats = {
            'checked_count': checked_count,
            'skipped_uncertain': skipped_uncertain,
            'corrected_count': corrected_count,
            'change_types': {'MINOR': 0, 'MISSING': 0, 'MAJOR': 0}
        }
        
        # Count change types
        for corr in corrections:
            stats['change_types'][corr['Change Type']] += 1
        
        return df, corrections, stats

# ============================================================================
# STREAMLIT UI
# ============================================================================

def main():
    st.set_page_config(
        page_title="Interactive Mint Name Checker",
        page_icon="🏭",
        layout="wide"
    )
    
    st.title("🏭 Interactive Mint Name Checker")
    st.markdown("**Period-based extraction with exact matching - preserves all original logic**")
    
    # Show features
    with st.expander("✨ Features", expanded=False):
        st.markdown("""
        - ✅ **Period-based extraction**: mint names between periods after year
        - ✅ **Uncertainty filtering**: excludes uncertain/approximate references
        - ✅ **Smart text correction**: avoids double periods
        - ✅ **Change classification**: MINOR/MISSING/MAJOR types
        - ✅ **Exact matching**: word boundaries for precise identification
        - ✅ **Multiple year patterns**: (19xx), (20xx), ND (19xx)
        """)
    
    # Initialize mint checker
    if 'mint_checker' not in st.session_state:
        st.session_state.mint_checker = InteractiveMintChecker()
        st.session_state.database_loaded = False
    
    # Load database
    if not st.session_state.database_loaded:
        with st.spinner("Loading official mint database..."):
            try:
                total_mints, mapping_count = st.session_state.mint_checker.load_official_mint_database_from_github()
                st.success(f"✅ Loaded {total_mints} official mint names, created {mapping_count} exact mappings")
                st.session_state.database_loaded = True
            except Exception as e:
                st.error(f"❌ Error loading database: {e}")
                st.info("Make sure the 'cpun confirmed mint names.xlsx' file is available in your GitHub repo")
                return
    
    # File upload
    st.subheader("📁 Upload Your Excel File")
    uploaded_file = st.file_uploader(
        "Choose an Excel file",
        type=['xlsx', 'xls'],
        help="Upload your Excel file containing English and Chinese coin descriptions"
    )
    
    if uploaded_file is not None:
        try:
            # Load the Excel file
            df = pd.read_excel(uploaded_file)
            st.success(f"✅ File loaded successfully! {len(df)} rows, {len(df.columns)} columns found.")
            
            # Show preview
            with st.expander("👀 Preview Data", expanded=True):
                st.dataframe(df.head())
            
            # Column selection
            st.subheader("📊 Select Columns")
            col1, col2 = st.columns(2)
            
            with col1:
                english_col = st.selectbox(
                    "🇬🇧 English Column (contains mint names)",
                    options=df.columns,
                    help="Select the column containing English text with mint names"
                )
            
            with col2:
                chinese_col = st.selectbox(
                    "🇨🇳 Chinese Column (to be corrected)", 
                    options=df.columns,
                    help="Select the column containing Chinese text to be corrected"
                )
            
            if english_col and chinese_col:
                st.markdown(f"**Selected:** {english_col} → {chinese_col}")
                
                # Show sample data for selected columns
                with st.expander("🔍 Sample Data for Selected Columns", expanded=False):
                    sample_data = df[[english_col, chinese_col]].head(3)
                    for idx, row in sample_data.iterrows():
                        st.markdown(f"**Row {idx + 1}:**")
                        st.markdown(f"- English: {str(row[english_col])[:100]}{'...' if len(str(row[english_col])) > 100 else ''}")
                        st.markdown(f"- Chinese: {str(row[chinese_col])[:100]}{'...' if len(str(row[chinese_col])) > 100 else ''}")
                
                # Analysis button
                if st.button("🚀 Start Mint Correction Analysis", type="primary"):
                    with st.spinner("Processing mint names with period-based extraction..."):
                        df_corrected, corrections, stats = st.session_state.mint_checker.process_mint_corrections(df, english_col, chinese_col)
                    
                    # Display results
                    display_mint_results(df_corrected, corrections, stats, english_col, chinese_col, uploaded_file.name)
                    
        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")

def display_mint_results(df: pd.DataFrame, corrections: List[Dict], stats: Dict, english_col: str, chinese_col: str, filename: str):
    """Display mint correction results with statistics and export option"""
    
    # Summary statistics
    st.subheader("📈 Mint Correction Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Rows with 'Mint'", stats['checked_count'])
        st.metric("⚠️ Skipped Uncertain", stats['skipped_uncertain'])
    
    with col2:
        st.metric("✅ Total Corrections", stats['corrected_count'])
        st.metric("📄 MINOR Changes", stats['change_types']['MINOR'])
    
    with col3:
        st.metric("📋 MISSING Additions", stats['change_types']['MISSING'])
        st.metric("🔧 MAJOR Changes", stats['change_types']['MAJOR'])
    
    with col4:
        if stats['checked_count'] > 0:
            correction_rate = (stats['corrected_count'] / stats['checked_count'] * 100)
            st.metric("Correction Rate", f"{correction_rate:.1f}%")
    
    # Change type explanations
    with st.expander("📖 Change Type Explanations", expanded=False):
        st.markdown("""
        - **📄 MINOR**: Only 鑄幣廠 → 造幣廠 character change
        - **📋 MISSING**: No Chinese mint name → Added Chinese mint name  
        - **🔧 MAJOR**: Other significant changes (different mint names)
        """)
    
    # Show corrections
    if corrections:
        st.subheader("🔧 Mint Corrections Made")
        st.markdown(f"**{len(corrections)}** corrections applied")
        
        # Show sample corrections (first 10)
        with st.expander(f"💡 Sample Corrections (showing first {min(10, len(corrections))})", expanded=True):
            for i, corr in enumerate(corrections[:10], 1):
                type_icon = {"MINOR": "📄", "MISSING": "📋", "MAJOR": "🔧"}[corr['Change Type']]
                
                with st.container():
                    st.markdown(f"**{i:2d}. {corr['Inventory']} (Row {corr['Row']}) {type_icon} {corr['Change Type']}**")
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.markdown(f"**English Mint:** {corr['English Mint Found']}")
                        st.markdown(f"**English:** {corr['Full English Text'][:70]}{'...' if len(corr['Full English Text']) > 70 else ''}")
                    with col2:
                        st.markdown(f"**Before:** {corr['Original Chinese']}")
                        st.markdown(f"**After:** {corr['New Chinese Text']}")
                    st.markdown("---")
        
        # Export results
        st.subheader("📥 Export Results")
        
        # Create Excel file in memory
        output_buffer = io.BytesIO()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        base_name = filename.split('.')[0].replace(' ', '_')
        export_filename = f"MINT_CORRECTED_{base_name}_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
            # Save corrected data
            df.to_excel(writer, sheet_name='Corrected_Data', index=False)
            
            # Save corrections log
            corrections_df = pd.DataFrame(corrections)
            corrections_df.to_excel(writer, sheet_name='Corrections_Log', index=False)
            
            # Add summary sheet
            summary_data = {
                'Metric': [
                    'Total Rows', 'Rows with Mint References', 'Skipped Uncertain',
                    'Total Corrections', 'MINOR Changes', 'MISSING Additions', 'MAJOR Changes'
                ],
                'Count': [
                    len(df), stats['checked_count'], stats['skipped_uncertain'],
                    stats['corrected_count'], stats['change_types']['MINOR'], 
                    stats['change_types']['MISSING'], stats['change_types']['MAJOR']
                ]
            }
            
            if stats['checked_count'] > 0:
                summary_data['Metric'].append('Correction Rate (%)')
                summary_data['Count'].append(f"{(stats['corrected_count'] / stats['checked_count'] * 100):.1f}")
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        output_buffer.seek(0)
        
        # Download button
        st.download_button(
            label="📥 Download Corrected Data & Analysis",
            data=output_buffer.getvalue(),
            file_name=export_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download complete mint corrections with detailed log"
        )
        
        st.success(f"🎯 Period-based extraction completed! {stats['corrected_count']} mint corrections applied.")
        
    else:
        st.success("✅ NO CORRECTIONS NEEDED! All mint names are already correct.")
    
    # Show sample results
    st.subheader("👀 Sample Results")
    display_columns = [english_col, chinese_col]
    st.dataframe(df[display_columns].head(10))

# Run the Streamlit app
if __name__ == "__main__":
    main()
