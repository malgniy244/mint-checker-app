#!/usr/bin/env python3
"""
Interactive Mint Name Checker - Module Version (Using Your Existing Code)
Automatically corrects Chinese mint names based on English text analysis
"""

import pandas as pd
import re
from datetime import datetime
from typing import List, Dict, Optional
import requests
from io import BytesIO

class InteractiveMintChecker:
    def __init__(self):
        self.english_to_chinese = {}
        self.official_mints = None

    def load_official_mint_database_from_github(self):
        """Load the official mint database from GitHub"""
        try:
            url = "https://raw.githubusercontent.com/malgniy244/mint-checker-app/main/cpun%20confirmed%20mint%20names.xlsx"
            response = requests.get(url)
            response.raise_for_status()
            db_file = BytesIO(response.content)
            return self.load_official_mint_database(db_file)
        except Exception as e:
            raise Exception(f"Could not download database from GitHub: {str(e)}")

    def load_official_mint_database(self, db_source):
        """Load the official mint names from a file path or file object."""
        try:
            # Handle both file paths and file objects
            self.official_mints = pd.read_excel(db_source)
            for _, row in self.official_mints.iterrows():
                english = str(row['English Mint Name']).strip()
                chinese = str(row['Chinese Mint Name']).strip()
                self.english_to_chinese[english] = chinese
            return f"Loaded {len(self.english_to_chinese)} official mint names."
        except Exception as e:
            raise e

    def find_english_mint_in_text(self, text):
        """Find English mint name in text with uncertainty filtering"""
        if not text or not isinstance(text, str): 
            return None
            
        uncertainty_words = ['uncertain', 'likely', 'probably', 'possibly', 'maybe', 'perhaps', 'or', 'either', 'unknown', 'unidentified', 'attributed', 'tentative']
        text_lower = text.lower()
        
        for word in uncertainty_words:
            if word in text_lower and "uncertain mint" not in text_lower: 
                return None
                
        segments = text.split('.')
        for i, segment in enumerate(segments):
            segment = segment.strip()
            if not segment: 
                continue
                
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
                        if has_year: 
                            return official_mint
        return None

    def extract_current_chinese_mint(self, chinese_text):
        """Extract current Chinese mint name from text"""
        if not chinese_text or not isinstance(chinese_text, str): 
            return None
            
        patterns = [r'([^。，\s]{2,15})造币厂', r'([^。，\s]{2,15})铸币厂', r'造币总厂', r'宝德局']
        for pattern in patterns:
            if match := re.search(pattern, chinese_text): 
                return match.group(0)
        return None

    def smart_add_mint_name(self, chinese_text, mint_name):
        """Smart addition of mint name to Chinese text"""
        chinese_text = chinese_text.strip()
        return f"{chinese_text}{mint_name}" if chinese_text.endswith('。') else f"{chinese_text}。{mint_name}"

    def process_file(self, df, english_col, chinese_col):
        """Process file and return corrections (your existing logic)"""
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
                        
                        if current_chinese_mint is None: 
                            change_type = "MISSING"
                        elif current_chinese_mint.replace('铸币厂', '造币厂') == official_chinese: 
                            change_type = "MINOR"
                        else: 
                            change_type = "MAJOR"
                            
                        corrections.append({
                            'Inventory': inventory_id, 
                            'Row': index + 2, 
                            'Change Type': change_type, 
                            'English Mint Found': english_mint, 
                            'Full English Text': english_text, 
                            'Original Chinese': chinese_text, 
                            'Current Mint': current_chinese_mint or '[无]', 
                            'Corrected To': official_chinese, 
                            'New Chinese Text': corrected_chinese
                        })
                        corrected_count += 1
                        
        return df, {
            "checked_count": checked_count, 
            "skipped_uncertain": skipped_uncertain, 
            "corrected_count": corrected_count, 
            "corrections": corrections
        }

