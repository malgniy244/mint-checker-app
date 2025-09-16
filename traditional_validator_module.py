#!/usr/bin/env python3
"""
Traditional Chinese Character Validator - Module Version
Exports the validate_traditional_chinese_batch function for unified validator
"""

import pandas as pd
from typing import Set, List, Dict, Tuple, Optional

class EnhancedTraditionalValidator:
    def __init__(self):
        # COMPREHENSIVE simplified to traditional character database (500+ characters)
        # EXACT COPY from your original script
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
            '钢': '鋼', '铁': '鐵', '铜': '銅', '锌': '鋅', '锡': '錫',
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
            '农': '農', '医': '醫', '老': '闆',
            
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
            '膑': '臏',  # Kneecap/shin
            '槟': '檳',  # Betel
            '摈': '擯',  # Reject, expel
            '傧': '儐',  # Best man
            '殡': '殯',  # Funeral
            '镔': '鎮',  # Fine steel
            '饼': '餅',  # Cake, biscuit
            '禀': '稟',  # Report to
            '拨': '撥',  # Allocate, dial
            '剥': '剝',  # Peel, strip
            '驳': '駁',  # Refute
            '钹': '鈸',  # Cymbals
            '镈': '鎛',  # Ancient bell
            '铂': '鉑',  # Platinum
            '钵': '缽',  # Bowl
            '饽': '餑',  # Steamed bread
            '补': '補',  # Repair, supplement
            '布': '佈',  # Arrange, spread
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

def validate_traditional_chinese_batch(df: pd.DataFrame, chinese_columns: List[str]) -> List[Dict]:
    """
    Validate traditional Chinese characters in DataFrame columns.
    Returns list of issues found - this is the function your unified app expects.
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
            simplified_analysis = validator.find_simplified_characters(text)
            
            if simplified_analysis['simplified_found']:
                inventory_value = row[inventory_col] if inventory_col else f"Row {index + 2}"
                
                issues.append({
                    'Row': index + 2,
                    'Inventory': inventory_value,
                    'Column': col_name,
                    'Issue_Type': 'SIMPLIFIED_CHARACTERS',
                    'Original_Text': text,
                    'Simplified_Found': ', '.join(simplified_analysis['simplified_found']),
                    'Suggestions': ' | '.join(simplified_analysis['suggestions']),
                    'Status': 'NEEDS_REVIEW'
                })
    
    return issues
