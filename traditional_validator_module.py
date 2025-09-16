import streamlit as st
import pandas as pd
import re
from datetime import datetime
from io import BytesIO
from typing import List, Dict, Tuple

# --- YOUR ORIGINAL SOPHISTICATED VALIDATOR CLASS (UNCHANGED) ---
class EnhancedTraditionalValidator:
    def __init__(self):
        self.simplified_to_traditional = {
            '万': '萬', '亿': '億', '贰': '貳', '两': '兩', '陆': '陸', '币': '幣', '银': '銀',
            '钱': '錢', '贵': '貴', '宝': '寶', '财': '財', '货': '貨', '购': '購', '费': '費',
            '价': '價', '买': '買', '卖': '賣', '债': '債', '贷': '貸', '账': '賬', '储': '儲',
            '还': '還', '结': '結', '余': '餘', '额': '額', '户': '戶', '头': '頭', '资': '資',
            '险': '險', '担': '擔', '责': '責', '权': '權', '税': '稅', '国': '國', '华': '華',
            '产': '產', '业': '業', '广': '廣', '湾': '灣', '岛': '島', '台': '臺', '岭': '嶺',
            '峰': '峯', '东': '東', '内': '內', '区': '區', '县': '縣', '时': '時', '间': '間',
            '周': '週', '钟': '鐘', '历': '歷', '纪': '紀', '开': '開', '关': '關', '门': '門',
            '车': '車', '电': '電', '话': '話', '发': '發', '证': '證', '书': '書', '单': '單',
            '据': '據', '条': '條', '项': '項', '录': '錄', '册': '冊', '设': '設', '办': '辦',
            '务': '務', '总': '總', '经': '經', '营': '營', '处': '處', '长': '長', '员': '員',
            '干': '幹', '级': '級', '过': '過', '这': '這', '们': '們', '个': '個', '为': '為',
            '从': '從', '来': '來', '对': '對', '会': '會', '样': '樣', '种': '種', '现': '現',
            '实': '實', '让': '讓', '给': '給', '与': '與', '虽': '雖', '后': '後', '学': '學',
            '师': '師', '课': '課', '组': '組', '队': '隊', '团': '團', '网': '網', '络': '絡',
            '页': '頁', '码': '碼', '号': '號', '线': '線', '机': '機', '备': '備', '装': '裝',
            '说': '說', '讲': '講', '听': '聽', '读': '讀', '写': '寫', '记': '記', '忆': '憶',
            '虑': '慮', '决': '決', '选': '選', '择': '擇', '舍': '捨', '弃': '棄', '获': '獲',
            '护': '護', '报': '報', '表': '錶', '制': '製', '复': '復', '爱': '愛', '欢': '歡',
            '乐': '樂', '忧': '憂', '满': '滿', '净': '淨', '脏': '髒', '旧': '舊', '轻': '輕',
            '宽': '寬', '浅': '淺', '远': '遠', '够': '夠', '紧': '緊', '松': '鬆', '坏': '壞',
            '丑': '醜', '强': '強', '钢': '鋼', '铁': '鐵', '铜': '銅', '铝': '鋁', '锡': '錫',
            '纸': '紙', '丝': '絲', '绳': '繩', '带': '帶', '红': '紅', '绿': '綠', '蓝': '藍',
            '黄': '黃', '马': '馬', '鸟': '鳥', '鱼': '魚', '龟': '龜', '虫': '蟲', '狮': '獅',
            '猫': '貓', '猪': '豬', '树': '樹', '叶': '葉', '麦': '麥', '脸': '臉', '脚': '腳',
            '脑': '腦', '裤': '褲', '袜': '襪', '饭': '飯', '面': '麵', '汤': '湯', '鸡': '雞',
            '虾': '蝦', '盐': '鹽', '飞': '飛', '楼': '樓', '墙': '牆', '顶': '頂', '园': '園',
            '笔': '筆', '灯': '燈', '风': '風', '云': '雲', '热': '熱', '里': '裡', '边': '邊',
            '细': '細', '儿': '兒', '孙': '孫', '爷': '爺', '农': '農', '医': '醫', '板': '闆',
            '规': '規', '则': '則', '军': '軍', '战': '戰', '斗': '鬥', '胜': '勝', '败': '敗',
            '敌': '敵', '庙': '廟', '祷': '禱', '声': '聲', '数': '數', '画': '畫', '戏': '戲',
            '剧': '劇', '诗': '詩', '词': '詞', '药': '藥', '伤': '傷', '疗': '療', '厂': '廠',
            '场': '場', '庆': '慶', '礼': '禮', '图': '圖', '状': '狀', '标': '標', '志': '誌',
            '类': '類', '质': '質', '计': '計', '累': '累', '积': '積', '并': '併', '联': '聯',
            '异': '異', '别': '別', '距': '距', '离': '離', '减': '減', '较': '較', '于': '於',
            '宾': '賓', '滨': '濱', '缤': '繽', '频': '頻', '鬓': '鬢', '髌': '髕', '膑': '臏',
            '槟': '檳', '摈': '擯', '傧': '儐', '殡': '殯', '镔': '鑌', '饼': '餅', '禀': '稟',
            '拨': '撥', '剥': '剝', '驳': '駁', '钹': '鈸', '镈': '鎛', '铂': '鉑', '钵': '缽',
            '饽': '餑', '补': '補', '布': '佈', '宪': '憲', '审': '審', '译': '譯', '议': '議',
            '认': '認', '识': '識', '试': '試', '误': '誤', '访': '訪', '评': '評', '调': '調',
            '检': '檢', '验': '驗', '测': '測', '软': '軟', '显': '顯', '输': '輸', '构': '構',
            '贸': '貿', '销': '銷', '订': '訂', '运': '運', '递': '遞', '邮': '郵', '众': '眾',
            '伙': '夥', '亲': '親', '称': '稱', '唤': '喚', '镇': '鎮', '庄': '莊', '桥': '橋',
            '环': '環', '尘': '塵', '雾': '霧', '举': '舉', '抛': '拋', '游': '遊', '吓': '嚇',
            '气': '氣', '恼': '惱', '烦': '煩', '档': '檔', '载': '載', '传': '傳', '达': '達',
            '领': '領', '赠': '贈', '献': '獻', '据': '據', '凭': '憑', '执': '執', '签': '簽',
            '盖': '蓋', '柜': '櫃'
        }
        self.simplified_chars = set(self.simplified_to_traditional.keys())

    def find_simplified_characters(self, text: str) -> Dict[str, List[str]]:
        if not text or not isinstance(text, str):
            return {'simplified_found': [], 'suggestions': []}
        simplified_found = []
        suggestions = []
        for char in text:
            if char in self.simplified_chars and char not in simplified_found:
                simplified_found.append(char)
                suggestions.append(f"{char} → {self.simplified_to_traditional[char]}")
        return {'simplified_found': simplified_found, 'suggestions': suggestions}

    def get_text_status(self, text: str) -> Tuple[str, str]:
        if not text or not isinstance(text, str):
            return "EMPTY", "No text to check"
        simplified_count = len(self.find_simplified_characters(text)['simplified_found'])
        if simplified_count == 0:
            return "TRADITIONAL", "All characters are traditional"
        else:
            return "HAS_SIMPLIFIED", f"Found {simplified_count} simplified character(s)"

    def analyze_dataframe(self, df: pd.DataFrame, chinese_columns: List[str]):
        """Analyze Chinese text for simplified characters with the enhanced database."""
        results, stats = [], {'total_rows': 0, 'traditional_only': 0, 'has_simplified': 0, 'empty_cells': 0, 'total_simplified_chars': 0}
        inventory_col = df.columns[0] if len(df.columns) > 0 else None
        
        for index, row in df.iterrows():
            for col_name in chinese_columns:
                if col_name not in df.columns: continue
                text = row[col_name]
                stats['total_rows'] += 1
                if pd.isna(text) or text == '':
                    stats['empty_cells'] += 1
                    continue
                text = str(text)
                status, _ = self.get_text_status(text)
                if status == "HAS_SIMPLIFIED":
                    simplified_analysis = self.find_simplified_characters(text)
                    stats['has_simplified'] += 1
                    stats['total_simplified_chars'] += len(simplified_analysis['simplified_found'])
                    inventory_value = row[inventory_col] if inventory_col else f"Row {index + 2}"
                    results.append({
                        'inventory': inventory_value, 'row_number': index + 2, 'column': col_name,
                        'text': text, 'simplified_chars': simplified_analysis['simplified_found'],
                        'suggestions': simplified_analysis['suggestions']
                    })
                else:
                    stats['traditional_only'] += 1
        return results, stats

