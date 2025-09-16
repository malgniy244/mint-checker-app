#!/usr/bin/env python3
"""
Chinese Banknote Translation Validator - Module Version
Specialized for banknotes with Republic year conversion and banknote-specific filtering
"""

import re
import pandas as pd
from typing import Set, Tuple, List, Dict, Optional
from datetime import datetime

# Chinese numeral mappings (same as coin validator)
CHINESE_DIGITS = {
    # Basic characters
    '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
    '六': 6, '七': 7, '八': 8, '九': 9,
    # Traditional/formal characters
    '壹': 1, '贰': 2, '叁': 3, '肆': 4, '伍': 5, 
    '陆': 6, '柒': 7, '捌': 8, '玖': 9,
    # Special characters
    '两': 2, '兩': 2,  # Both variants of "two"
}

PLACE_VALUES = {
    # Basic place values
    '十': 10, '百': 100, '千': 1000, '万': 10000, '萬': 10000,
    # Traditional place values  
    '拾': 10, '佰': 100, '仟': 1000,
}

def republic_to_western(republic_year: int) -> int:
    """Convert Republic year to Western year: Republic Year + 1911 = Western Year"""
    return republic_year + 1911

def western_to_republic(western_year: int) -> int:
    """Convert Western year to Republic year: Western Year - 1911 = Republic Year"""
    return western_year - 1911

def convert_chinese_compound_number(chinese_str: str) -> int:
    """Convert compound Chinese numbers to Arabic."""
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
    
    # Special case: 元年 = year 1
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
            
            if place_value >= 10000:  # 万 and above
                # For 万, multiply the accumulated amount by place value
                if temp_num == 0 and result == 0:
                    temp_num = 1  # Handle cases like 万 alone
                if result > 0:
                    # We have accumulated amount, multiply by 万
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

def extract_republic_years(text: str) -> List[int]:
    """Extract Republic years from Chinese text and convert to Western years."""
    if not text or not isinstance(text, str):
        return []
    
    republic_years = []
    
    # Pattern: 民国X年 where X is Chinese numeral
    pattern = r'民国([元一二三四五六七八九十壹贰叁肆伍陆柒捌玖拾佰仟萬万]+)年'
    matches = re.findall(pattern, text)
    
    for match in matches:
        republic_year = convert_chinese_compound_number(match)
        if republic_year > 0:
            western_year = republic_to_western(republic_year)
            republic_years.append(western_year)
    
    return republic_years

def extract_chinese_numbers_banknote(text: str) -> Set[str]:
    """
    Simplified Chinese number extraction for banknotes.
    Extract ALL Chinese numbers regardless of units.
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
    
    # 3. Extract Republic years and convert to Western years
    republic_western_years = extract_republic_years(text)
    numbers.update(str(year) for year in republic_western_years)
    
    # Track Republic years to avoid double-counting
    republic_pattern = r'民国([元一二三四五六七八九十壹贰叁肆伍陆柒捌玖拾佰仟萬万]+)年'
    republic_matches = re.findall(republic_pattern, text)
    republic_raw_numbers = set()
    for match in republic_matches:
        val = convert_chinese_compound_number(match)
        if val > 0:
            republic_raw_numbers.add(str(val))
    
    # 4. Simplified Chinese number patterns - extract ALL numbers with ANY unit
    patterns = [
        # Any number + any common banknote unit
        r'([元壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万佰仟]+)圆',     # X圆 (dollars)
        r'([元壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万佰仟]+)元',     # X元 (yuan)
        r'([两兩壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万佰仟]+)张',      # X张 (pieces)
        r'([壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万佰仟]+)枚',      # X枚 (pieces)
        r'([壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万佰仟]+)份',      # X份 (copies)
        
        # Standalone numbers (like 壹佰, 拾圆, etc.)
        r'([壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万佰仟]{2,})',      # Multi-character Chinese numbers
        
        # Special units that might appear
        r'([壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万佰仟]+)毫',      # X毫
        r'([壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万佰仟]+)分',      # X分
        r'([壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万佰仟]+)角',      # X角
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

def extract_english_numbers_banknote(text: str) -> Dict[str, Set[str]]:
    """
    Enhanced English number extraction for banknotes.
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
    
    # Remove ALL commas from numbers: "1,000,000" -> "1000000"
    text_no_commas = re.sub(r'(\d+(?:,\d+)+)', lambda m: m.group(1).replace(',', ''), text)
    
    # Extract years from full dates first: "14.11.1898" -> "1898"
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
    
    # Extract quantity patterns: "Lot of (3)" -> 3
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

