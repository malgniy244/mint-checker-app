#!/usr/bin/env python3
"""
Interactive Mint Checker - Choose your Excel file and columns
"""

import pandas as pd
import re
from datetime import datetime
import os
import glob

class InteractiveMintChecker:
    def __init__(self):
        """Initialize with official mint names database"""
        self.load_official_mint_database()
        
    def load_official_mint_database(self):
        """Load the official mint names from cpun confirmed file"""
        try:
            self.official_mints = pd.read_excel("cpun confirmed mint names.xlsx")
            print(f"✅ Loaded {len(self.official_mints)} official mint names")
            
            # Create exact lookup dictionary
            self.english_to_chinese = {}
            
            for _, row in self.official_mints.iterrows():
                english = str(row['English Mint Name']).strip()
                chinese = str(row['Chinese Mint Name']).strip()
                self.english_to_chinese[english] = chinese
                    
            print(f"📚 Created exact matching for {len(self.english_to_chinese)} mint names")
            
        except Exception as e:
            print(f"❌ Error loading official mint database: {e}")
            raise
    
    def select_excel_file(self):
        """Show available Excel files and let user choose"""
        print("\n📁 AVAILABLE EXCEL FILES:")
        
        # Find all Excel files in current directory
        excel_files = []
        for pattern in ['*.xlsx', '*.xls']:
            excel_files.extend(glob.glob(pattern))
        
        if not excel_files:
            print("❌ No Excel files found in current directory")
            return None
        
        # Show files with numbers
        print("=" * 60)
        for i, filename in enumerate(excel_files, 1):
            try:
                # Try to get basic info about the file
                df = pd.read_excel(filename, nrows=0)  # Just headers
                cols = len(df.columns)
                print(f"{i:2d}. {filename:<40} ({cols} columns)")
            except:
                print(f"{i:2d}. {filename:<40} (⚠️  may be corrupted)")
        
        print("=" * 60)
        
        # Get user choice
        while True:
            try:
                choice = input(f"\nSelect file (1-{len(excel_files)}): ").strip()
                file_index = int(choice) - 1
                
                if 0 <= file_index < len(excel_files):
                    selected_file = excel_files[file_index]
                    print(f"✅ Selected: {selected_file}")
                    return selected_file
                else:
                    print(f"❌ Please enter a number between 1 and {len(excel_files)}")
                    
            except ValueError:
                print("❌ Please enter a valid number")
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Selection cancelled")
                return None
    
    def show_file_structure(self, filename):
        """Show file structure and let user select columns"""
        try:
            print(f"\n📊 ANALYZING FILE: {filename}")
            df = pd.read_excel(filename)
            print(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
            
            # Show column structure
            print(f"\n📋 AVAILABLE COLUMNS:")
            print("=" * 70)
            for i, col in enumerate(df.columns):
                col_letter = chr(65 + i) if i < 26 else f"Col{i}"
                print(f"{col_letter:>3} ({i:2d}): {col}")
            
            # Show sample data
            print(f"\n📝 SAMPLE DATA (first 3 rows):")
            print("=" * 70)
            for idx, row in df.head(3).iterrows():
                print(f"\nRow {idx + 1}:")
                for i, col in enumerate(df.columns[:8]):  # Show first 8 columns
                    col_letter = chr(65 + i) if i < 26 else f"Col{i}"
                    value = str(row[col])[:50] if pd.notna(row[col]) else ""
                    if value:
                        print(f"  {col_letter}: {value}{'...' if len(str(row[col])) > 50 else ''}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None
    
    def select_columns(self, df):
        """Let user select English and Chinese columns"""
        print(f"\n🎛️  COLUMN SELECTION:")
        print("=" * 50)
        
        # Select English column
        while True:
            try:
                print(f"\nWhich column contains the ENGLISH text (with mint names)?")
                english_choice = input("Enter column letter (A,B,C...) or number (0,1,2...): ").strip().upper()
                
                # Convert to index
                if english_choice.isdigit():
                    english_idx = int(english_choice)
                elif len(english_choice) == 1 and english_choice.isalpha():
                    english_idx = ord(english_choice) - ord('A')
                else:
                    print("❌ Please enter a single letter (A,B,C) or number (0,1,2)")
                    continue
                
                if 0 <= english_idx < len(df.columns):
                    english_col = df.columns[english_idx]
                    print(f"✅ English column: {english_choice} - {english_col}")
                    break
                else:
                    print(f"❌ Column index out of range. Available: 0-{len(df.columns)-1}")
                    
            except (ValueError, IndexError):
                print("❌ Invalid input. Try again.")
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Selection cancelled")
                return None, None
        
        # Select Chinese column
        while True:
            try:
                print(f"\nWhich column contains the CHINESE text (to be corrected)?")
                chinese_choice = input("Enter column letter (A,B,C...) or number (0,1,2...): ").strip().upper()
                
                # Convert to index
                if chinese_choice.isdigit():
                    chinese_idx = int(chinese_choice)
                elif len(chinese_choice) == 1 and chinese_choice.isalpha():
                    chinese_idx = ord(chinese_choice) - ord('A')
                else:
                    print("❌ Please enter a single letter (A,B,C) or number (0,1,2)")
                    continue
                
                if 0 <= chinese_idx < len(df.columns):
                    chinese_col = df.columns[chinese_idx]
                    print(f"✅ Chinese column: {chinese_choice} - {chinese_col}")
                    break
                else:
                    print(f"❌ Column index out of range. Available: 0-{len(df.columns)-1}")
                    
            except (ValueError, IndexError):
                print("❌ Invalid input. Try again.")
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Selection cancelled")
                return None, None
        
        return english_idx, chinese_idx
    
    def find_english_mint_in_text(self, text):
        """Find English mint name in text - ONLY between two periods"""
        if not text or not isinstance(text, str):
            return None
        
        # EXCLUDE uncertain/approximate references
        uncertainty_words = [
            'uncertain', 'likely', 'probably', 'possibly', 'maybe', 'perhaps',
            'or', 'either', 'unknown', 'unidentified', 'attributed', 'tentative'
        ]
        
        # Check if text contains uncertainty words (but allow "Uncertain Mint" as it's in database)
        text_lower = text.lower()
        for word in uncertainty_words:
            if word in text_lower and "uncertain mint" not in text_lower:
                return None
        
        # Find all segments between periods
        segments = text.split('.')
        
        for i, segment in enumerate(segments):
            segment = segment.strip()
            
            # Skip empty segments
            if not segment:
                continue
            
            # Check if this segment contains a mint name and appears to be after a year
            for official_mint in self.english_to_chinese.keys():
                # Use word boundaries to ensure exact matching
                escaped_mint = re.escape(official_mint)
                pattern = r'\b' + escaped_mint + r'\b'
                
                if re.search(pattern, segment, re.IGNORECASE):
                    # Found a mint in this segment
                    # Check if the previous segment (before this period) contains a year
                    if i > 0:
                        prev_segment = segments[i-1].strip()
                        
                        # Check if previous segment contains a year pattern
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
                        
                        # Also check for year patterns anywhere in the previous segments
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
    
    def extract_current_chinese_mint(self, chinese_text):
        """Extract current Chinese mint name from text"""
        if not chinese_text or not isinstance(chinese_text, str):
            return None
            
        # Look for mint patterns
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
    
    def smart_add_mint_name(self, chinese_text, mint_name):
        """Smartly add mint name without creating double periods"""
        chinese_text = chinese_text.strip()
        
        # If text already ends with period, just add mint name (no extra period)
        if chinese_text.endswith('。'):
            return f"{chinese_text}{mint_name}"
        
        # If text doesn't end with period, add period then mint name
        else:
            return f"{chinese_text}。{mint_name}"
    
    def process_file(self, filename, english_col_idx, chinese_col_idx):
        """Process the selected file with chosen columns"""
        try:
            df = pd.read_excel(filename)
            english_col = df.columns[english_col_idx]
            chinese_col = df.columns[chinese_col_idx]
            inventory_col = df.columns[0]  # Use first column for inventory
            
            print(f"\n🔍 PROCESSING MINT NAMES:")
            print(f"📁 File: {filename}")
            print(f"📊 English Column: {english_col}")
            print(f"📊 Chinese Column: {chinese_col}")
            print("🎯 Period-based extraction: mint names between periods after year")
            print("=" * 70)
            
            corrections = []
            checked_count = 0
            corrected_count = 0
            skipped_uncertain = 0
            
            # Process each row
            for index, row in df.iterrows():
                english_text = str(row[english_col]) if pd.notna(row[english_col]) else ""
                chinese_text = str(row[chinese_col]) if pd.notna(row[chinese_col]) else ""
                inventory_id = str(row[inventory_col]) if pd.notna(row[inventory_col]) else f"Row {index + 2}"
                
                # Check if English text contains a mint reference
                if 'Mint' in english_text or 'mint' in english_text:
                    checked_count += 1
                    
                    # Find the English mint name (will return None for uncertain cases)
                    english_mint = self.find_english_mint_in_text(english_text)
                    
                    if english_mint is None and any(word in english_text.lower() for word in ['uncertain', 'likely', 'or']) and "uncertain mint" not in english_text.lower():
                        skipped_uncertain += 1
                        continue
                    
                    if english_mint and english_mint in self.english_to_chinese:
                        official_chinese = self.english_to_chinese[english_mint]
                        current_chinese_mint = self.extract_current_chinese_mint(chinese_text)
                        
                        # Check if correction is needed
                        if current_chinese_mint != official_chinese:
                            # Create corrected Chinese text
                            if current_chinese_mint:
                                # Replace existing mint name
                                corrected_chinese = chinese_text.replace(current_chinese_mint, official_chinese)
                            else:
                                # Add mint name smartly (avoiding double periods)
                                corrected_chinese = self.smart_add_mint_name(chinese_text, official_chinese)
                            
                            # Update the DataFrame
                            df.at[index, chinese_col] = corrected_chinese
                            
                            # Determine change type
                            if current_chinese_mint is None:
                                change_type = "MISSING"  # No Chinese mint → Added Chinese mint
                            elif current_chinese_mint.replace('鑄幣廠', '造幣廠') == official_chinese:
                                change_type = "MINOR"    # Only 鑄幣廠 → 造幣廠 change
                            else:
                                change_type = "MAJOR"    # Other significant changes
                            
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
            
            # Count change types
            change_types = {'MINOR': 0, 'MISSING': 0, 'MAJOR': 0}
            for corr in corrections:
                change_types[corr['Change Type']] += 1
            
            print(f"\n📊 RESULTS:")
            print(f"   Rows with 'Mint': {checked_count}")
            print(f"   ⚠️  Skipped uncertain: {skipped_uncertain}")
            print(f"   ✅ Total corrections: {corrected_count}")
            print(f"   📝 MINOR (鑄幣廠→造幣廠): {change_types['MINOR']}")
            print(f"   📋 MISSING (add mint): {change_types['MISSING']}")
            print(f"   🔧 MAJOR (other changes): {change_types['MAJOR']}")
            
            # Show sample corrections (first 5)
            if corrections:
                print(f"\n🔧 SAMPLE CORRECTIONS (first 5):")
                print("=" * 80)
                for i, corr in enumerate(corrections[:5], 1):
                    type_icon = {"MINOR": "📝", "MISSING": "📋", "MAJOR": "🔧"}[corr['Change Type']]
                    print(f"\n{i:2d}. {corr['Inventory']} (Row {corr['Row']}) {type_icon} {corr['Change Type']}")
                    print(f"     English Mint: {corr['English Mint Found']}")
                    print(f"     English: {corr['Full English Text'][:70]}{'...' if len(corr['Full English Text']) > 70 else ''}")
                    print(f"     Before: {corr['Original Chinese']}")
                    print(f"     After:  {corr['New Chinese Text']}")
            
            # Save results
            if corrections:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
                base_name = os.path.splitext(os.path.basename(filename))[0]
                corrected_filename = f"MINT_CORRECTED_{base_name.replace(' ', '_')}_{timestamp}.xlsx"
                
                with pd.ExcelWriter(corrected_filename, engine='openpyxl') as writer:
                    # Save corrected data
                    df.to_excel(writer, sheet_name='Corrected_Data', index=False)
                    
                    # Save corrections log
                    corrections_df = pd.DataFrame(corrections)
                    corrections_df.to_excel(writer, sheet_name='Corrections_Log', index=False)
                
                print(f"\n📄 Results saved to: {corrected_filename}")
                print(f"✅ {corrected_count} mint corrections completed")
            else:
                print(f"\n✅ NO CORRECTIONS NEEDED!")
            
            return df, corrections
            
        except Exception as e:
            print(f"❌ Error processing file: {e}")
            import traceback
            traceback.print_exc()
            return None, None

def main():
    """Main interactive function"""
    print("🏭 INTERACTIVE MINT NAME CHECKER")
    print("=" * 50)
    print("📁 Choose your Excel file")
    print("📊 Select your columns") 
    print("🎯 Period-based extraction with exact matching")
    print("=" * 50)
    
    # Check if official database exists
    if not os.path.exists("cpun confirmed mint names.xlsx"):
        print("❌ cpun confirmed mint names.xlsx not found in current directory")
        return
    
    try:
        checker = InteractiveMintChecker()
        
        # Step 1: Select Excel file
        filename = checker.select_excel_file()
        if not filename:
            return
        
        # Step 2: Show file structure
        df = checker.show_file_structure(filename)
        if df is None:
            return
        
        # Step 3: Select columns
        english_idx, chinese_idx = checker.select_columns(df)
        if english_idx is None or chinese_idx is None:
            return
        
        # Step 4: Process the file
        print(f"\n🚀 STARTING MINT NAME PROCESSING...")
        result = checker.process_file(filename, english_idx, chinese_idx)
        
        if result[0] is not None:
            print(f"\n💡 PROCESSING COMPLETE!")
            print(f"🎯 Period-based extraction working perfectly")
            print(f"📝 Change types classified for easy review")
            print(f"📋 Check the generated Excel file for detailed corrections")
        
    except (EOFError, KeyboardInterrupt):
        print("\n\n❌ Program interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()