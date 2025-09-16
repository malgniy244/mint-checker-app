import streamlit as st
import pandas as pd
import re
from datetime import datetime
import os
from io import BytesIO

# --- YOUR ORIGINAL SOPHISTICATED LOGIC CLASS (UNCHANGED) ---
class InteractiveMintChecker:
    def __init__(self):
        """Initialize and load official mint names database"""
        self.english_to_chinese = {}
        # The database will be loaded once a file is provided or found.

    def load_official_mint_database(self, db_source):
        """Load the official mint names from a file path or uploaded file."""
        try:
            self.official_mints = pd.read_excel(db_source)
            self.english_to_chinese = {}
            for _, row in self.official_mints.iterrows():
                english = str(row['English Mint Name']).strip()
                chinese = str(row['Chinese Mint Name']).strip()
                self.english_to_chinese[english] = chinese
            return f"✅ Loaded {len(self.english_to_chinese)} official mint names."
        except Exception as e:
            raise Exception(f"Error loading official mint database: {e}")

    def find_english_mint_in_text(self, text):
        """Find English mint name in text - ONLY between two periods"""
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
                        prev_segment = segments[i-1].strip()
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
        patterns = [r'([^。，\s]{
