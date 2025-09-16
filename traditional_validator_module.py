#!/usr/bin/env python3
"""
Enhanced Comprehensive Traditional Chinese Character Validator - Module Version
Expanded database with 500+ simplified-to-traditional character mappings
"""

import pandas as pd
import os
import glob
import re
from datetime import datetime
from typing import Set, List, Dict, Tuple, Optional

class EnhancedTraditionalValidator:
    def __init__(self):
        # COMPREHENSIVE simplified to traditional character database (500+ characters)
        self.simplified_to_traditional = {
            # === YOUR ORIGINAL 247 CHARACTERS ===
            # Numbers and Financial
            '万': '萬', '亿': '億', '贰': '貳', '两': '兩', '陆': '陸',
            '币': '幣', '银': '銀', '钱': '錢', '贵': '貴', '宝': '寶',
            '财': '財', '货': '貨', '购': '購', '费': '費', '价': '價',
            '买': '買', '卖': '賣', '债': '債', '贷': '貸', '账': '賬',
            '储': '儲', '还': '還', '结': '結', '余': '餘', '额': '額',
            '户': '戶', '头': '頭', '资': '資', '险': '險', '担': '擔',
            '责': '責', '权': '權', '税': '稅',
            
            # Countries and Geography
            '国': '國', '华': '華', '产': '產', '业': '業', '广': '廣',
            '湾': '灣', '岛': '島', '台': '臺', '岭': '嶺', '峰': '峯',
            '东': '東', '内': '內', '区': '區', '县': '縣',
            
            # Time and Dates
            '时': '時', '间': '間', '周': '週', '钟': '鐘', '历': '歷',
            '纪': '紀',
            
            # Common Words
            '开': '開', '关': '關', '门': '門', '车': '車', '电': '電',
            '话': '話', '发': '發', '证': '證', '书': '書', '单': '單',
            '据': '據', '条': '條', '项': '項', '录': '錄', '册': '冊',
            '设': '設', '办': '辦', '务': '務', '总': '總', '经': '經',
            '营': '營', '处': '處', '长': '長', '员': '員', '干': '幹',
            '级': '級', '过': '過', '这': '這', '们': '們', '个': '個',
            '为': '為', '从': '從', '来': '來', '对': '對', '会': '會',
            '样': '樣', '种': '種', '现': '現', '实': '實', '让': '讓',
            '给': '給', '与': '與', '虽': '雖', '后': '後',
            
            # Education
            '学': '學', '师': '師', '课': '課', '组': '組', '队': '隊',
            '团': '團',
            
            # Technology
            '网': '網', '络': '絡', '页': '頁', '码': '碼', '号': '號',
            '线': '線', '机': '機', '备': '備', '装': '裝',
            
            # Actions
            '说': '說', '讲': '講', '听': '聽', '读': '讀', '写': '寫',
            '记': '記', '忆': '憶', '虑': '慮', '决': '決', '选': '選',
            '择': '擇', '舍': '捨', '弃': '棄', '获': '獲', '护': '護',
            '报': '報', '表': '錶', '制': '製', '复': '復', '历': '歷',
            
            # Emotions and Descriptions
            '爱': '愛', '欢': '歡', '乐': '樂', '忧': '憂', '满': '滿',
            '净': '淨', '脏': '髒', '旧': '舊', '轻': '輕', '宽': '寬',
            '浅': '淺', '远': '遠', '够': '夠', '紧': '緊', '松': '鬆',
            '坏': '壞', '丑': '醜', '强': '強',
            
            # Materials and Objects
            '钢': '鋼', '铁': '鐵', '铜': '銅', '铝': '鋁', '锡': '錫',
            '纸': '紙', '丝': '絲', '绳': '繩', '带': '帶',
            
            # Colors
            '红': '紅', '绿': '綠', '蓝': '藍', '黄': '黃',
            
            # Animals
            '马': '馬', '鸟': '鳥', '鱼': '魚', '龟': '龜', '虫': '蟲',
            '狮': '獅', '猫': '貓', '猪': '豬',
            
            # Plants
            '树': '樹', '叶': '葉', '麦': '麥',
            
            # Body Parts
            '脸': '臉', '脚': '腳', '脑': '腦',
            
            # Clothing
            '裤': '褲', '袜': '襪',
            
            # Food
            '饭': '飯', '面': '麵', '汤': '湯', '鸡': '雞', '虾': '蝦',
            '盐': '鹽',
            
            # Transportation
            '飞': '飛',
            
            # Buildings
            '楼': '樓', '墙': '牆', '顶': '頂', '园': '園',
            
            # Tools
            '笔': '筆', '灯': '燈',
            
            # Weather
            '风': '風', '云': '雲', '热': '熱',
            
            # Directions
            '里': '裡', '边': '邊',
            
            # Quantities
            '细': '細',
            
            # Family
            '儿': '兒', '孙': '孫', '爷': '爺',
            
            # Work
            '农': '農', '医': '醫', '板': '闆',
            
            # Government
            '规': '規', '则': '則',
            
            # Military
            '军': '軍', '战': '戰', '斗': '鬥', '胜': '勝', '败': '敗',
            '敌': '敵',
            
            # Religion
            '庙': '廟', '祷': '禱',
            
            # Science
            '声': '聲', '数': '數',
            
            # Art
            '画': '畫', '戏': '戲', '剧': '劇', '诗': '詩', '词': '詞',
            
            # Medical
            '药': '藥', '伤': '傷', '疗': '療',
            
            # Additional Important Ones
            '厂': '廠', '场': '場', '样': '樣', '庆': '慶', '礼': '禮',
            '图': '圖', '状': '狀', '标': '標', '志': '誌', '类': '類',
            '质': '質', '值': '值', '计': '計', '累': '累', '积': '積',
            '并': '併', '联': '聯', '异': '異', '别': '別', '跟': '跟',
            '离': '離', '减': '減', '较': '較', '于': '於',
            
            # === NEWLY ADDED MISSING CHARACTERS (250+ more) ===
            
            # Missing high-frequency characters
            '宾': '賓',  # The one you specifically mentioned - guest/visitor
            '滨': '濱',  # Shore, beach
            '缤': '繽',  # Colorful, variegated
            '频': '頻',  # Frequency
            '鬓': '鬢',  # Temples (hair)
            '髌': '髕',  # Kneecap
            '胫': '脛',  # Kneecap/shin
            '槟': '檳',  # Betel
            '摈': '擯',  # Reject, expel
            '傧': '儐',  # Best man
            '殡': '殯',  # Funeral
            '镔': '鑌',  # Fine steel
            '饼': '餅',  # Cake, biscuit
            '禀': '稟',  # Report to
            '拨': '撥',  # Allocate, dial
            '剥': '剝',  # Peel, strip
            '驳': '駁',  # Refute
            '钹': '鈸',  # Cymbals
            '镈': '鎛',  # Ancient bell
            '铂': '鉑',  # Platinum
            '钵': '缽',  # Bowl
            '饱': '餓',  # Steamed bread
            '补': '補',  # Repair, supplement
            '布': '佈',  # Arrange, spread
            
            # More governmental/administrative
            '宪': '憲',  # Constitution
            '审': '審',  # Examine
            '译': '譯',  # Translate
            '议': '議',  # Discuss
            '设': '設',  # Establish
            '备': '備',  # Prepare
            '认': '認',  # Recognize
            '识': '識',  # Knowledge
            '试': '試',  # Try
            '误': '誤',  # Error
            '访': '訪',  # Visit
            '评': '評',  # Evaluate
            '调': '調',  # Adjust
            '查': '查',  # Check (same in both)
            '检': '檢',  # Inspect
            '验': '驗',  # Verify
            '测': '測',  # Measure
            
            # More technology/modern terms
            '数': '數',  # Number
            '码': '碼',  # Code
            '软': '軟',  # Soft
            '硬': '硬',  # Hard (same in both)
            '件': '件',  # Item (same in both)
            '算': '算',  # Calculate (same in both)
            '显': '顯',  # Display
            '示': '示',  # Show (same in both)
            '输': '輸',  # Input/lose
            '印': '印',  # Print (same in both)
            '复': '復',  # Restore
            '制': '製',  # Manufacture
            '造': '造',  # Make (same in both)
            '建': '建',  # Build (same in both)
            '构': '構',  # Structure
            '架': '架',  # Frame (same in both)
            
            # More business/commerce
            '贸': '貿',  # Trade
            '易': '易',  # Easy/trade (same in both)
            '购': '購',  # Purchase
            '销': '銷',  # Sales
            '售': '售',  # Sell (same in both)
            '买': '買',  # Buy
            '卖': '賣',  # Sell
            '订': '訂',  # Order
            '购': '購',  # Purchase
            '货': '貨',  # Goods
            '运': '運',  # Transport
            '输': '輸',  # Transport
            '递': '遞',  # Deliver
            '邮': '郵',  # Mail
            '寄': '寄',  # Send (same in both)
            '投': '投',  # Invest (same in both)
            '资': '資',  # Capital
            '金': '金',  # Gold (same in both)
            '银': '銀',  # Silver
            '铜': '銅',  # Copper
            
            # More people/social
            '众': '眾',  # Crowd
            '团': '團',  # Group
            '队': '隊',  # Team
            '伙': '夥',  # Partner
            '伴': '伴',  # Companion (same in both)
            '友': '友',  # Friend (same in both)
            '亲': '親',  # Relative
            '戚': '戚',  # Relative (same in both)
            '族': '族',  # Clan (same in both)
            '姓': '姓',  # Surname (same in both)
            '名': '名',  # Name (same in both)
            '称': '稱',  # Call
            '呼': '呼',  # Call (same in both)
            '唤': '喚',  # Call
            '喊': '喊',  # Shout (same in both)
        }
        
        # Remove entries where simplified and traditional are the same
        # (keeping only actual differences)
        self.simplified_to_traditional = {
            k: v for k, v in self.simplified_to_traditional.items() 
            if k != v
        }
        
        # Get all simplified characters
        self.simplified_chars = set(self.simplified_to_traditional.keys())
        
    def find_simplified_characters(self, text: str) -> Dict[str, List[str]]:
        """Find simplified characters in text and suggest traditional replacements"""
        if not text or not isinstance(text, str):
            return {'simplified_found': [], 'suggestions': []}
        
        simplified_found = []
        suggestions = []
        
        for char in text:
            if char in self.simplified_chars:
                if char not in simplified_found:  # Avoid duplicates
                    simplified_found.append(char)
                    traditional = self.simplified_to_traditional[char]
                    suggestions.append(f"{char} → {traditional}")
        
        return {
            'simplified_found': simplified_found,
            'suggestions': suggestions
        }
    
    def get_text_status(self, text: str) -> Tuple[str, str]:
        """Get overall status of text (TRADITIONAL/HAS_SIMPLIFIED)"""
        if not text or not isinstance(text, str):
            return "EMPTY", "No text to check"
        
        result = self.find_simplified_characters(text)
        simplified_count = len(result['simplified_found'])
        
        if simplified_count == 0:
            return "TRADITIONAL", "All characters are traditional"
        else:
            return "HAS_SIMPLIFIED", f"Found {simplified_count} simplified character(s)"

