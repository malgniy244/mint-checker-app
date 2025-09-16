#!/usr/bin/env python3
"""
Chinese Banknote Translation Validator - Module Version
Preserves ALL original script logic exactly as provided from clean_banknote_validator.py
"""

import pandas as pd
import re
from typing import Set, Tuple, List, Dict, Optional
from datetime import datetime

# ============================================================================
# REPUBLIC YEAR CONVERSION SYSTEM (EXACT ORIGINAL LOGIC)
# Using Taiwan government table: https://www.ris.gov.tw/app/portal/219
# Western Year - 1911 = Republic Year
# ============================================================================

def republic_to_western(republic_year: int) -> int:
    """Convert Republic year to Western year: Republic Year + 1911 = Western Year"""
    return republic_year + 1911

def western_to_republic(western_year: int) -> int:
    """Convert Western year to Republic year: Western Year - 1911 = Republic Year"""
    return western_year - 1911

def extract_republic_years(text: str) -> List[int]:
    """Extract Republic years from Chinese text and convert to Western years."""
    if not text or not isinstance(text, str):
        return []
    
    republic_years = []
    
    # Pattern: 民國X年 where X is Chinese numeral
    pattern = r'民國([元一二三四五六七八九十壹貳叁肆伍陸柒捌玖拾佰仟萬]+)年'
    matches = re.findall(pattern, text)
    
    for match in matches:
        republic_year = convert_chinese_compound_number(match)
        if republic_year > 0:
            western_year = republic_to_western(republic_year)
            republic_years.append(western_year)
    
    return republic_years

# ============================================================================
# SIMPLIFIED CHINESE NUMBER EXTRACTION FOR BANKNOTES (EXACT ORIGINAL LOGIC)
# Extract ALL Chinese numbers regardless of units
# ============================================================================

# Chinese numeral mappings (EXACT from original)
CHINESE_DIGITS = {
    # Basic characters
    '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
    '六': 6, '七': 7, '八': 8, '九': 9,
    # Traditional/formal characters
    '壹': 1, '貳': 2, '叁': 3, '肆': 4, '伍': 5, 
    '陸': 6, '柒': 7, '捌': 8, '玖': 9,
    # Special characters
    '兩': 2, '両': 2,  # Both variants of "two"
}

PLACE_VALUES = {
    # Basic place values
    '十': 10, '百': 100, '千': 1000, '萬': 10000, '万': 10000,
    # Traditional place values  
    '拾': 10, '佰': 100, '仟': 1000,
}

def convert_chinese_compound_number(chinese_str: str) -> int:
    """Convert compound Chinese numbers to Arabic. (EXACT ORIGINAL LOGIC)"""
    if not chinese_str:
        return 0
    
    # Handle single characters first
    if len(chinese_str) == 1:
        if chinese_str in CHINESE_DIGITS:
            return CHINESE_DIGITS[chinese_str]
        elif chinese_str in PLACE_VALUES:
            return PLACE_VALUES[chinese_str]
        else:
            return 0
    
    # Special case: 元年 = year 1 (EXACT from original)
    if chinese_str == '元' or '元年' in chinese_str:
        return 1
    
    # Parse compound numbers
    result = 0
    temp_num = 0
    
    i = 0
    while i < len(chinese_str):
        char = chinese_str[i]
        
        if char in CHINESE_DIGITS:
            temp_num = CHINESE_DIGITS[char]
            
        elif char in PLACE_VALUES:
            place_value = PLACE_VALUES[char]
            
            # Handle cases where no digit precedes place value
            if temp_num == 0:
                temp_num = 1
            
            if place_value >= 10000:  # 萬 and above
                # For 萬, multiply the accumulated amount by place value
                if temp_num == 0 and result == 0:
                    temp_num = 1  # Handle cases like 萬 alone
                if result > 0:
                    # We have accumulated amount, multiply by 萬
                    result = result * place_value
                else:
                    # No accumulated amount, use temp_num
                    result = temp_num * place_value
                temp_num = 0
            else:  # 十, 百, 千
                result += temp_num * place_value
                temp_num = 0
        
        i += 1
    
    # Add any remaining number
    result += temp_num
    return result

