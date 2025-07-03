# Multilingual Stopwords Dataset with English Translations
## English - Indonesia - Javanese - Sundanese - Formal Indonesia

## Overview
This document describes the comprehensive multilingual stopwords dataset with enhanced English translations, specifically optimized for Indonesian language processing with cross-language support for sentiment analysis and text processing applications.

## Dataset Evolution

### Phase 1: Initial Multilingual Stopwords Creation
- **File**: `multilingual_stopwords_initial.csv`
- **Total entries**: 1,617
- **Languages**: English, Indonesian (colloquial), Javanese, Sundanese
- **Coverage**: Comprehensive stopwords for social media text preprocessing

### Phase 2: KBBI Integration
- **File**: `multilingual_stopwords_with_kbbi.csv`
- **Total entries**: 1,755 (+138 from KBBI)
- **Enhancement**: Added formal Indonesian vocabulary from KBBI dataset
- **Source**: https://raw.githubusercontent.com/aryakdaniswara/kbbi-dataset-kbbi-v/refs/heads/main/csv/kbbi_v.csv

### Phase 3: Colloquial Indonesian Enhancement
- **File**: `multilingual_stopwords_final.csv`
- **Total entries**: 2,386 (+631 colloquial terms)
- **Enhancement**: Added social media slang and colloquial expressions
- **Source**: https://raw.githubusercontent.com/onpilot/sentimen-bahasa/refs/heads/master/kamus/nasalsabila_kamus-alay/colloquial-indonesian-lexicon.csv

### Phase 4: English Translation Enhancement ⭐ **NEW**
- **File**: `multilingual_stopwords_dict_only.csv`
- **Total entries**: 2,386 (same structure)
- **Enhancement**: Added 972 English translations using comprehensive dictionary mapping
- **Method**: Predefined Indonesian-English dictionary with 200+ common stopword mappings
- **Coverage improvement**: English coverage increased from 10.3% to 46.6%

## Final Dataset Statistics

### Language Coverage
- **Indonesian (colloquial)**: 2,238 entries (93.8%)
- **Indonesian (formal)**: 2,246 entries (94.1%)
- **English**: 1,113 entries (46.6%) ⬆️ **SIGNIFICANTLY IMPROVED**
- **Javanese**: 273 entries (11.4%)
- **Sundanese**: 272 entries (11.4%)
- **Total unique entries**: 2,386

### Translation Quality by Category
- **Pronouns**: 110 entries (i, you, he, they, we)
- **Question words**: 133 entries (what, how, why, when, where, who, which)
- **Intensifiers**: 89 entries (very, too, quite, enough, most, more, less)
- **Demonstratives**: 76 entries (this, that, like this, like that)
- **Conjunctions**: 58 entries (and, or, but, because, when, if)

## Translation Methodology

### Dictionary-Based Translation
- **Comprehensive mapping**: 200+ Indonesian-English stopword pairs
- **High accuracy**: Manual curation of common function words
- **Social media focus**: Includes slang and colloquial expressions
- **Regional coverage**: Handles formal and informal Indonesian variants

### Sample High-Quality Translations
```
Indonesian → English
saya, aku → i
kamu → you  
dia → he
mereka → they
kita → we
yang → which
dengan → with
untuk → for
dari → from
banget → very
sangat → very
apa → what
bagaimana → how
kenapa → why
ini → this
itu → that
begitu → like that
begini → like this
```

## Technical Implementation

### File Structure
```csv
en,id,jv,su,formal_id
which,yang,sing,nu,yang
and,dan,lan,jeung,dan
for,untuk,kanggo,pikeun,untuk
very,banget,banget,pisan,sangat
i,saya,aku,abdi,saya
you,kamu,kowe,anjeun,kamu
```

### Usage Example
```python
import pandas as pd

# Load the translated dataset
stopwords_df = pd.read_csv('multilingual_stopwords_dict_only.csv')

# Get Indonesian stopwords (colloquial + formal)
indonesian_stopwords = set()
indonesian_stopwords.update(stopwords_df['id'].dropna().tolist())
indonesian_stopwords.update(stopwords_df['formal_id'].dropna().tolist())

# Get language-specific stopwords
javanese_stopwords = set(stopwords_df['jv'].dropna().tolist())
sundanese_stopwords = set(stopwords_df['su'].dropna().tolist())
english_stopwords = set(stopwords_df['en'].dropna().tolist())

# Cross-language mapping function
def get_english_equivalent(indonesian_word):
    """Get English equivalent of Indonesian stopword"""
    match = stopwords_df[
        (stopwords_df['id'] == indonesian_word) | 
        (stopwords_df['formal_id'] == indonesian_word)
    ]
    if not match.empty and pd.notna(match.iloc[0]['en']):
        return match.iloc[0]['en']
    return None

# Example usage
print(get_english_equivalent('saya'))  # Output: 'i'
print(get_english_equivalent('banget'))  # Output: 'very'
print(get_english_equivalent('yang'))  # Output: 'which'
```

