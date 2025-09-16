#!/usr/bin/env python3
"""
Mint Checker Module - Complete Version
Exports validate_mint_names_batch function for unified validator
"""

import pandas as pd
import re
from datetime import datetime
import requests
from io import BytesIO
from typing import Optional, List, Dict

class InteractiveMintChecker:
    def __init__(self):
        """Initialize with official mint names database"""
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
        """Load the official mint names from file"""
        try:
            self.official_mints = pd.read_excel(db_source)
            self.english_to_chinese = {}
            
            for _, row in self.official_mints.iterrows():
                english = str(row['English Mint Name']).strip()
                chinese = str(row['Chinese Mint Name']).strip()
                self.english_to_chinese[english] = chinese
            
            return len(self.english_to_chinese)
            
        except Exception as e:
            raise Exception(f"Error loading official mint database: {e}")

    def find_english_mint_in_text(self, text):
        """Find English mint name in text - ONLY between two periods (EXACT ORIGINAL LOGIC)"""
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

    def extract_current_chinese_mint(self, chinese_text):
        """Extract current Chinese mint name from text (EXACT ORIGINAL LOGIC)"""
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

    def smart_add_mint_name(self, chinese_text, mint_name):
        """Smartly add mint name without creating double periods (EXACT ORIGINAL LOGIC)"""
        chinese_text = chinese_text.strip()
        
        # If text already ends with period, just add mint name (no extra period)
        if chinese_text.endswith('。'):
            return f"{chinese_text}{mint_name}"
        
        # If text doesn't end with period, add period then mint name
        else:
            return f"{chinese_text}。{mint_name}"

    def classify_change_type(self, current_chinese_mint, official_chinese):
        """Classify the type of change (EXACT ORIGINAL LOGIC)"""
        if current_chinese_mint is None:
            return "MISSING"  # No Chinese mint → Added Chinese mint
        elif current_chinese_mint.replace('鑄幣廠', '造幣廠') == official_chinese:
            return "MINOR"    # Only 鑄幣廠 → 造幣廠 change
        else:
            return "MAJOR"    # Other significant changes

def validate_mint_names_batch(df: pd.DataFrame, english_col: str, chinese_col: str) -> List[Dict]:
    """
    Validate mint names in DataFrame - the function your unified app expects.
    Returns list of issues found.
    """
    checker = InteractiveMintChecker()
    
    # Load database
    try:
        checker.load_official_mint_database_from_github()
    except Exception as e:
        # Return error as issue
        return [{
            'Row': 1,
            'Inventory': 'SYSTEM',
            'Column': 'DATABASE',
            'Issue_Type': 'DATABASE_ERROR',
            'Status': f'Could not load mint database: {str(e)}'
        }]
    
    issues = []
    inventory_col = df.columns[0] if len(df.columns) > 0 else None
    
    for index, row in df.iterrows():
        english_text = str(row[english_col]) if pd.notna(row[english_col]) else ""
        chinese_text = str(row[chinese_col]) if pd.notna(row[chinese_col]) else ""
        
        # Check if English text contains a mint reference
        if 'Mint' in english_text or 'mint' in english_text:
            
            # Find the English mint name (will return None for uncertain cases)
            english_mint = checker.find_english_mint_in_text(english_text)
            
            # Skip uncertain references
            if english_mint is None and any(word in english_text.lower() for word in ['uncertain', 'likely', 'or']) and "uncertain mint" not in english_text.lower():
                continue
            
            if english_mint and english_mint in checker.english_to_chinese:
                official_chinese = checker.english_to_chinese[english_mint]
                current_chinese_mint = checker.extract_current_chinese_mint(chinese_text)
                
                # Check if correction is needed
                if current_chinese_mint != official_chinese:
                    inventory_value = row[inventory_col] if inventory_col else f"Row {index + 2}"
                    
                    # Determine change type
                    change_type = checker.classify_change_type(current_chinese_mint, official_chinese)
                    
                    issues.append({
                        'Row': index + 2,
                        'Inventory': inventory_value,
                        'Column': f"{english_col} -> {chinese_col}",
                        'Issue_Type': f'MINT_{change_type}',
                        'English_Text': english_text,
                        'Chinese_Text': chinese_text,
                        'English_Mint_Found': english_mint,
                        'Current_Chinese_Mint': current_chinese_mint or '[無]',
                        'Correct_Chinese_Mint': official_chinese,
                        'Status': 'NEEDS_REVIEW'
                    })
    
    return issues