def extract_chinese_numbers_banknote(text: str) -> Set[str]:
    """
    Simplified Chinese number extraction for banknotes. (EXACT ORIGINAL LOGIC)
    Extract ALL Chinese numbers regardless of units (文/錢/分/圓/張/佰/拾).
    """
    if not text or not isinstance(text, str):
        return set()
    
    numbers = set()
    
    # 1. Extract year ranges as single strings FIRST (same as English)
    range_pattern = r'(1[89]\d{2}|20\d{2})-(\d{2}|\d{4})'
    year_ranges = []
    for match in re.finditer(range_pattern, text):
        year_range = match.group(0)
        year_ranges.append(year_range)
        numbers.add(year_range)
    
    # 2. Remove commas from Chinese text and extract Arabic numbers
    text_no_commas = re.sub(r'(\d+(?:,\d+)+)', lambda m: m.group(1).replace(',', ''), text)
    all_arabic_nums = re.findall(r'\d+', text_no_commas)
    for num_str in all_arabic_nums:
        # Skip if this number is part of a year range we already extracted
        is_part_of_range = False
        for year_range in year_ranges:
            if num_str in year_range.replace('-', ''):
                is_part_of_range = True
                break
        if not is_part_of_range:
            numbers.add(num_str)
    
    # 2. Extract Republic years and convert to Western years
    republic_western_years = extract_republic_years(text)
    numbers.update(str(year) for year in republic_western_years)
    
    # Track Republic years to avoid double-counting
    republic_pattern = r'民國([元一二三四五六七八九十壹貳叁肆伍陸柒捌玖拾佰仟萬]+)年'
    republic_matches = re.findall(republic_pattern, text)
    republic_raw_numbers = set()
    for match in republic_matches:
        val = convert_chinese_compound_number(match)
        if val > 0:
            republic_raw_numbers.add(str(val))
    
    # 3. Simplified Chinese number patterns - extract ALL numbers with ANY unit (EXACT ORIGINAL)
    patterns = [
        # Any number + any common banknote unit
        r'([元壹貳叁肆伍陸柒捌玖拾一二三四五六七八九十百千萬佰仟]+)圓',     # X圓 (dollars)
        r'([元壹貳叁肆伍陸柒捌玖拾一二三四五六七八九十百千萬佰仟]+)元',     # X元 (yuan)
        r'([兩両壹貳叁肆伍陸柒捌玖拾一二三四五六七八九十百千萬佰仟]+)張',      # X張 (pieces)
        r'([壹貳叁肆伍陸柒捌玖拾一二三四五六七八九十百千萬佰仟]+)枚',      # X枚 (pieces)
        r'([壹貳叁肆伍陸柒捌玖拾一二三四五六七八九十百千萬佰仟]+)份',      # X份 (copies)
        
        # Standalone numbers (like 壹佰, 拾圓, etc.)
        r'([壹貳叁肆伍陸柒捌玖拾一二三四五六七八九十百千萬佰仟]{2,})',      # Multi-character Chinese numbers
        
        # Special units that might appear
        r'([壹貳叁肆伍陸柒捌玖拾一二三四五六七八九十百千萬佰仟]+)毫',      # X毫
        r'([壹貳叁肆伍陸柒捌玖拾一二三四五六七八九十百千萬佰仟]+)分',      # X分
        r'([壹貳叁肆伍陸柒捌玖拾一二三四五六七八九十百千萬佰仟]+)角',      # X角
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if match:
                val = convert_chinese_compound_number(match)
                if val > 0:
                    # Don't add Republic years that we already converted
                    if str(val) not in republic_raw_numbers:
                        numbers.add(str(val))
    
    return numbers

# ============================================================================
# ENHANCED ENGLISH FILTERING FOR BANKNOTES (EXACT ORIGINAL LOGIC)
# Remove PMG grades, Pick numbers, S/M numbers, etc.
# ============================================================================

def extract_english_numbers_banknote(text: str) -> Dict[str, Set[str]]:
    """
    Enhanced English number extraction for banknotes. (EXACT ORIGINAL LOGIC)
    Cut off everything after the last year to remove catalog junk.
    """
    if not text or not isinstance(text, str):
        return {'numbers': set(), 'years': set(), 'quantities': set()}
    
    # PREPROCESSING: Cut off everything after the last year to remove catalog junk
    # Handle year ranges first to find the correct cut point
    year_range_matches = list(re.finditer(r'\b(1[89]\d{2}|20\d{2})-(\d{2}|\d{4})\b', text))
    year_matches = list(re.finditer(r'\b(1[89]\d{2}|20\d{2})\b', text))
    
    if year_range_matches:
        # Cut after the last year range
        last_year_end = year_range_matches[-1].end()
        text = text[:last_year_end].strip()
    elif year_matches:
        # Cut after the last individual year
        last_year_end = year_matches[-1].end()
        text = text[:last_year_end].strip()
    
    result = {
        'numbers': set(),
        'years': set(),
        'quantities': set()
    }
    
    # Extract year ranges as single strings FIRST
    year_ranges = []
    range_pattern = r'\b(1[89]\d{2}|20\d{2})-(\d{2}|\d{4})\b'
    for match in re.finditer(range_pattern, text):
        year_ranges.append(match.group(0))  # Keep full range as string
        result['years'].add(match.group(0))
    
    # Remove ALL commas from numbers: "1,000,000" -> "1000000" (EXACT ORIGINAL)
    text_no_commas = re.sub(r'(\d+(?:,\d+)+)', lambda m: m.group(1).replace(',', ''), text)
    
    # Extract years from full dates first: "14.11.1898" -> "1898" (EXACT ORIGINAL)
    date_patterns = [
        r'\b(\d{1,2})\.(\d{1,2})\.(1[89]\d{2}|20\d{2})\b',  # DD.MM.YYYY
        r'\b(\d{1,2})/(\d{1,2})/(1[89]\d{2}|20\d{2})\b',   # DD/MM/YYYY
        r'\b(\d{1,2})-(\d{1,2})-(1[89]\d{2}|20\d{2})\b',   # DD-MM-YYYY
    ]
    date_years = set()
    for pattern in date_patterns:
        for match in re.finditer(pattern, text_no_commas):
            year = match.group(3)  # The year part
            date_years.add(year)
            result['years'].add(year)
    
    # Extract all individual numbers (but skip parts of year ranges and dates)
    all_numbers = set()
    for match in re.finditer(r'\d+', text_no_commas):
        number_str = match.group(0)
        # Skip if this number is part of a year range we already extracted
        is_part_of_range = False
        for year_range in year_ranges:
            if number_str in year_range.replace('-', ''):
                is_part_of_range = True
                break
        
        # Skip if this number is part of a date we already processed
        is_part_of_date = False
        for pattern in date_patterns:
            for date_match in re.finditer(pattern, text_no_commas):
                if date_match.start() <= match.start() <= date_match.end():
                    is_part_of_date = True
                    break
            if is_part_of_date:
                break
        
        if not is_part_of_range and not is_part_of_date:
            all_numbers.add(number_str)
    
    # Extract quantity patterns: "Lot of (3)" → 3 (EXACT ORIGINAL)
    quantity_patterns = [
        r'Lot\s+of\s*\((\d+)\)',
        r'Set\s+of\s*\((\d+)\)',
        r'Group\s+of\s*\((\d+)\)',
        r'\((\d+)\)\s*(?:pieces?|notes?|bills?)',
    ]
    for pattern in quantity_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            quantity = match.group(1)
            result['quantities'].add(quantity)
            all_numbers.add(quantity)  # Also add to all numbers
    
    # Since we cut after the year, all remaining numbers are clean
    clean_numbers = all_numbers
    result['numbers'] = clean_numbers
    
    # Categorize numbers (skip year ranges that are already in result['years'])
    for num_str in clean_numbers:
        if num_str not in result['years']:  # Don't re-process year ranges
            try:
                num = int(num_str)
                if 1850 <= num <= 2100:  # Banknote years range
                    result['years'].add(num_str)
            except ValueError:
                # Not a valid integer (shouldn't happen after our processing)
                pass
    
    return result

# ============================================================================
# BANKNOTE ANALYSIS WITH REPUBLIC YEAR MATCHING (EXACT ORIGINAL LOGIC)
# ============================================================================

def analyze_banknote_translation(chinese_text: str, english_text: str) -> Tuple[bool, Set[str], Set[str], str, str]:
    """
    Analyze banknote translation with Republic year conversion. (EXACT ORIGINAL LOGIC)
    
    Key difference from coins: Republic year conversion is critical.
    """
    # Extract numbers
    chinese_numbers = extract_chinese_numbers_banknote(chinese_text)
    english_data = extract_english_numbers_banknote(english_text)
    
    # Combine all English numbers (including quantities and year ranges)
    all_english_numbers = english_data['numbers'].union(english_data['quantities']).union(english_data['years'])
    
    # Handle empty cases
    if not chinese_numbers and not all_english_numbers:
        return True, chinese_numbers, all_english_numbers, "NO_NUMBERS", "No numbers in either text"
    
    # Perfect match (including Republic year conversions)
    if chinese_numbers == all_english_numbers:
        return True, chinese_numbers, all_english_numbers, "MATCH", "Perfect alignment including Republic year conversion"
    
    # Check for Republic year mismatches specifically
    republic_years = extract_republic_years(chinese_text)
    english_years = set()
    for year in english_data['years']:
        try:
            english_years.add(int(year))
        except ValueError:
            # Year ranges like "1973-79" can't be converted to int, skip for now
            pass
    
    republic_year_match = False
    if republic_years and english_years:
        for rep_year in republic_years:
            if rep_year in english_years:
                republic_year_match = True
                break
    
    # Analyze differences
    chinese_extra = chinese_numbers - all_english_numbers
    english_extra = all_english_numbers - chinese_numbers
    
    # HARD_MISMATCH: Both have extra numbers (excluding years if Republic conversion matches)
    if chinese_extra and english_extra:
        # Check if the extras are just year conversion issues
        if republic_year_match:
            # Filter out years from extras (handle both integers and year ranges)
            chinese_non_year = set()
            for x in chinese_extra:
                try:
                    if not (1850 <= int(x) <= 2100):
                        chinese_non_year.add(x)
                except ValueError:
                    # Year ranges or non-numeric, keep them
                    chinese_non_year.add(x)
            
            english_non_year = set()
            for x in english_extra:
                try:
                    if not (1850 <= int(x) <= 2100):
                        english_non_year.add(x)
                except ValueError:
                    # Year ranges or non-numeric, keep them  
                    english_non_year.add(x)
            
            if chinese_non_year and english_non_year:
                notes = f"HARD MISMATCH: Chinese extra: {sorted(chinese_non_year)}, English extra: {sorted(english_non_year)} (years match via Republic conversion)"
                return False, chinese_numbers, all_english_numbers, "HARD_MISMATCH", notes
            else:
                return True, chinese_numbers, all_english_numbers, "ACCEPTABLE", f"Republic year conversion matches: {republic_years} → {sorted(english_years)}"
        else:
            notes = f"HARD MISMATCH: Chinese extra: {sorted(chinese_extra)}, English extra: {sorted(english_extra)}"
            return False, chinese_numbers, all_english_numbers, "HARD_MISMATCH", notes
    
    # Check Republic year conversion specifically
    if republic_years and english_years:
        if republic_year_match:
            # Years match, check other numbers
            if not chinese_extra or not english_extra:
                return True, chinese_numbers, all_english_numbers, "ACCEPTABLE", f"Republic year conversion correct: {republic_years} → {sorted(english_years)}"
        else:
            notes = f"Republic year mismatch: Chinese {republic_years} vs English {sorted(english_years)}"
            return False, chinese_numbers, all_english_numbers, "YEAR_MISMATCH", notes
    
    # Regular mismatch
    notes = ""
    if chinese_extra:
        notes += f"Chinese extra: {sorted(chinese_extra)}. "
    if english_extra:
        notes += f"English extra: {sorted(english_extra)}. "
    
    return False, chinese_numbers, all_english_numbers, "MISMATCH", notes.strip()

def is_banknote_lot(chinese_text: str, english_text: str) -> bool:
    """Detect if this is a Chinese banknote lot. (EXACT ORIGINAL LOGIC)"""
    if not chinese_text or not isinstance(chinese_text, str):
        return False
    
    # Banknote indicators (EXACT from original)
    chinese_banknote_indicators = [
        '民國', '中國銀行', '交通銀行', '中央銀行', '中國通商銀行',
        '中華民國', '中國農民銀行', '福建興業銀行', '廣東省銀行',
        '紙幣', '鈔票', '銀行券', '兌換券'
    ]
    
    for indicator in chinese_banknote_indicators:
        if indicator in chinese_text:
            return True
    
    if isinstance(english_text, str):
        english_banknote_indicators = [
            'Bank of China', 'Central Bank', 'Commercial Bank', 
            'Banknote', 'Note', 'Paper Money', 'Currency'
        ]
        for indicator in english_banknote_indicators:
            if indicator.upper() in english_text.upper():
                return True
    
    return False

# ============================================================================
# MODULE INTERFACE FUNCTION FOR UNIFIED VALIDATOR
# ============================================================================

def validate_banknote_translations_batch(df: pd.DataFrame, chinese_col: str, english_col: str) -> List[Dict]:
    """
    Validate banknote translations in DataFrame.
    Returns list of issues found.
    Preserves ALL original logic from clean_banknote_validator.py
    """
    issues = []
    inventory_col = df.columns[0] if len(df.columns) > 0 else None
    
    # Process ALL rows as banknote lots (EXACT original behavior)
    for index, row in df.iterrows():
        chinese_text = str(row[chinese_col]) if pd.notna(row[chinese_col]) else ""
        english_text = str(row[english_col]) if pd.notna(row[english_col]) else ""
        
        # Skip empty rows
        if not chinese_text or not english_text:
            continue
        
        # Run EXACT original banknote analysis
        match, chinese_numbers, english_numbers, status, notes = analyze_banknote_translation(chinese_text, english_text)
        
        if not match:
            inventory_value = row[inventory_col] if inventory_col else f"Row {index + 2}"
            issues.append({
                'Row': index + 2,
                'Inventory': inventory_value,
                'Column': f"{chinese_col} <-> {english_col}",
                'Issue_Type': f'BANKNOTE_{status}',
                'Chinese_Text': chinese_text,
                'English_Text': english_text,
                'Chinese_Numbers': ', '.join(sorted(chinese_numbers)),
                'English_Numbers': ', '.join(sorted(english_numbers)),
                'Analysis_Notes': notes,
                'Status': 'NEEDS_REVIEW'
            })
    
    return issues

# ============================================================================
# TEST FUNCTIONS (EXACT ORIGINAL EXAMPLES)
# ============================================================================

def test_banknote_cases():
    """Test the provided banknote test cases (EXACT from original)."""
    test_cases = [
        (
            "民國三年交通銀行壹佰圓",
            "100 Yuan, 1.10.1914"
        ),
        (
            "民國七年中國銀行壹，伍 & 拾圓。三張",
            "Lot of (3). 1, 5, & 10 Dollars, 1918"
        ),
        (
            "民國二十一年中國通商銀行拾圓",
            "10 Dollars, 1932"
        ),
    ]
    
    print("Testing banknote cases with preserved original logic:")
    for i, (chinese_text, english_text) in enumerate(test_cases, 1):
        print(f"\n{i}. Chinese: {chinese_text}")
        print(f"   English: {english_text}")
        
        # Extract numbers
        chinese_nums = extract_chinese_numbers_banknote(chinese_text)
        english_data = extract_english_numbers_banknote(english_text)
        all_english = english_data['numbers'].union(english_data['quantities'])
        
        print(f"   Chinese numbers: {sorted(chinese_nums)}")
        print(f"   English numbers: {sorted(all_english)}")
        
        # Analyze
        match, c_nums, e_nums, status, notes = analyze_banknote_translation(chinese_text, english_text)
        
        status_icon = "✅" if match else "❌"
        print(f"   {status_icon} Status: {status}")
        print(f"   Notes: {notes}")

def test_republic_conversion():
    """Test Republic year conversion logic (EXACT from original)."""
    test_cases = [
        (3, 1914, "民國三年 should convert to 1914"),
        (7, 1918, "民國七年 should convert to 1918"), 
        (21, 1932, "民國二十一年 should convert to 1932"),
    ]
    
    print("Testing Republic Year Conversion:")
    for republic_year, expected_western, description in test_cases:
        result = republic_to_western(republic_year)
        status = "✅" if result == expected_western else "❌"
        print(f"   {status} Republic {republic_year} → Western {result} (expected {expected_western}) - {description}")

# Main function for testing
if __name__ == "__main__":
    print("BANKNOTE VALIDATOR MODULE - Testing Original Logic")
    print("=" * 60)
    test_republic_conversion()
    print("=" * 60)
    test_banknote_cases()
    print("=" * 60)
    print("All original logic preserved and ready for unified validator!")