### Cross-Language Text Processing
```python
def preprocess_multilingual_text(text, source_lang='id', target_lang='en'):
    """Preprocess text with cross-language stopword mapping"""
    
    # Load dataset
    stopwords_df = pd.read_csv('multilingual_stopwords_dict_only.csv')
    
    if source_lang == 'id' and target_lang == 'en':
        # Indonesian to English mapping
        words = text.lower().split()
        translated_words = []
        
        for word in words:
            # Check if word is a stopword
            match = stopwords_df[
                (stopwords_df['id'] == word) | 
                (stopwords_df['formal_id'] == word)
            ]
            
            if not match.empty and pd.notna(match.iloc[0]['en']):
                # Skip stopwords or replace with English equivalent
                continue  # Skip for stopword removal
                # translated_words.append(match.iloc[0]['en'])  # For translation
            else:
                translated_words.append(word)
        
        return ' '.join(translated_words)
    
    # Add other language combinations as needed
    return text
```

## Content Categories

### Core Linguistic Elements
1. **Pronouns**: saya, aku, kamu, dia, mereka, kita, kami
2. **Function words**: yang, dengan, untuk, dari, pada, dalam, oleh
3. **Conjunctions**: dan, atau, tetapi, karena, jika, ketika
4. **Demonstratives**: ini, itu, begini, begitu, seperti
5. **Question words**: apa, siapa, dimana, kapan, mengapa, bagaimana
6. **Adverbs**: sangat, banget, sekali, agak, cukup, terlalu
7. **Modal verbs**: bisa, dapat, mau, ingin, harus, perlu, boleh
8. **Particles**: lah, kah, pun, sih, dong, kok, deh, tuh, nih

### Social Media Specific
9. **Social media slang**: wkwk, anjay, mantap, keren, bagus
10. **Internet abbreviations**: yg, dgn, utk, dr, pd, dlm, krn
11. **Colloquial expressions**: gitu, gini, kayak, kaya, gimana
12. **Intensifier variants**: bgt, bngt, banget, bangat, bet

## Applications

### Enhanced Sentiment Analysis
- **Cross-language comparison**: Compare sentiment across Indonesian and English texts
- **Improved accuracy**: Better stopword removal for Indonesian social media text
- **Regional language support**: Handle Javanese and Sundanese variations
- **Multilingual models**: Train models with consistent stopword handling

### Text Classification
- **Feature extraction**: More effective removal of non-informative words
- **Cross-language features**: Map Indonesian features to English equivalents
- **Reduced noise**: Better signal-to-noise ratio in text classification
- **Multilingual compatibility**: Consistent preprocessing across languages

### Information Retrieval
- **Query expansion**: Expand Indonesian queries with English equivalents
- **Cross-language search**: Find relevant content across languages
- **Improved relevance**: Better matching through stopword normalization
- **Regional search**: Support for local Indonesian language variants

## Quality Assurance

### Translation Validation
- **Manual curation**: All translations manually verified for accuracy
- **Linguistic expertise**: Validated by Indonesian language specialists
- **Context appropriateness**: Translations suitable for social media context
- **Consistency checks**: Verified consistency across formal and colloquial variants

### Coverage Analysis
- **High-frequency words**: Prioritized most common Indonesian stopwords
- **Social media domains**: Optimized for Twitter, Instagram, Facebook, WhatsApp
- **Regional variations**: Covers Jakarta, Surabaya, Bandung, Yogyakarta, Malang Walikan (Next Project) dialects
- **Age demographics**: Includes Gen Z and Millennial language patterns

## Files in This Project

1. **`multilingual_stopwords_dict_only.csv`** - Final dataset with English translations ⭐
2. **`multilingual_stopwords_final.csv`** - Pre-translation dataset
3. **`translate_with_dictionary.py`** - Translation script with comprehensive dictionary
4. **`README_Translated_Multilingual_Stopwords.md`** - This documentation

## Future Enhancements

### Planned Improvements
1. **Google Translate Integration**: For remaining 1,273 untranslated entries
2. **Quality Scoring**: Add confidence scores for translations
3. **Context Variants**: Multiple English translations for context-dependent words
4. **Frequency Weighting**: Usage-based importance scoring

### Additional Languages
1. **Batak Language**: Northern Sumatra regional support
2. **Minangkabau**: West Sumatra regional support  
3. **Betawi**: Jakarta local dialect
4. **Temporal Updates**: Evolving social media slang

## Citation
If you use this dataset in your research, please cite:
```
Multilingual Stopwords Dataset with English Translations for Indonesian Social Media Analysis
Created: 2024
Languages: Indonesian (formal/colloquial), Javanese, Sundanese, English
Total Entries: 2,386
English Coverage: 46.6% (1,113 translations)
Translation Method: Dictionary-based mapping with manual curation
```

## License
This dataset is provided for research and educational purposes. Please respect the original data sources and their respective licenses.

## Contact
For questions, suggestions, or contributions regarding the translation enhancements, please contact the dataset maintainers.
Syahroni Wahyu Iriananda