def analyze_banknote_translation(chinese_text: str, english_text: str) -> Tuple[bool, Set[str], Set[str], str, str]:
    """
    Analyze banknote translation with Republic year conversion.
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
    """Detect if this is a Chinese banknote lot."""
    if not chinese_text or not isinstance(chinese_text, str):
        return False
    
    # Banknote indicators
    chinese_banknote_indicators = [
        '民国', '中国银行', '交通银行', '中央银行', '中国通商银行',
        '中华民国', '中国农民银行', '福建兴业银行', '广东省银行',
        '纸币', '钞票', '银行券', '兑换券'
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

def validate_banknote_translations_batch(df: pd.DataFrame, chinese_col: str, english_col: str) -> List[Dict]:
    """
    Validate banknote translations in a DataFrame.
    Returns list of issues found.
    """
    issues = []
    inventory_col = df.columns[0] if len(df.columns) > 0 else None
    
    for index, row in df.iterrows():
        chinese_text = row[chinese_col]
        english_text = row[english_col]
        
        # Skip empty rows
        if pd.isna(chinese_text) or pd.isna(english_text):
            continue
        
        chinese_text = str(chinese_text)
        english_text = str(english_text)
        
        # Check if it's a banknote (you can skip this check if all rows are banknotes)
        if not is_banknote_lot(chinese_text, english_text):
            continue
        
        # Run banknote analysis
        match, chinese_numbers, english_numbers, status, notes = analyze_banknote_translation(
            chinese_text, english_text
        )
        
        if not match:
            inventory_value = row[inventory_col] if inventory_col else f"Row {index + 2}"
            issues.append({
                'Row': index + 2,
                'Inventory': inventory_value,
                'Column': f"{chinese_col} <-> {english_col}",
                'Issue_Type': f'BANKNOTE_TRANSLATION_{status}',
                'Chinese_Text': chinese_text,
                'English_Text': english_text,
                'Chinese_Numbers': ', '.join(sorted(chinese_numbers)),
                'English_Numbers': ', '.join(sorted(english_numbers)),
                'Analysis_Notes': notes,
                'Status': 'NEEDS_REVIEW'
            })
    
    return issues

def export_banknote_validation_results(issues: List[Dict], output_filename: str = None) -> str:
    """Export banknote validation results to Excel"""
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        output_filename = f"BANKNOTE_validation_{timestamp}.xlsx"
    
    if issues:
        output_df = pd.DataFrame(issues)
        output_df.to_excel(output_filename, index=False)
        return f"Exported {len(issues)} banknote translation issues to {output_filename}"
    else:
        # Create empty file with headers
        empty_df = pd.DataFrame(columns=[
            'Row', 'Inventory', 'Column', 'Issue_Type', 'Chinese_Text', 'English_Text',
            'Chinese_Numbers', 'English_Numbers', 'Analysis_Notes', 'Status'
        ])
        empty_df.to_excel(output_filename, index=False)
        return f"No banknote translation issues found - empty report saved to {output_filename}"

# Interactive function for standalone use
def main_interactive_banknote():
    """Interactive main function for standalone banknote validation."""
    print("CHINESE BANKNOTE TRANSLATION VALIDATOR")
    print("=" * 60)
    print("Republic year conversion (民国X年 → Western Year)")
    print("Simplified Chinese number extraction (all banknote units)")
    print("Enhanced English filtering (PMG grades, Pick numbers)")
    print("Date format handling (1.10.1914 → 1914)")
    print("Quantity pattern extraction (Lot of (3) → 3)")
    print("=" * 60)
    
    # Test with sample cases
    test_cases = [
        (
            "民国三年交通银行壹佰圆",
            "100 Yuan, 1.10.1914"
        ),
        (
            "民国七年中国银行壹，伍 & 拾圆。三张",
            "Lot of (3). 1, 5, & 10 Dollars, 1918"
        ),
        (
            "民国二十一年中国通商银行拾圆",
            "10 Dollars, 1932"
        ),
    ]
    
    print("\nTesting with sample banknote cases:")
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

if __name__ == "__main__":
    try:
        main_interactive_banknote()
    except KeyboardInterrupt:
        print("\nGoodbye!")