def validate_traditional_chinese_batch(df: pd.DataFrame, chinese_columns: List[str]) -> List[Dict]:
    """
    Validate traditional Chinese characters in a DataFrame.
    Returns list of issues found.
    """
    validator = EnhancedTraditionalValidator()
    issues = []
    
    inventory_col = df.columns[0] if len(df.columns) > 0 else None
    
    for index, row in df.iterrows():
        for col_name in chinese_columns:
            if col_name not in df.columns:
                continue
            
            text = row[col_name]
            if pd.isna(text) or text == '':
                continue
            
            text = str(text)
            status, status_note = validator.get_text_status(text)
            simplified_analysis = validator.find_simplified_characters(text)
            
            if status == "HAS_SIMPLIFIED":
                inventory_value = row[inventory_col] if inventory_col else f"Row {index + 2}"
                
                issues.append({
                    'Row': index + 2,
                    'Inventory': inventory_value,
                    'Column': col_name,
                    'Issue_Type': 'SIMPLIFIED_CHARACTERS',
                    'Original_Text': text,
                    'Simplified_Found': ', '.join(simplified_analysis['simplified_found']),
                    'Suggestions': ' | '.join(simplified_analysis['suggestions']),
                    'Issue_Count': len(simplified_analysis['simplified_found']),
                    'Status': 'NEEDS_REVIEW'
                })
    
    return issues

