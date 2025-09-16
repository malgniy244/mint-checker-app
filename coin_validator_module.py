#!/usr/bin/env python3
"""
Complete Fixed Chinese Coin Translation Validator - Module Version
PRESERVES ALL SOPHISTICATED LOGIC FROM complete_fixed_validator.py
Enhanced Chinese compound numeral extraction and smart mismatch detection
"""

import re
import os
import pandas as pd
from typing import Set, Tuple, List, Dict, Optional
from datetime import datetime

# ============================================================================
# COMPLETE CHINESE NUMERAL EXTRACTION SYSTEM
# Based on https://followerstock.blogspot.com/2021/08/blog-post.html
# EXACT COPY from complete_fixed_validator.py
# ============================================================================

# Complete Chinese numeral mappings
CHINESE_DIGITS = {
    # Basic characters (一二三四五六七八九十百千万)
    '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
    '六': 6, '七': 7, '八': 8, '九': 9,
    # Traditional/formal characters (壹贰叁肆伍陆柒捌玖拾佰仟万)
    '壹': 1, '贰': 2, '叁': 3, '肆': 4, '伍': 5, 
    '陆': 6, '柒': 7, '捌': 8, '玖': 9,
}

PLACE_VALUES = {
    # Basic place values
    '十': 10, '百': 100, '千': 1000, '万': 10000, '萬': 10000,
    # Traditional place values  
    '拾': 10, '佰': 100, '仟': 1000,
}

def convert_chinese_compound_number(chinese_str: str) -> int:
    """
    Convert compound Chinese numbers to Arabic.
    
    Examples:
    - 二十二 = 2×10+2 = 22
    - 三十四 = 3×10+4 = 34  
    - 贰佰 = 2×100 = 200
    - 五千三百 = 5×1000+3×100 = 5300
    """
    if not chinese_str:
        return 0
    
    # Handle single characters first
    if len(chinese_str) == 1:
        if chinese_str in CHINESE_DIGITS:
            return CHINESE_DIGITS[chinese_str]
        elif chinese_str in PLACE_VALUES:
            return PLACE_VALUES[chinese_str]  # 十 = 10
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
            
            # Handle cases where no digit precedes place value (e.g., 十八 = 18)
            if temp_num == 0:
                temp_num = 1
            
            if place_value >= 10000:  # 万 and above
                result = (result + temp_num) * place_value
                temp_num = 0
            else:  # 十, 百, 千
                result += temp_num * place_value
                temp_num = 0
        
        i += 1
    
    # Add any remaining number
    result += temp_num
    return result

