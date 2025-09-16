#!/usr/bin/env python3
"""
Complete Fixed Chinese Coin Translation Validator - Module Version
Enhanced Chinese compound numeral extraction and smart mismatch detection
"""

import re
import os
import pandas as pd
from typing import Set, Tuple, List, Dict, Optional
from datetime import datetime

# Complete Chinese numeral mappings
CHINESE_DIGITS = {
    # Basic characters
    '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, 
    '六': 6, '七': 7, '八': 8, '九': 9,
    # Traditional/formal characters
    '壹': 1, '贰': 2, '叁': 3, '肆': 4, '伍': 5, 
    '陆': 6, '柒': 7, '捌': 8, '玖': 9,
}

PLACE_VALUES = {
    # Basic place values
    '十': 10, '百': 100, '千': 1000, '万': 10000, '萬': 10000,
    # Traditional place values  
    '拾': 10, '佰': 100, '仟': 1000,
}

# Official era table for validation
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

def convert_chinese_compound_number(chinese_str: str) -> int:
    """Convert compound Chinese numbers to Arabic."""
    if not chinese_str:
        return 0
    
    # Handle single characters first
    if len(chinese_str) == 1:
        i += 1
    
    # Add any remaining number
    result += temp_num
    return result

def extract_chinese_numbers_complete(text: str) -> Set[str]:
    """Extract Chinese numbers with compound numeral support."""
    if not text or not isinstance(text, str):
        return set()
    
    numbers = set()
    
    # Extract Arabic numbers first
    arabic_nums = re.findall(r'\d+', text)
    numbers.update(arabic_nums)
    
    # Chinese compound number patterns
    patterns = [
        # Republic/Dynasty years (highest priority)
        r'民国([元一二三四五六七八九十壹贰叁肆伍陆柒捌玖拾佰仟万]+)年',
        r'光绪([元一二三四五六七八九十壹贰叁肆伍陆柒捌玖拾佰仟万]+)年',
        r'宣统([元一二三四五六七八九十壹贰叁肆伍陆柒捌玖拾佰仟万]+)年',
        
        # Currency denominations
        r'([元壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万佰仟]+)圆',
        r'([元壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万佰仟]+)元(?!年)',
        r'([壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万佰仟]+)角',
        r'([壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万佰仟]+)分',
        r'([壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万佰仟]+)文',
        
        # Traditional weights
        r'([壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万佰仟]+)钱',
        r'([壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万佰仟]+)两',
        
        # Standalone year patterns
        r'([壹贰叁肆伍陆柒捌玖拾一二三四五六七八九十百千万佰仟]+)年',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if match:
                val = convert_chinese_compound_number(match)
                if val > 0:
                    numbers.add(str(val))
    
    # Handle 元年 special case
    if '元年' in text:
        numbers.add('1')
    
    return numbers

def extract_english_numbers_enhanced(text: str) -> Dict[str, Set[str]]:
    """Enhanced English number extraction with implied denominations."""
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

def extract_era_names(text: str) -> List[str]:
    """Extract era names from Chinese text."""
    if not text or not isinstance(text, str):
        return []
    
    found_eras = []
    for era_name in OFFICIAL_ERA_TABLE.keys():
        if era_name in text:
            found_eras.append(era_name)
    
    return found_eras

def validate_era_names(era_names: List[str], english_years: Set[str]) -> Tuple[bool, str]:
    """Validate era names against official table."""
    if not era_names:
        return True, "No era names to validate"
    
    for era_name in era_names:
        if era_name in OFFICIAL_ERA_TABLE:
            valid_years = OFFICIAL_ERA_TABLE[era_name]
            for year_str in english_years:
                if int(year_str) in valid_years:
                    return True, f"Era {era_name} matches year {year_str}"
            return False, f"Era {era_name} = {valid_years}, but English has {sorted(english_years)}"
        else:
            return False, f"Invalid era name '{era_name}'"
    
    return False, f"Era validation failed for {era_names}"

def analyze_translation_complete(chinese_text: str, english_text: str) -> Tuple[bool, Set[str], Set[str], str, str]:
    """Complete translation analysis with all fixes applied."""
    
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
        if not chinese_extra or not english_extra:
            return True, chinese_numbers, all_english_numbers, "ACCEPTABLE", "ND pattern allows flexibility"
    
    # Regular mismatch
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

def validate_coin_translations_batch(df: pd.DataFrame, chinese_col: str, english_col: str) -> List[Dict]:
    """
    Validate coin translations in a DataFrame.
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
        
        # Check if it's a Chinese coin
        if not is_chinese_lot(chinese_text, english_text):
            continue
        
        # Run translation analysis
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
        print("\nGoodbye!")f chinese_str in CHINESE_DIGITS:
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
                result = (result + temp_num) * place_value
                temp_num = 0
            else:  # 十, 百, 千
                result += temp_num * place_value
                temp_num = 0
        
        i
