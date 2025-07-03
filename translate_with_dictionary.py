#!/usr/bin/env python3
"""
Translate Indonesian stopwords to English using a predefined dictionary + Google Translate fallback
"""

import pandas as pd
import time
import logging
from googletrans import Translator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Predefined Indonesian to English dictionary for common stopwords
INDONESIAN_ENGLISH_DICT = {
    # Pronouns
    'saya': 'i', 'aku': 'i', 'kamu': 'you', 'anda': 'you', 'dia': 'he', 'ia': 'he',
    'mereka': 'they', 'kita': 'we', 'kami': 'we', 'kalian': 'you',
    
    # Common function words
    'yang': 'which', 'dengan': 'with', 'untuk': 'for', 'dari': 'from', 'pada': 'on',
    'dalam': 'in', 'oleh': 'by', 'ke': 'to', 'di': 'at', 'akan': 'will',
    'sudah': 'already', 'sedang': 'being', 'masih': 'still', 'belum': 'not yet',
    'tidak': 'not', 'bukan': 'not', 'jangan': 'do not', 'juga': 'also',
    'hanya': 'only', 'saja': 'just', 'pula': 'also', 'lagi': 'again',
    
    # Conjunctions
    'dan': 'and', 'atau': 'or', 'tetapi': 'but', 'karena': 'because',
    'jika': 'if', 'ketika': 'when', 'sementara': 'while', 'sebelum': 'before',
    'sesudah': 'after', 'sampai': 'until', 'sejak': 'since',
    
    # Demonstratives
    'ini': 'this', 'itu': 'that', 'begini': 'like this', 'begitu': 'like that',
    'demikian': 'thus', 'seperti': 'like', 'sama': 'same',
    
    # Question words
    'apa': 'what', 'siapa': 'who', 'dimana': 'where', 'kemana': 'where to',
    'kapan': 'when', 'mengapa': 'why', 'kenapa': 'why', 'bagaimana': 'how',
    'berapa': 'how many', 'mana': 'which',
    
    # Adverbs
    'sangat': 'very', 'banget': 'very', 'sekali': 'very', 'agak': 'quite',
    'cukup': 'enough', 'terlalu': 'too', 'lebih': 'more', 'paling': 'most',
    'kurang': 'less', 'hampir': 'almost', 'selalu': 'always', 'sering': 'often',
    'kadang': 'sometimes', 'jarang': 'rarely', 'pernah': 'ever', 'belum pernah': 'never',
    
    # Modal verbs
    'bisa': 'can', 'dapat': 'can', 'mau': 'want', 'ingin': 'want',
    'harus': 'must', 'perlu': 'need', 'boleh': 'may', 'seharusnya': 'should',
    
    # Common particles
    'lah': '', 'kah': '', 'pun': '', 'sih': '', 'dong': '', 'kok': '',
    'deh': '', 'tuh': '', 'nih': '', 'yah': '', 'ya': 'yes',
    
    # Common colloquial
    'gitu': 'like that', 'gini': 'like this', 'kayak': 'like', 'kaya': 'like',
    'gimana': 'how', 'kenapa': 'why', 'emang': 'indeed', 'memang': 'indeed',
    'udah': 'already', 'belom': 'not yet', 'lagi': 'again', 'aja': 'just',
    
    # Common abbreviations
    'yg': 'which', 'dgn': 'with', 'utk': 'for', 'dr': 'from', 'pd': 'on',
    'dlm': 'in', 'krn': 'because', 'jk': 'if', 'jgn': 'do not',
    'bgt': 'very', 'bngt': 'very', 'gk': 'not', 'ga': 'not', 'tdk': 'not',
    'tdk': 'not', 'blm': 'not yet', 'sdh': 'already', 'lg': 'again',
    'sm': 'with', 'sma': 'same', 'kl': 'if', 'klo': 'if', 'kalo': 'if',
    
    # Family terms
    'ayah': 'father', 'ibu': 'mother', 'bapak': 'father', 'mama': 'mother',
    'papa': 'father', 'kakak': 'sibling', 'adik': 'sibling', 'anak': 'child',
    
    # Time words
    'sekarang': 'now', 'nanti': 'later', 'kemarin': 'yesterday', 'besok': 'tomorrow',
    'hari': 'day', 'minggu': 'week', 'bulan': 'month', 'tahun': 'year',
    'jam': 'hour', 'menit': 'minute', 'detik': 'second',
    
    # Common expressions
    'terima kasih': 'thank you', 'maaf': 'sorry', 'permisi': 'excuse me',
    'selamat': 'congratulations', 'halo': 'hello', 'hai': 'hi',
    
    # Laughing expressions
    'haha': 'haha', 'hehe': 'hehe', 'hihi': 'hihi', 'hoho': 'hoho', 'huhu': 'huhu',
    'hahaha': 'hahaha', 'hehehe': 'hehehe', 'hahahaha': 'hahahaha',
    
    # Common internet slang
    'wkwk': 'lol', 'wkwkwk': 'lol', 'kwkw': 'lol', 'anjay': 'wow',
    'mantap': 'great', 'keren': 'cool', 'bagus': 'good', 'jelek': 'bad',
}

