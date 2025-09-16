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
                
                all_issues = []
                
                with st.spinner("Running comprehensive validation..."):
                    
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # 1. Traditional Chinese validation (always runs)
                    status_text.text("🔤 Checking traditional Chinese characters...")
                    progress_bar.progress(20)
                    
                    try:
                        traditional_issues = validate_traditional_chinese_batch(df, chinese_columns)
                        all_issues.extend(traditional_issues)
                        st.write(f"✅ Traditional Chinese: Found {len(traditional_issues)} issues")
                    except Exception as e:
                        st.warning(f"⚠️ Traditional Chinese validation error: {e}")
                    
                    # 2. Type-specific validation
                    if validation_type == "Coins":
                        # Coin translation validation
                        status_text.text("🪙 Validating coin translations...")
                        progress_bar.progress(50)
                        
                        try:
                            coin_issues = validate_coin_translations_batch(
                                df, chinese_translation_col, english_translation_col
                            )
                            all_issues.extend(coin_issues)
                            st.write(f"✅ Coin Translations: Found {len(coin_issues)} issues")
                        except Exception as e:
                            st.warning(f"⚠️ Coin translation validation error: {e}")
                        
                        # Mint name validation
                        status_text.text("🏭 Checking mint names...")
                        progress_bar.progress(80)
                        
                        try:
                            mint_issues = validate_mint_names_batch(
                                df, english_translation_col, chinese_translation_col
                            )
                            all_issues.extend(mint_issues)
                            st.write(f"✅ Mint Names: Found {len(mint_issues)} issues")
                        except Exception as e:
                            st.warning(f"⚠️ Mint name validation error: {e}")
                            
                    else:  # Banknotes
                        status_text.text("🏦 Validating banknote translations...")
                        progress_bar.progress(60)
                        
                        try:
                            banknote_issues = validate_banknote_translations_batch(
                                df, chinese_translation_col, english_translation_col
                            )
                            all_issues.extend(banknote_issues)
                            st.write(f"✅ Banknote Translations: Found {len(banknote_issues)} issues")
                        except Exception as e:
                            st.warning(f"⚠️ Banknote translation validation error: {e}")
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Validation complete!")
                
                # Step 5: Show results and export
                st.header("📊 Validation Results")
                
                if all_issues:
                    st.error(f"🚨 Found {len(all_issues)} total issues requiring review")
                    
                    # Create results dataframe
                    results_df = pd.DataFrame(all_issues)
                    
                    # Show summary by issue type
                    st.subheader("📈 Issues Summary")
                    issue_summary = results_df['Issue_Type'].value_counts()
                    
                    # Display as columns for better layout
                    summary_cols = st.columns(min(3, len(issue_summary)))
                    for i, (issue_type, count) in enumerate(issue_summary.items()):
                        with summary_cols[i % len(summary_cols)]:
                            st.metric(issue_type.replace('_', ' '), count)
                    
                    # Show detailed results (first 10)
                    st.subheader("📋 Detailed Issues (First 10)")
                    display_columns = ['Row', 'Issue_Type', 'Column', 'Status']
                    if 'Original_Text' in results_df.columns:
                        display_columns.append('Original_Text')
                    if 'Chinese_Text' in results_df.columns:
                        display_columns.append('Chinese_Text')
                    
                    st.dataframe(
                        results_df[display_columns].head(10),
                        use_container_width=True
                    )
                    
                    # Export functionality
                    st.subheader("📥 Download Results")
                    
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        # Sheet 1: Original data
                        df.to_excel(writer, sheet_name='Original_Data', index=False)
                        
                        # Sheet 2: All issues found
                        results_df.to_excel(writer, sheet_name='All_Issues', index=False)
                        
                        # Sheet 3: Issues by type
                        for issue_type in results_df['Issue_Type'].unique():
                            type_issues = results_df[results_df['Issue_Type'] == issue_type]
                            sheet_name = issue_type.replace('_', ' ')[:31]  # Excel sheet name limit
                            type_issues.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                        # Sheet 4: Summary
                        summary_data = [
                            ['Total Rows Processed', len(df)],
                            ['Total Issues Found', len(all_issues)],
                            ['Validation Type', validation_type],
                            ['Chinese Columns Checked', ', '.join(chinese_columns)],
                            ['Translation Columns', f"{chinese_translation_col} ↔ {english_translation_col}"],
                            ['Timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                        ]
                        
                        # Add issue type breakdown
                        summary_data.append(['', ''])  # Empty row
                        summary_data.append(['ISSUE TYPE BREAKDOWN', 'COUNT'])
                        for issue_type, count in issue_summary.items():
                            summary_data.append([issue_type, count])
                        
                        summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
                        summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    
                    output.seek(0)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                    filename = f"VALIDATION_{validation_type.upper()}_{timestamp}.xlsx"
                    
                    st.download_button(
                        label="📄 Download Complete Validation Report",
                        data=output,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary"
                    )
                    
                    st.success(f"✅ Report ready for download: {filename}")
                    
                    # Show critical issues that need immediate attention
                    critical_types = [
                        'SIMPLIFIED_CHARACTERS', 
                        'HARD_MISMATCH', 
                        'ERA_MISMATCH', 
                        'YEAR_MISMATCH',
                        'MAJOR_MINT_CORRECTION'
                    ]
                    critical_issues = results_df[results_df['Issue_Type'].isin(critical_types)]
                    
                    if len(critical_issues) > 0:
                        st.subheader("🚨 Critical Issues (Immediate Attention Required)")
                        st.error(f"Found {len(critical_issues)} critical issues")
                        
                        for i, (_, issue) in enumerate(critical_issues.head(5).iterrows()):
                            with st.expander(f"Critical Issue {i+1}: Row {issue['Row']} - {issue['Issue_Type']}"):
                                for key, value in issue.items():
                                    if pd.notna(value) and value != '':
                                        st.write(f"**{key}:** {value}")
                    
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
                    
                    st.markdown("### 🏆 All validations passed successfully!")
                    st.markdown("Your data meets all quality standards for Chinese numismatic descriptions.")
                    
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