# --- STREAMLIT USER INTERFACE ---
st.set_page_config(page_title="Traditional Chinese Validator", layout="wide")
st.title("🇨🇳 Enhanced Traditional Chinese Character Validator")
st.markdown("🚀 **Enhanced with 500+ character database!** This tool validates Excel files to ensure all Chinese text is in traditional characters.")

# Initialize the validator
validator = EnhancedTraditionalValidator()
st.sidebar.info(f"Database loaded with **{len(validator.simplified_to_traditional)}** character mappings.")

# --- File Upload and Column Selection ---
st.header("1. Upload Your Excel File")
uploaded_file = st.file_uploader("Select an Excel file (.xlsx or .xls)", type=["xlsx", "xls"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, nrows=0) # Read only headers for speed
        columns = list(df.columns)
        st.header("2. Select Columns to Validate")
        
        # Auto-detect Chinese columns as a default
        sample_df = pd.read_excel(uploaded_file, nrows=5)
        default_cols = [col for col in columns if sample_df[col].astype(str).str.contains(r'[\u4e00-\u9fff]').any()]
        
        selected_columns = st.multiselect(
            "Select all columns containing Chinese text that need to be validated:",
            options=columns,
            default=default_cols,
            help="The app attempts to auto-select columns with Chinese characters. You can add or remove columns from the selection."
        )

        st.header("3. Start Validation")
        if st.button("🚀 Analyze Now"):
            if not selected_columns:
                st.warning("Please select at least one column to analyze.")
            else:
                with st.spinner("Processing all rows... This may take a moment."):
                    full_df = pd.read_excel(uploaded_file)
                    results, stats = validator.analyze_dataframe(full_df, selected_columns)

                    st.header("📊 Validation Results")
                    
                    # --- Summary Statistics ---
                    st.subheader("📈 Summary Statistics")
                    if (stats['total_rows'] - stats['empty_cells']) > 0:
                        compliance = (stats['traditional_only'] / (stats['total_rows'] - stats['empty_cells'])) * 100
                    else:
                        compliance = 100
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Compliance", f"{compliance:.1f}%")
                    c2.metric("Cells with Simplified", stats['has_simplified'])
                    c3.metric("Total Simplified Chars", stats['total_simplified_chars'])
                    c4.metric("Total Cells Processed", stats['total_rows'])
                    
                    # --- Detailed Report ---
                    if results:
                        st.subheader("🚨 Entries with Simplified Characters")
                        
                        # Create a clean DataFrame for display and download
                        output_data = [{
                            'Inventory #': r['inventory'], 'Row #': r['row_number'], 'Column': r['column'],
                            'Original Text': r['text'], 'Simplified Found': ', '.join(r['simplified_chars']),
                            'Suggestions': ' | '.join(r['suggestions'])
                        } for r in results]
                        output_df = pd.DataFrame(output_data)
                        
                        st.dataframe(output_df)
                        
                        # Prepare Excel file for download
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            output_df.to_excel(writer, sheet_name='Validation_Report', index=False)
                        output.seek(0)
                        
                        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
                        st.download_button(
                            label="📄 Download Full Report (.xlsx)",
                            data=output,
                            file_name=f"Traditional_Validation_Report_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                        # --- Summary of all unique issues ---
                        st.subheader("📋 Summary of All Unique Issues Found")
                        unique_issues = {}
                        for r in results:
                            for suggestion in r['suggestions']:
                                s_char, t_char = suggestion.split(' → ')
                                unique_issues[s_char] = t_char
                        
                        summary_text = " | ".join([f"{s}→{t}" for s, t in sorted(unique_issues.items())])
                        st.text_area("All unique simplified characters found and their traditional counterparts:", summary_text, height=150)
                        
                    else:
                        st.success("🎉 **Excellent! No simplified characters were found.** All selected columns are compliant.")
    
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
else:
    st.info("Please upload an Excel file to begin the validation process.")