def translate_using_dictionary(text):
    """Translate using predefined dictionary"""
    text_lower = text.lower().strip()
    
    # Direct match
    if text_lower in INDONESIAN_ENGLISH_DICT:
        return INDONESIAN_ENGLISH_DICT[text_lower]
    
    # Check for partial matches (for compound words)
    for indo_word, eng_word in INDONESIAN_ENGLISH_DICT.items():
        if indo_word in text_lower and len(indo_word) > 2:
            return eng_word
    
    return None

def translate_with_google(text, translator, max_retries=2):
    """Fallback to Google Translate"""
    
    for attempt in range(max_retries):
        try:
            result = translator.translate(text.strip(), src='id', dest='en')
            translation = result.text.lower().strip()
            
            # Basic validation
            if len(translation) > 50 or translation == text.lower():
                return None
            
            return translation
            
        except Exception as e:
            logging.warning(f"Google Translate attempt {attempt + 1} failed for '{text}': {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
    
    return None

def fill_english_translations(df, use_google=True, max_entries=None):
    """Fill English translations using dictionary + Google Translate"""
    
    # Get entries that need translation
    missing_en = (df['en'].isna() | (df['en'] == ''))
    has_indonesian = (df['id'].notna() & (df['id'] != '')) | (df['formal_id'].notna() & (df['formal_id'] != ''))
    candidates = df[missing_en & has_indonesian].copy()
    
    if max_entries:
        candidates = candidates.head(max_entries)
    
    if len(candidates) == 0:
        print("No entries need translation")
        return df, 0, 0
    
    print(f"Processing {len(candidates)} entries for translation...")
    
    # Initialize Google Translator if needed
    translator = Translator() if use_google else None
    
    # Process translations
    df_updated = df.copy()
    dict_translations = 0
    google_translations = 0
    
    for i, (idx, row) in enumerate(candidates.iterrows()):
        # Get text to translate
        if pd.notna(row['formal_id']) and str(row['formal_id']).strip():
            text = str(row['formal_id']).strip()
        elif pd.notna(row['id']) and str(row['id']).strip():
            text = str(row['id']).strip()
        else:
            continue
        
        print(f"  {i + 1:3d}/{len(candidates)}: '{text}' -> ", end='')
        
        # Try dictionary first
        translation = translate_using_dictionary(text)
        
        if translation is not None:
            df_updated.at[idx, 'en'] = translation
            dict_translations += 1
            print(f"'{translation}' (dict)")
        elif use_google and translator:
            # Fallback to Google Translate
            translation = translate_with_google(text, translator)
            if translation:
                df_updated.at[idx, 'en'] = translation
                google_translations += 1
                print(f"'{translation}' (google)")
                time.sleep(1)  # Rate limiting
            else:
                print("FAILED")
        else:
            print("SKIPPED")
    
    total_translations = dict_translations + google_translations
    print(f"\nTranslation complete:")
    print(f"  Dictionary translations: {dict_translations}")
    print(f"  Google translations: {google_translations}")
    print(f"  Total successful: {total_translations}")
    
    return df_updated, dict_translations, google_translations

def main():
    """Main function"""
    
    # Load dataset
    try:
        df = pd.read_csv('multilingual_stopwords_final.csv')
        print(f"Loaded dataset with {len(df)} entries")
    except FileNotFoundError:
        print("multilingual_stopwords_final.csv not found!")
        return
    
    # Check how many need translation
    missing_en = (df['en'].isna() | (df['en'] == ''))
    has_indonesian = (df['id'].notna() & (df['id'] != '')) | (df['formal_id'].notna() & (df['formal_id'] != ''))
    total_needing = (missing_en & has_indonesian).sum()
    
    print(f"Total entries needing translation: {total_needing}")
    
    # Ask user for preferences
    print("\nTranslation options:")
    print("1. Dictionary only (fast, limited coverage)")
    print("2. Dictionary + Google Translate (slower, better coverage)")
    print("3. Test with first 100 entries")
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == '1':
        df_translated, dict_count, google_count = fill_english_translations(df, use_google=False)
        output_file = 'multilingual_stopwords_dict_only.csv'
    elif choice == '3':
        df_translated, dict_count, google_count = fill_english_translations(df, use_google=True, max_entries=100)
        output_file = 'multilingual_stopwords_test_100.csv'
    else:  # Default to option 2
        df_translated, dict_count, google_count = fill_english_translations(df, use_google=True)
        output_file = 'multilingual_stopwords_fully_translated.csv'
    
    # Save results
    df_translated.to_csv(output_file, index=False)
    
    # Show summary
    original_en = (df['en'].notna() & (df['en'] != '')).sum()
    final_en = (df_translated['en'].notna() & (df_translated['en'] != '')).sum()
    
    print(f"\n=== FINAL SUMMARY ===")
    print(f"Original English entries: {original_en}")
    print(f"Final English entries: {final_en}")
    print(f"New translations: {dict_count + google_count}")
    print(f"English coverage: {(final_en / len(df_translated) * 100):.1f}%")
    print(f"Saved as: {output_file}")

if __name__ == "__main__":
    main()