def extract_chinese_numbers_complete(text: str) -> Set[str]:
    """
    COMPLETELY OVERHAULED Chinese number extraction.
    
    Properly handles:
    - Compound numbers: 二十二→22, 三十四→34, 贰佰→200
    - Traditional characters: 壹→1, 贰→2, 叁→3, etc.
    - Context patterns: 民国X年, X钱Y分, X圆, X文, etc.
    """
    if not text or not isinstance(text, str):
        return set()
    
    numbers = set()
    
    # 1. Extract Arabic numbers first
    arabic_nums = re.findall(r'\d+', text)
    numbers.update(arabic_nums)
    
    # 2. Chinese compound number patterns (PRIORITY ORDER)
    patterns = [
        # Republic/Dynasty years (highest priority)
        r'民国([元一二三四五六七八九十壹贰叁肆伍陆柒捌玖拾佰仟万]+)年',
        r'光绪([元一二三四五六七八九十壹贰叁肆伍陆柒捌玖拾佰仟万]+)年',
        r'宣统([元一二三四五六七八九十壹贰叁肆伍陆柒捌玖拾佰仟万]+)年',
        
        # Large denominations (prevent double counting)
        r'([壹贰叁肆伍陆柒捌玖一二三四五六七八九])佰文',  # X百文
        r'([壹贰叁肆伍陆柒捌玖一二三四五六七八九])仟文',  # X千文
        r'([壹贰叁肆伍陆柒捌玖一二三四五六七八九])角',    # X角 = X*10
        
        # Currency denominations  
        r'([元壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万]+)圆',
        r'([元壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万]+)元(?!年)',  # Exclude 元年
        r'([壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万]+)角',
        r'([壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万]+)分',
        r'([壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万]+)文',
        
        # Traditional weights
        r'([壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万]+)钱',
        r'([壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万]+)两',
        
        # Compound weight patterns (三钱六分)
        r'([壹贰叁肆伍陆柒捌玖一二三四五六七八九十])钱([壹贰叁肆伍陆柒捌玖一二三四五六七八九十])分',
        
        # Standalone year patterns
        r'([壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万]+)年',
        
        # Special coin terms
        r'元宝',  # Always implies 1
        r'每元',  # Per yuan = 1
        r'([壹贰叁肆伍陆柒捌玖一二三四五六七八九十])章噶',  # X tangka
    ]
    
    processed_ranges = []  # Track processed text ranges to avoid duplicates
    
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            # Check for overlap with already processed ranges
            start, end = match.span()
            if any(s <= start < e or s < end <= e for s, e in processed_ranges):
                continue
            
            groups = match.groups()
            
            if pattern.endswith('钱([壹贰叁肆伍陆柒捌玖一二三四五六七八九十])分'):
                # Handle X钱Y分 pattern
                mace_str, candareen_str = groups
                mace_val = convert_chinese_compound_number(mace_str)
                candareen_val = convert_chinese_compound_number(candareen_str)
                if mace_val > 0:
                    numbers.add(str(mace_val))
                if candareen_val > 0:
                    numbers.add(str(candareen_val))
            elif pattern in ['元宝', '每元']:
                # Special cases that always mean 1
                numbers.add('1')
            else:
                # Regular patterns
                for group in groups:
                    if group:
                        if pattern.endswith('佰文'):
                            # X佰文 = X*100
                            digit_val = convert_chinese_compound_number(group)
                            if digit_val > 0:
                                numbers.add(str(digit_val * 100))
                        elif pattern.endswith('仟文'):
                            # X仟文 = X*1000  
                            digit_val = convert_chinese_compound_number(group)
                            if digit_val > 0:
                                numbers.add(str(digit_val * 1000))
                        elif pattern.endswith('角') and len(group) == 1 and group in CHINESE_DIGITS:
                            # Single digit + 角 = X*10 (e.g., 二角 = 20)
                            digit_val = convert_chinese_compound_number(group)
                            if digit_val > 0:
                                numbers.add(str(digit_val * 10))
                        else:
                            # Regular conversion
                            val = convert_chinese_compound_number(group)
                            if val > 0:
                                numbers.add(str(val))
            
            processed_ranges.append((start, end))
    
    # 3. Handle 元年 special case
    if '元年' in text:
        numbers.add('1')
    
    return numbers

def extract_english_numbers_enhanced(text: str) -> Dict[str, Set[str]]:
    """
    Enhanced English number extraction with implied denominations.
    
    Returns:
        Dict with 'numbers', 'years', 'denominations', 'implied_denominations'
    """
    if not text or not isinstance(text, str):
        return {'numbers': set(), 'years': set(), 'denominations': set(), 'implied_denominations': set()}
    
    result = {
        'numbers': set(),
        'years': set(), 
        'denominations': set(),
        'implied_denominations': set()
    }
    
    # Extract all numbers first
    all_numbers = set(re.findall(r'\d+', text))
    result['numbers'] = all_numbers.copy()
    
    # Filter out grading scores
    grading_companies = ['PCGS', 'NGC', 'ANACS', 'GBCA', 'CCG']
    grade_abbreviations = ['AU', 'MS', 'EF', 'VF', 'XF', 'VG', 'F', 'G', 'AG', 'PO']
    
    filtered_numbers = set()
    
    # Remove grading company scores
    for company in grading_companies:
        pattern = rf'{company}\s+(?:[A-Z]+(?:\s+Details)?(?:--[^.]*)?[-\s])?(\d+)'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            filtered_numbers.add(match.group(1))
    
    # Remove grade abbreviation scores  
    for grade in grade_abbreviations:
        pattern = rf'\b{grade}[-\s](\d+)\b'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            filtered_numbers.add(match.group(1))
    
    # Clean numbers (remove grading scores)
    clean_numbers = all_numbers - filtered_numbers
    result['numbers'] = clean_numbers
    
    # Categorize numbers
    for num_str in clean_numbers:
        num = int(num_str)
        if 1800 <= num <= 2100:
            result['years'].add(num_str)
        else:
            result['denominations'].add(num_str)
    
    # Extract IMPLIED denominations from text
    implied_patterns = [
        (r'\bDollar\b', '1'),     # Dollar implies 1
        (r'\bPeso\b', '1'),      # Peso implies 1  
        (r'\bRupee\b', '1'),     # Rupee implies 1
        (r'\bYuan\b', '1'),      # Yuan implies 1
        (r'\bFranc\b', '1'),     # Franc implies 1
        (r'\bMark\b', '1'),      # Mark implies 1
        (r'\bPound\b', '1'),     # Pound implies 1
        (r'\bRuble\b', '1'),     # Ruble implies 1
    ]
    
    for pattern, implied_value in implied_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            # Only add if no explicit number already present for this denomination
            if implied_value not in result['denominations']:
                result['implied_denominations'].add(implied_value)
    
    return result

