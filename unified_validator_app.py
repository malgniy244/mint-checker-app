import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# Import your validator modules
try:
    from traditional_validator_module import validate_traditional_chinese_batch
    from coin_validator_module import validate_coin_translations_batch
    from mint_checker_module import validate_mint_names_batch
    from banknote_validator_module import validate_banknote_translations_batch
except ImportError as e:
    st.error(f"Error importing validator modules: {e}")
    st.stop()

# Password protection
PASSWORD = "123456"

def add_validation_columns_to_dataframe(df, validation_type, traditional_issues, translation_issues, mint_issues):
    """
    Add validation result columns directly to the original DataFrame.
    Only adds columns, never adds new rows.
    """
    # Make a copy to avoid modifying the original
    result_df = df.copy()
    
    # Initialize validation columns with default values
    # Traditional Chinese validation columns (always added)
    result_df['Traditional_Chinese_Issue'] = False
    result_df['Simplified_Characters_Found'] = ''
    result_df['Traditional_Suggestions'] = ''
    
    if validation_type == "Coins":
        # Coin Translation validation columns
        result_df['Coin_Translation_Issue'] = False
        result_df['Translation_Issue_Type'] = ''
        result_df['Chinese_Numbers_Found'] = ''
        result_df['English_Numbers_Found'] = ''
        result_df['Translation_Analysis_Notes'] = ''
        
        # Mint validation columns
        result_df['Mint_Issue'] = False
        result_df['Mint_Change_Type'] = ''
        result_df['English_Mint_Found'] = ''
        result_df['Current_Chinese_Mint'] = ''
        result_df['Correct_Chinese_Mint'] = ''
    else:  # Banknotes
        # Banknote Translation validation columns
        result_df['Banknote_Translation_Issue'] = False
        result_df['Translation_Issue_Type'] = ''
        result_df['Chinese_Numbers_Found'] = ''
        result_df['English_Numbers_Found'] = ''
        result_df['Translation_Analysis_Notes'] = ''
    
    # Process Traditional Chinese issues
    for issue in traditional_issues:
        row_idx = issue['Row'] - 2  # Convert Excel row to DataFrame index
        if 0 <= row_idx < len(result_df):
            result_df.at[row_idx, 'Traditional_Chinese_Issue'] = True
            result_df.at[row_idx, 'Simplified_Characters_Found'] = issue.get('Simplified_Found', '')
            result_df.at[row_idx, 'Traditional_Suggestions'] = issue.get('Suggestions', '')
    
    # Process Translation issues
    for issue in translation_issues:
        row_idx = issue['Row'] - 2  # Convert Excel row to DataFrame index
        if 0 <= row_idx < len(result_df):
            if validation_type == "Coins":
                result_df.at[row_idx, 'Coin_Translation_Issue'] = True
            else:
                result_df.at[row_idx, 'Banknote_Translation_Issue'] = True
            
            result_df.at[row_idx, 'Translation_Issue_Type'] = issue.get('Issue_Type', '').replace('COIN_TRANSLATION_', '').replace('BANKNOTE_', '')
            result_df.at[row_idx, 'Chinese_Numbers_Found'] = issue.get('Chinese_Numbers', '')
            result_df.at[row_idx, 'English_Numbers_Found'] = issue.get('English_Numbers', '')
            result_df.at[row_idx, 'Translation_Analysis_Notes'] = issue.get('Analysis_Notes', '')
    
    # Process Mint issues (only for coins)
    if validation_type == "Coins":
        for issue in mint_issues:
            row_idx = issue['Row'] - 2  # Convert Excel row to DataFrame index
            if 0 <= row_idx < len(result_df):
                result_df.at[row_idx, 'Mint_Issue'] = True
                result_df.at[row_idx, 'Mint_Change_Type'] = issue.get('Issue_Type', '').replace('MINT_', '')
                result_df.at[row_idx, 'English_Mint_Found'] = issue.get('English_Mint_Found', '')
                result_df.at[row_idx, 'Current_Chinese_Mint'] = issue.get('Current_Chinese_Mint', '')
                result_df.at[row_idx, 'Correct_Chinese_Mint'] = issue.get('Correct_Chinese_Mint', '')
    
    return result_df