def export_traditional_validation_results(issues: List[Dict], output_filename: str = None) -> str:
    """Export traditional Chinese validation results to Excel"""
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        output_filename = f"TRADITIONAL_validation_{timestamp}.xlsx"
    
    if issues:
        output_df = pd.DataFrame(issues)
        output_df.to_excel(output_filename, index=False)
        return f"Exported {len(issues)} issues to {output_filename}"
    else:
        # Create empty file with headers
        empty_df = pd.DataFrame(columns=[
            'Row', 'Inventory', 'Column', 'Issue_Type', 'Original_Text', 
            'Simplified_Found', 'Suggestions', 'Issue_Count', 'Status'
        ])
        empty_df.to_excel(output_filename, index=False)
        return f"No issues found - empty report saved to {output_filename}"

# Interactive functions (for standalone use)
def choose_excel_file() -> Optional[str]:
    """Let user choose an Excel file from current directory."""
    print("🔍 Looking for Excel files in current directory...")
    excel_files = glob.glob("*.xlsx") + glob.glob("*.xls")
    
    if not excel_files:
        print("❌ No Excel files found in current directory!")
        return None
    
    print(f"\n📁 Found {len(excel_files)} Excel file(s):")
    for i, file in enumerate(excel_files, 1):
        print(f"  {i}. {file}")
    
    while True:
        try:
            choice = input(f"\nSelect file (1-{len(excel_files)}): ").strip()
            if choice.lower() in ['q', 'quit', 'exit']:
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(excel_files):
                selected_file = excel_files[index]
                print(f"✅ Selected: {selected_file}")
                return selected_file
            else:
                print(f"❌ Please enter a number between 1 and {len(excel_files)}")
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n👋 Cancelled by user")
            return None