def validate_mint_names_batch(df: pd.DataFrame, english_col: str, chinese_col: str) -> List[Dict]:
    """
    Validate mint names in a DataFrame.
    Returns list of issues/corrections found.
    """
    checker = InteractiveMintChecker()
    
    # Try to load database
    try:
        checker.load_official_mint_database_from_github()
    except Exception as e:
        # If can't load from GitHub, return empty issues list
        return []
    
    issues = []
    inventory_col = df.columns[0] if len(df.columns) > 0 else None
    
    for index, row in df.iterrows():
        english_text = str(row[english_col]) if pd.notna(row[english_col]) else ""
        chinese_text = str(row[chinese_col]) if pd.notna(row[chinese_col]) else ""
        
        # Skip if no mint mentioned
        if 'Mint' not in english_text and 'mint' not in english_text:
            continue
            
        inventory_id = str(row[inventory_col]) if inventory_col and pd.notna(row[inventory_col]) else f"Row {index + 2}"
        
        # Skip uncertain cases
        if any(word in english_text.lower() for word in ['uncertain', 'likely', 'or']) and "uncertain mint" not in english_text.lower():
            continue
            
        english_mint = checker.find_english_mint_in_text(english_text)
        
        if english_mint and english_mint in checker.english_to_chinese:
            official_chinese = checker.english_to_chinese[english_mint]
            current_chinese_mint = checker.extract_current_chinese_mint(chinese_text)
            
            if current_chinese_mint != official_chinese:
                if current_chinese_mint is None: 
                    change_type = "MISSING_MINT_NAME"
                elif current_chinese_mint.replace('铸币厂', '造币厂') == official_chinese: 
                    change_type = "MINOR_MINT_CORRECTION"
                else: 
                    change_type = "MAJOR_MINT_CORRECTION"
                
                corrected_chinese = chinese_text.replace(current_chinese_mint, official_chinese) if current_chinese_mint else checker.smart_add_mint_name(chinese_text, official_chinese)
                
                issues.append({
                    'Row': index + 2,
                    'Inventory': inventory_id,
                    'Column': f"{english_col} -> {chinese_col}",
                    'Issue_Type': change_type,
                    'English_Text': english_text,
                    'Chinese_Original': chinese_text,
                    'English_Mint_Found': english_mint,
                    'Current_Chinese_Mint': current_chinese_mint or '[无]',
                    'Should_Be': official_chinese,
                    'Corrected_Chinese': corrected_chinese,
                    'Status': 'NEEDS_CORRECTION'
                })
    
    return issues

def export_mint_validation_results(issues: List[Dict], output_filename: str = None) -> str:
    """Export mint validation results to Excel"""
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        output_filename = f"MINT_validation_{timestamp}.xlsx"
    
    if issues:
        output_df = pd.DataFrame(issues)
        output_df.to_excel(output_filename, index=False)
        return f"Exported {len(issues)} mint name issues to {output_filename}"
    else:
        # Create empty file with headers
        empty_df = pd.DataFrame(columns=[
            'Row', 'Inventory', 'Column', 'Issue_Type', 'English_Text', 'Chinese_Original',
            'English_Mint_Found', 'Current_Chinese_Mint', 'Should_Be', 'Corrected_Chinese', 'Status'
        ])
        empty_df.to_excel(output_filename, index=False)
        return f"No mint name issues found - empty report saved to {output_filename}"

# Interactive function for standalone use
def main_interactive_mint():
    """Interactive main function for standalone mint validation."""
    print("INTERACTIVE MINT NAME CHECKER")
    print("=" * 50)
    print("Automatically corrects Chinese mint names based on English text analysis")
    print("=" * 50)
    
    # Demo with sample data
    checker = InteractiveMintChecker()
    
    try:
        result = checker.load_official_mint_database_from_github()
        print(f"✅ {result}")
        
        # Test sample
        test_english = "China, Kiangnan Province, 1 Tael, ND(1899), Mint: Kiangnan"
        test_chinese = "中国江南省造光绪元宝库平一两"
        
        print(f"\nTesting with sample:")
        print(f"English: {test_english}")
        print(f"Chinese: {test_chinese}")
        
        english_mint = checker.find_english_mint_in_text(test_english)
        current_chinese_mint = checker.extract_current_chinese_mint(test_chinese)
        
        print(f"Found English mint: {english_mint}")
        print(f"Current Chinese mint: {current_chinese_mint}")
        
        if english_mint and english_mint in checker.english_to_chinese:
            official_chinese = checker.english_to_chinese[english_mint]
            print(f"Should be: {official_chinese}")
            if current_chinese_mint != official_chinese:
                print("⚠️ Correction needed!")
            else:
                print("✅ Already correct!")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        main_interactive_mint()
    except KeyboardInterrupt:
        print("\nGoodbye!")