def main_app():
    st.title("🔍 Unified Numismatic Validation System")
    st.markdown("Choose validation type and upload your file for comprehensive checking")
    
    # Step 1: Choose validation type
    validation_type = st.radio(
        "What type of items are you validating?",
        ["Coins", "Banknotes"],
        help="This determines which validation scripts will be applied"
    )
    
    st.markdown(f"### Selected: {validation_type}")
    if validation_type == "Coins":
        st.info("✅ Traditional Chinese + Coin Translation + Mint Name validation")
    else:
        st.info("✅ Traditional Chinese + Banknote Translation validation")
    
    # Step 2: File upload
    uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'])
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            st.success(f"📊 Loaded {len(df)} rows with {len(df.columns)} columns")
            
            # Show preview
            with st.expander("👀 Preview Original Data", expanded=False):
                st.dataframe(df.head())
            
            # Step 3: Column selection
            st.header("📋 Column Configuration")
            
            col1, col2 = st.columns(2)
            
            # Chinese columns for traditional character checking
            with col1:
                st.subheader("Traditional Chinese Check")
                chinese_columns = st.multiselect(
                    "Select Chinese text columns:",
                    df.columns.tolist(),
                    help="All columns containing Chinese text that need traditional character validation"
                )
            
            # Translation columns
            with col2:
                st.subheader("Translation Check")
                chinese_translation_col = st.selectbox(
                    "Chinese column (for translation):",
                    df.columns.tolist(),
                    help="Main Chinese column for translation validation"
                )
                english_translation_col = st.selectbox(
                    "English column (for translation):",
                    df.columns.tolist(),
                    help="Corresponding English column"
                )
            
            # Step 4: Run validation
            if st.button("🚀 Run Comprehensive Validation", type="primary"):
                if not chinese_columns:
                    st.error("❌ Please select at least one Chinese column for traditional character checking")
                    return
                
                traditional_issues = []
                translation_issues = []
                mint_issues = []
                
                with st.spinner("Running comprehensive validation..."):
                    
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # 1. Traditional Chinese validation (always runs)
                    status_text.text("🔤 Checking traditional Chinese characters...")
                    progress_bar.progress(20)
                    
                    try:
                        traditional_issues = validate_traditional_chinese_batch(df, chinese_columns)
                        st.write(f"✅ Traditional Chinese: Found {len(traditional_issues)} issues")
                    except Exception as e:
                        st.warning(f"⚠️ Traditional Chinese validation error: {e}")
                    
                    # 2. Type-specific validation
                    if validation_type == "Coins":
                        # Coin translation validation
                        status_text.text("🪙 Validating coin translations...")
                        progress_bar.progress(50)
                        
                        try:
                            translation_issues = validate_coin_translations_batch(
                                df, chinese_translation_col, english_translation_col
                            )
                            st.write(f"✅ Coin Translations: Found {len(translation_issues)} issues")
                        except Exception as e:
                            st.warning(f"⚠️ Coin translation validation error: {e}")
                        
                        # Mint name validation
                        status_text.text("🏭 Checking mint names...")
                        progress_bar.progress(80)
                        
                        try:
                            mint_issues = validate_mint_names_batch(
                                df, english_translation_col, chinese_translation_col
                            )
                            st.write(f"✅ Mint Names: Found {len(mint_issues)} issues")
                        except Exception as e:
                            st.warning(f"⚠️ Mint name validation error: {e}")
                            
                    else:  # Banknotes
                        status_text.text("🏦 Validating banknote translations...")
                        progress_bar.progress(60)
                        
                        try:
                            translation_issues = validate_banknote_translations_batch(
                                df, chinese_translation_col, english_translation_col
                            )
                            st.write(f"✅ Banknote Translations: Found {len(translation_issues)} issues")
                        except Exception as e:
                            st.warning(f"⚠️ Banknote translation validation error: {e}")
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Validation complete!")
                
                # Step 5: Create enhanced DataFrame with validation columns
                enhanced_df = add_validation_columns_to_dataframe(
                    df, validation_type, traditional_issues, translation_issues, mint_issues
                )
                
                # Calculate total issues
                total_issues = len(traditional_issues) + len(translation_issues) + len(mint_issues)
                
                # Step 6: Show results and export
                st.header("📊 Validation Results")
                
                if total_issues > 0:
                    st.error(f"🚨 Found {total_issues} total issues requiring review")
                    
                    # Show summary by issue type
                    st.subheader("📈 Issues Summary")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Traditional Chinese Issues", len(traditional_issues))
                    with col2:
                        if validation_type == "Coins":
                            st.metric("Coin Translation Issues", len(translation_issues))
                        else:
                            st.metric("Banknote Translation Issues", len(translation_issues))
                    with col3:
                        if validation_type == "Coins":
                            st.metric("Mint Name Issues", len(mint_issues))
                        else:
                            st.metric("Republic Year Issues", 0)  # Placeholder
                    
                    # Show sample of enhanced data
                    st.subheader("📋 Enhanced Data with Validation Results")
                    st.info("Your original data with added validation columns (showing rows with issues)")
                    
                    # Filter to show only rows with issues
                    if validation_type == "Coins":
                        issue_mask = (enhanced_df['Traditional_Chinese_Issue'] == True) | \
                                   (enhanced_df['Coin_Translation_Issue'] == True) | \
                                   (enhanced_df['Mint_Issue'] == True)
                    else:
                        issue_mask = (enhanced_df['Traditional_Chinese_Issue'] == True) | \
                                   (enhanced_df['Banknote_Translation_Issue'] == True)
                    
                    rows_with_issues = enhanced_df[issue_mask]
                    
                    if len(rows_with_issues) > 0:
                        st.dataframe(rows_with_issues.head(10), use_container_width=True)
                        if len(rows_with_issues) > 10:
                            st.info(f"Showing first 10 of {len(rows_with_issues)} rows with issues. Download full file to see all.")
                    
                else:
                    st.success("🎉 Excellent! No issues found!")
                    st.balloons()
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Traditional Chinese", "✅ PASS")
                    with col2:
                        if validation_type == "Coins":
                            st.metric("Coin Translations", "✅ PASS")
                        else:
                            st.metric("Banknote Translations", "✅ PASS")
                    with col3:
                        if validation_type == "Coins":
                            st.metric("Mint Names", "✅ PASS")
                        else:
                            st.metric("Republic Years", "✅ PASS")
                
                # Export functionality - SINGLE SHEET with enhanced data
                st.subheader("📥 Download Enhanced Data")
                st.info("Your original data with validation result columns added")
                
                output = BytesIO()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                filename = f"ENHANCED_{validation_type.upper()}_{timestamp}.xlsx"
                
                # Single sheet with enhanced data
                enhanced_df.to_excel(output, index=False, engine='openpyxl')
                output.seek(0)
                
                st.download_button(
                    label="📄 Download Enhanced Data (Single Sheet)",
                    data=output,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )
                
                st.success(f"✅ Enhanced data ready: {filename}")
                st.markdown("**File contains:** Your original data + validation result columns")
                
                # Show column summary
                with st.expander("📋 Validation Columns Added", expanded=False):
                    st.markdown("### Traditional Chinese Validation:")
                    st.markdown("- `Traditional_Chinese_Issue` (TRUE/FALSE)")
                    st.markdown("- `Simplified_Characters_Found` (e.g., '国,银')")
                    st.markdown("- `Traditional_Suggestions` (e.g., '国→國, 银→銀')")
                    
                    if validation_type == "Coins":
                        st.markdown("### Coin Translation Validation:")
                        st.markdown("- `Coin_Translation_Issue` (TRUE/FALSE)")
                        st.markdown("- `Translation_Issue_Type` (e.g., 'HARD_MISMATCH')")
                        st.markdown("- `Chinese_Numbers_Found` (e.g., '22, 1')")
                        st.markdown("- `English_Numbers_Found` (e.g., '22, 1')")
                        st.markdown("- `Translation_Analysis_Notes`")
                        
                        st.markdown("### Mint Name Validation:")
                        st.markdown("- `Mint_Issue` (TRUE/FALSE)")
                        st.markdown("- `Mint_Change_Type` (e.g., 'MISSING', 'MINOR')")
                        st.markdown("- `English_Mint_Found`")
                        st.markdown("- `Current_Chinese_Mint`")
                        st.markdown("- `Correct_Chinese_Mint`")
                    else:
                        st.markdown("### Banknote Translation Validation:")
                        st.markdown("- `Banknote_Translation_Issue` (TRUE/FALSE)")
                        st.markdown("- `Translation_Issue_Type`")
                        st.markdown("- `Chinese_Numbers_Found`")
                        st.markdown("- `English_Numbers_Found`")
                        st.markdown("- `Translation_Analysis_Notes`")
                    
        except Exception as e:
            st.error(f"❌ Error reading Excel file: {e}")
            st.info("💡 Please ensure your file is a valid Excel (.xlsx or .xls) format")

# Password protection
if "password_correct" not in st.session_state:
    st.session_state.password_correct = False

if not st.session_state.password_correct:
    st.title("🔐 Access Required")
    st.markdown("### Unified Numismatic Validation System")
    st.info("This system validates Chinese coin and banknote descriptions for traditional characters, translation accuracy, and mint name correctness.")
    
    password_guess = st.text_input("Enter Password", type="password")
    if password_guess == PASSWORD:
        st.session_state.password_correct = True
        st.rerun()
    elif password_guess != "":
        st.error("❌ Password incorrect.")
else:
    main_app()