# ============================================================================
# ERA NAME VALIDATION (ONLY WHEN PRESENT)
# Using Taiwan government table: https://www.ris.gov.tw/documents/html/8/1/219.html
# EXACT COPY from complete_fixed_validator.py
# ============================================================================

OFFICIAL_ERA_TABLE = {
    # Historical zodiac years relevant to coins (1876-1950)
    '丙子': [1876, 1936], '丁丑': [1877, 1937], '戊寅': [1878, 1938], '己卯': [1879, 1939],
    '庚辰': [1880, 1940], '辛巳': [1881, 1941], '壬午': [1882, 1942], '癸未': [1883, 1943],
    '甲申': [1884, 1944], '乙酉': [1885, 1945], '丙戌': [1886, 1946], '丁亥': [1887, 1947],
    '戊子': [1888, 1948], '己丑': [1889, 1949], '庚寅': [1890, 1950], '辛卯': [1891, 1951],
    '壬辰': [1892, 1952], '癸巳': [1893, 1953], '甲午': [1894, 1954], '乙未': [1895, 1955],
    '丙申': [1896, 1956], '丁酉': [1897, 1957], '戊戌': [1898, 1958], '己亥': [1899, 1959],
    '庚子': [1900, 1960], '辛丑': [1901, 1961], '壬寅': [1902, 1962], '癸卯': [1903, 1963],
    '甲辰': [1904, 1964], '乙巳': [1905, 1965], '丙午': [1906, 1966], '丁未': [1907, 1967],
    '戊申': [1908, 1968], '己酉': [1909, 1969], '庚戌': [1910, 1970], '辛亥': [1911, 1971],
    '壬子': [1912, 1972], '癸丑': [1913, 1973], '甲寅': [1914, 1974], '乙卯': [1915, 1975],
}

def extract_era_names(text: str) -> List[str]:
    """Extract era names from Chinese text (ONLY if present)."""
    if not text or not isinstance(text, str):
        return []
    
    found_eras = []
    for era_name in OFFICIAL_ERA_TABLE.keys():
        if era_name in text:
            found_eras.append(era_name)
    
    return found_eras

def validate_era_names(era_names: List[str], english_years: Set[str]) -> Tuple[bool, str]:
    """Validate era names against official table (ONLY when era names are present)."""
    if not era_names:
        return True, "No era names to validate"  # Skip validation if no era names
    
    for era_name in era_names:
        if era_name in OFFICIAL_ERA_TABLE:
            valid_years = OFFICIAL_ERA_TABLE[era_name]
            # Check if any English year matches the era name
            for year_str in english_years:
                if int(year_str) in valid_years:
                    return True, f"Era {era_name} matches year {year_str}"
            # Era name is valid but doesn't match English years
            return False, f"Era {era_name} = {valid_years}, but English has {sorted(english_years)}"
        else:
            # Invalid era name
            return False, f"Invalid era name '{era_name}'"
    
    return False, f"Era validation failed for {era_names}"

# ============================================================================
# SMART MISMATCH DETECTION & ENHANCED STATUS LOGIC
# EXACT COPY from complete_fixed_validator.py
# ============================================================================

