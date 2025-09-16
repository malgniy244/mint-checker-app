# 🏛️ Comprehensive Numismatic Validator Platform

A powerful web-based tool for validating and analyzing numismatic descriptions, translations, and text authenticity across multiple specialized domains.

## 🚀 Live Demo

**Access the app**: [https://mint-checker-app-nyp8inkygdcvtfk4932vvt.streamlit.app/](https://mint-checker-app-nyp8inkygdcvtfk4932vvt.streamlit.app/)

## 📋 Core Validation Modules

### 🪙 Mint Name Validator
- **English-to-Chinese Mint Mapping**: Validates mint name translations using comprehensive database
- **Pattern Recognition**: Identifies English mint names in mixed-language descriptions
- **Accuracy Verification**: Ensures correct Chinese mint name usage
- **Database-Driven**: Uses "cpun confirmed mint names.xlsx" for authoritative validation

### 🥉 Coin Translation Validator  
- **Bilingual Accuracy**: Validates coin descriptions in English and Chinese
- **Translation Consistency**: Checks alignment between English and Chinese coin terminology
- **Numismatic Standards**: Ensures proper coin classification and naming conventions
- **Multi-Language Support**: Handles complex mixed-language numismatic descriptions

### 💵 Banknote Translation Validator
- **Paper Money Validation**: Specialized validation for banknote descriptions
- **Translation Quality**: Ensures accuracy in banknote terminology translation
- **Historical Context**: Validates period-appropriate terminology usage
- **Multi-Currency Support**: Handles various national currency descriptions

### 🈶 Traditional Chinese Text Validator
- **Character Authenticity**: Validates traditional Chinese character usage
- **Historical Accuracy**: Ensures period-appropriate traditional Chinese forms
- **Cultural Context**: Maintains cultural and historical authenticity in Chinese text
- **Pattern Analysis**: Advanced algorithms for detecting non-authentic usage

### Advanced Platform Capabilities
- **Unified Interface**: All validators accessible through single Streamlit application
- **Batch Processing**: Handle multiple validation tasks simultaneously
- **Detailed Analytics**: Comprehensive statistics and error categorization
- **Export Functionality**: Download validation reports and corrected data
- **Password Protection**: Secure access control for authorized users

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.8+
- **Text Processing**: Custom validation algorithms
- **Deployment**: Streamlit Community Cloud
- **Version Control**: GitHub

## 📁 Project Structure

```
numismatic-validator-platform/
├── unified_validator_app.py              # Main Streamlit application
├── mint_checker_module.py                # Mint name validation (core functionality)
├── coin_validator_module.py              # Coin translation validation
├── banknote_validator_module.py          # Banknote translation validation  
├── traditional_validator_module.py       # Traditional Chinese text validation
├── cpun confirmed mint names.xlsx        # Mint name database
├── requirements.txt                      # Python dependencies
└── README.md                            # This file
```

## 🔧 Installation & Setup

### Option 1: Use the Live App (Recommended)
Simply visit: [https://mint-checker-app-nyp8inkygdcvtfk4932vvt.streamlit.app/](https://mint-checker-app-nyp8inkygdcvtfk4932vvt.streamlit.app/)

### Option 2: Run Locally

1. **Clone the repository**:
   ```bash
   git clone https://github.com/malgniy244/mint-checker-app.git
   cd mint-checker-app
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**:
   ```bash
   streamlit run interactive_mint_checker_final.py
   ```

4. **Open in browser**:
   Navigate to `http://localhost:8501`

## 📖 How to Use

### 🔐 Authentication
1. **Access Control**: Enter the secure password to unlock validation features
2. **Session Management**: Stay logged in throughout your validation session

### 🔍 Choose Validation Type
Select from four specialized validators:
- **Mint Checker**: Validate English mint names and their Chinese translations
- **Coin Validator**: Check coin description translations and terminology
- **Banknote Validator**: Verify banknote description accuracy and translations  
- **Traditional Chinese**: Validate traditional Chinese character authenticity

### 📥 Input Methods
- **Direct Text Input**: Type or paste descriptions directly
- **File Upload**: Upload Excel, CSV, or text files for batch processing
- **Batch Mode**: Process multiple entries simultaneously with detailed reports

### 📊 Analysis & Results
- **Real-time Validation**: Instant feedback on description accuracy
- **Detailed Reports**: Comprehensive analysis with error categorization
- **Statistics Dashboard**: Overview of validation results and trends
- **Export Options**: Download corrected data and detailed reports

## 🎯 Use Cases

### Numismatic Research & Documentation
- **Auction House Catalogs**: Validate descriptions for accuracy and consistency
- **Academic Research**: Ensure proper terminology in scholarly publications
- **Museum Collections**: Standardize and validate collection descriptions
- **Price Guides**: Maintain accuracy in numismatic reference materials

### Translation & Localization
- **Bilingual Catalogs**: Ensure accurate translations between English and Chinese
- **International Sales**: Validate descriptions for global numismatic markets
- **Educational Materials**: Create accurate teaching resources
- **Cultural Preservation**: Maintain authenticity in historical descriptions

## 🔍 Validation Modules Detail

### 🪙 Mint Checker Module
- **Database Integration**: Uses comprehensive "cpun confirmed mint names.xlsx"
- **Pattern Recognition**: Identifies English mint names in complex descriptions
- **Smart Extraction**: Only validates mint names appearing after year information
- **Uncertainty Handling**: Excludes descriptions with uncertainty keywords
- **Exact Matching**: Provides authoritative Chinese translations

### 🥉 Coin Validator Module  
- **Terminology Validation**: Ensures consistent coin classification terms
- **Bilingual Accuracy**: Checks English-Chinese translation alignment
- **Numismatic Standards**: Maintains industry-standard terminology
- **Historical Context**: Validates period-appropriate descriptions
- **Batch Processing**: Handles multiple coin descriptions efficiently

### 💵 Banknote Validator Module
- **Paper Money Expertise**: Specialized knowledge of banknote terminology
- **Multi-Currency Support**: Handles various national currency systems  
- **Translation Consistency**: Ensures accurate bilingual descriptions
- **Historical Accuracy**: Validates period-appropriate terminology usage
- **Quality Assurance**: Comprehensive error detection and reporting

### 🈶 Traditional Chinese Validator
- **Character Authenticity**: Validates genuine traditional character usage
- **Cultural Accuracy**: Maintains historical and cultural context
- **Pattern Analysis**: Advanced algorithms for detecting inconsistencies
- **Comprehensive Coverage**: Handles various traditional Chinese text types
- **Educational Value**: Provides learning insights for character usage

## 🚀 Recent Updates

- **Multi-Module Architecture**: Integrated 4 specialized validation systems
- **Enhanced Security**: Password protection for authorized access
- **Improved Mint Detection**: Advanced algorithms for mint name recognition
- **Batch Processing**: Simultaneous validation of multiple descriptions
- **Export Functionality**: Enhanced reporting and data export capabilities
- **Database Integration**: Direct Excel database connectivity for mint names
- **Error Categorization**: Comprehensive classification of validation issues
- **Performance Optimization**: Faster processing for large datasets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`  
5. Submit a Pull Request

## 📝 License

This project is open source. Feel free to use, modify, and distribute according to your needs.

## 🐛 Issues & Support

If you encounter any issues or have suggestions:
1. Check the [live app](https://mint-checker-app-nyp8inkygdcvtfk4932vvt.streamlit.app/) first
2. Create an issue in this GitHub repository
3. Provide detailed description of the problem and steps to reproduce

## 📊 Project Status

- **Status**: Active Development ✅
- **Last Updated**: September 2025
- **Version**: 2.0
- **Stability**: Production Ready

## 🌟 Acknowledgments

Built specifically for the numismatic community to ensure accuracy and consistency in coin and banknote documentation across languages and cultural contexts. This platform bridges the gap between English and Chinese numismatic terminology while maintaining the highest standards of historical and cultural authenticity.

---

**Made with ❤️ for Numismatic Researchers Worldwide**