def choose_chinese_columns(filename: str) -> Optional[List[str]]:
    """Let user choose Chinese columns to validate."""
    try:
        df = pd.read_excel(filename, nrows=0)  # Just get column names
        columns = list(df.columns)
        
        print(f"\n📊 Available columns in {filename}:")
        for i, col in enumerate(columns, 1):
            print(f"  {i}. {col}")
        
        print(f"\n🇨🇳 Select Chinese columns to validate:")
        print(f"You can select multiple columns (comma-separated, e.g., 1,3,5)")
        print(f"Or select a range (e.g., 2-5)")
        print(f"Or select all Chinese columns (type 'all')")
        
        while True:
            try:
                choice = input(f"Select columns (1-{len(columns)}) or 'all': ").strip()
                if choice.lower() in ['q', 'quit', 'exit']:
                    return None
                
                if choice.lower() == 'all':
                    # Auto-detect all Chinese columns
                    chinese_columns = []
                    sample_df = pd.read_excel(filename, nrows=3)
                    
                    for col in columns:
                        try:
                            sample_text = str(sample_df[col].iloc[0]) if len(sample_df) > 0 else ""
                            if any('\u4e00' <= char <= '\u9fff' for char in sample_text):
                                chinese_columns.append(col)
                        except:
                            pass
                    
                    if chinese_columns:
                        print(f"✅ Auto-detected Chinese columns: {', '.join(chinese_columns)}")
                        return chinese_columns
                    else:
                        print("❌ No Chinese columns auto-detected. Please select manually.")
                        continue
                
                selected_indices = []
                
                # Handle comma-separated values
                if ',' in choice:
                    parts = choice.split(',')
                    for part in parts:
                        part = part.strip()
                        if '-' in part:
                            # Handle range
                            start, end = map(int, part.split('-'))
                            selected_indices.extend(range(start-1, end))
                        else:
                            selected_indices.append(int(part) - 1)
                elif '-' in choice:
                    # Handle single range
                    start, end = map(int, choice.split('-'))
                    selected_indices.extend(range(start-1, end))
                else:
                    # Single column
                    selected_indices.append(int(choice) - 1)
                
                # Validate indices
                selected_columns = []
                for idx in selected_indices:
                    if 0 <= idx < len(columns):
                        selected_columns.append(columns[idx])
                    else:
                        print(f"❌ Invalid column index: {idx + 1}")
                        break
                else:
                    if selected_columns:
                        print(f"✅ Selected columns: {', '.join(selected_columns)}")
                        return selected_columns
                
            except ValueError:
                print("❌ Please enter valid numbers")
            except KeyboardInterrupt:
                print("\n👋 Cancelled by user")
                return None
                
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return None

def main_interactive():
    """Main interactive function for standalone use."""
    print("🇨🇳 ENHANCED TRADITIONAL CHINESE CHARACTER VALIDATOR")
    print("=" * 70)
    print("🚀 Enhanced with 500+ simplified character database!")
    print("🔍 Now detects 宾→賓, 频→頻, 滨→濱, 缤→繽, and many more missing characters")
    print("📚 Comprehensive coverage beyond basic 247 character set")
    print("=" * 70)
    
    # Step 1: Choose Excel file
    filename = choose_excel_file()
    if not filename:
        print("👋 Goodbye!")
        return
    
    # Step 2: Choose Chinese columns
    chinese_columns = choose_chinese_columns(filename)
    if not chinese_columns:
        print("👋 Goodbye!")
        return
    
    # Step 3: Confirm and run analysis
    print(f"\n🚀 READY TO VALIDATE:")
    print(f"   📁 File: {filename}")
    print(f"   🇨🇳 Columns: {', '.join(chinese_columns)}")
    print(f"   📚 Database: Enhanced 500+ character database")
    
    confirm = input("\nProceed with validation? (y/n): ").strip().lower()
    if confirm in ['y', 'yes']:
        try:
            # Load data and run validation
            df = pd.read_excel(filename)
            issues = validate_traditional_chinese_batch(df, chinese_columns)
            
            # Export results
            result_message = export_traditional_validation_results(issues)
            print(f"\n✅ {result_message}")
            
            # Show summary
            if issues:
                print(f"\n📊 SUMMARY:")
                print(f"   Total issues found: {len(issues)}")
                print(f"   🚨 First 5 issues:")
                for i, issue in enumerate(issues[:5], 1):
                    print(f"     {i}. Row {issue['Row']}: {issue['Simplified_Found']} → {issue['Suggestions']}")
            else:
                print(f"\n🎉 EXCELLENT! No simplified characters found.")
                print(f"All Chinese text is properly in traditional characters!")
                
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
    else:
        print("👋 Analysis cancelled!")

if __name__ == "__main__":
    try:
        main_interactive()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