def analyze_translation_complete(chinese_text: str, english_text: str) -> Tuple[bool, Set[str], Set[str], str, str]:
    """
    Complete translation analysis with all fixes applied.
    
    Enhanced Status Categories:
    - MATCH: Numbers align properly including compound Chinese numerals
    - HARD_MISMATCH: Both Chinese and English have extra numbers (real errors)  
    - ERA_MISMATCH: Era name present but invalid or wrong year match
    - DENOMINATION_MISMATCH: Traditional measurements don't match exactly
    - ACCEPTABLE: ND flexibility, implied denominations, etc.
    """
    
    # Extract numbers using COMPLETE systems
    chinese_numbers = extract_chinese_numbers_complete(chinese_text)
    english_data = extract_english_numbers_enhanced(english_text)
    
    # Combine English numbers (explicit + implied)
    all_english_numbers = english_data['numbers'].union(english_data['implied_denominations'])
    
    # Handle empty cases
    if not chinese_numbers and not all_english_numbers:
        return True, chinese_numbers, all_english_numbers, "NO_NUMBERS", "No numbers in either text"
    
    # Perfect match
    if chinese_numbers == all_english_numbers:
        return True, chinese_numbers, all_english_numbers, "MATCH", "Perfect number alignment with FIXED extraction"
    
    # Era name validation (ONLY if era names present in Chinese)
    era_names = extract_era_names(chinese_text)
    if era_names:
        era_valid, era_msg = validate_era_names(era_names, english_data['years'])
        if not era_valid:
            return False, chinese_numbers, all_english_numbers, "ERA_MISMATCH", era_msg
        # If era valid, continue with other checks
    
    # SMART MISMATCH DETECTION: Both have extra numbers = HARD_MISMATCH
    chinese_extra = chinese_numbers - all_english_numbers
    english_extra = all_english_numbers - chinese_numbers
    
    if chinese_extra and english_extra:
        notes = f"HARD MISMATCH: Chinese extra: {sorted(chinese_extra)}, English extra: {sorted(english_extra)}"
        return False, chinese_numbers, all_english_numbers, "HARD_MISMATCH", notes
    
    # Traditional denomination implied (Chinese adds 1)
    if chinese_extra == {"1"} and not english_extra:
        return True, chinese_numbers, all_english_numbers, "ACCEPTABLE", "Chinese correctly adds implied '1'"
    
    # ND pattern handling
    if re.search(r'\bND\b', str(english_text), re.IGNORECASE):
        # Simple ND flexibility
        if not chinese_extra or not english_extra:
            return True, chinese_numbers, all_english_numbers, "ACCEPTABLE", "ND pattern allows flexibility"
    
    # Traditional measurement check
    traditional_terms = ['钱', '分', '两', '文', '厘']
    english_measurements = ['mace', 'candareen', 'tael', 'cash', 'li']
    
    has_chinese_traditional = any(term in str(chinese_text) for term in traditional_terms)
    has_english_measurements = any(term.lower() in str(english_text).lower() for term in english_measurements)
    
    if has_chinese_traditional and has_english_measurements:
        # Traditional measurements should match exactly
        if chinese_numbers != all_english_numbers:
            return False, chinese_numbers, all_english_numbers, "DENOMINATION_MISMATCH", "Traditional measurements don't match exactly"
        else:
            return True, chinese_numbers, all_english_numbers, "MATCH", "Traditional measurements match"
    
    # Regular mismatch (not hard mismatch)
    notes = ""
    if chinese_extra:
        notes += f"Chinese extra: {sorted(chinese_extra)}. "
    if english_extra:
        notes += f"English extra: {sorted(english_extra)}. "
    
    return False, chinese_numbers, all_english_numbers, "MISMATCH", notes.strip()

def is_chinese_lot(chinese_text: str, english_text: str) -> bool:
    """Detect if this is a Chinese coin lot."""
    if not chinese_text or not isinstance(chinese_text, str):
        return False
    
    chinese_indicators = [
        '民国', '光绪', '宣统', '咸丰', '同治', '康熙', '雍正', '乾隆',
        '中国', '中华', '清朝', '大清', '户部', '官局', '造币',
        '文', '圆', '元', '钱', '分', '两', '厘', '角',
        '四川', '福建', '广东', '北洋', '湖北', '江南', '奉天'
    ]
    
    for indicator in chinese_indicators:
        if indicator in chinese_text:
            return True
    
    if isinstance(english_text, str):
        english_indicators = ['CHINA', 'Chinese', 'Qing', 'Republic of China', 'Cash', 'Tael', 'Mace']
        for indicator in english_indicators:
            if indicator.upper() in english_text.upper():
                return True
    
    return False

# ============================================================================
# MODULE INTERFACE FUNCTIONS
# Adapted to work with the unified validator system
# ============================================================================

def validate_coin_translations_batch(df: pd.DataFrame, chinese_col: str, english_col: str) -> List[Dict]:
    """
    Validate coin translations in a DataFrame.
    Returns list of issues found.
    PRESERVES ALL LOGIC from analyze_and_export_complete_fixed()
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
        
        # Check if it's a Chinese coin lot
        if not is_chinese_lot(chinese_text, english_text):
            continue
        
        # Run COMPLETE FIXED analysis
        match, chinese_numbers, english_numbers, status, notes = analyze_translation_complete(
            chinese_text, english_text
        )
        
        if not match:
            inventory_value = row[inventory_col] if inventory_col else f"Row {index + 2}"
            issues.append({
                'Row': index + 2,
                'Inventory': inventory_value,
                'Column': f"{chinese_col} <-> {english_col}",
                'Issue_Type': f'COIN_TRANSLATION_{status}',
                'Chinese_Text': chinese_text,
                'English_Text': english_text,
                'Chinese_Numbers': ', '.join(sorted(chinese_numbers)),
                'English_Numbers': ', '.join(sorted(english_numbers)),
                'Analysis_Notes': notes,
                'Status': 'NEEDS_REVIEW'
            })
    
    return issues

def export_coin_validation_results(issues: List[Dict], output_filename: str = None) -> str:
    """Export coin validation results to Excel"""
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        output_filename = f"COIN_validation_{timestamp}.xlsx"
    
    if issues:
        output_df = pd.DataFrame(issues)
        output_df.to_excel(output_filename, index=False)
        return f"Exported {len(issues)} coin translation issues to {output_filename}"
    else:
        # Create empty file with headers
        empty_df = pd.DataFrame(columns=[
            'Row', 'Inventory', 'Column', 'Issue_Type', 'Chinese_Text', 'English_Text',
            'Chinese_Numbers', 'English_Numbers', 'Analysis_Notes', 'Status'
        ])
        empty_df.to_excel(output_filename, index=False)
        return f"No coin translation issues found - empty report saved to {output_filename}"

# Interactive functions for standalone use
def main_interactive_coin():
    """Interactive main function for standalone coin validation."""
    print("COMPLETE FIXED CHINESE COIN VALIDATOR")
    print("=" * 70)
    print("Enhanced Chinese compound numeral extraction")
    print("English implied denomination recognition") 
    print("Era name validation ONLY when present in Chinese text")
    print("Smart mismatch detection")
    print("Enhanced status logic with precise error categorization")
    print("=" * 70)
    
    # Demo with sample data
    test_cases = [
        ("民国二十二年孙中山像壹圆", "Dollar, Year 22"),
        ("光绪三年广东省造库平七钱二分", "Kuang Hsu, Year 3, 7 Mace 2 Candareen"),
        ("宣统元年大清银币", "Hsuan Tung, Year 1"),
    ]
    
    print("\nTesting with sample cases:")
    for i, (chinese, english) in enumerate(test_cases, 1):
        print(f"\n{i}. Chinese: {chinese}")
        print(f"   English: {english}")
        
        match, c_nums, e_nums, status, notes = analyze_translation_complete(chinese, english)
        print(f"   Result: {status} ({'PASS' if match else 'FAIL'})")
        print(f"   Chinese numbers: {sorted(c_nums)}")
        print(f"   English numbers: {sorted(e_nums)}")
        print(f"   Notes: {notes}")

if __name__ == "__main__":
    try:
        main_interactive_coin()
    except KeyboardInterrupt:
        print("\nGoodbye!")
