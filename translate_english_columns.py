#!/usr/bin/env python3
"""
Script to fill empty English columns by translating from Indonesian columns using Google Translate.
"""

import pandas as pd
import time
import logging
from googletrans import Translator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_stopwords_dataset():
    """Load the multilingual stopwords dataset"""
    try:
        df = pd.read_csv('multilingual_stopwords_final.csv')
        logging.info(f"Loaded dataset with {len(df)} entries")
        return df
    except FileNotFoundError:
        logging.error("multilingual_stopwords_final.csv not found!")
        return None

def analyze_missing_english(df):
    """Analyze which entries are missing English translations"""
    
    # Count missing English entries
    missing_en = df['en'].isna() | (df['en'] == '')
    total_missing = missing_en.sum()
    
    # Count entries that have Indonesian but no English
    has_indonesian = (df['id'].notna() & (df['id'] != '')) | (df['formal_id'].notna() & (df['formal_id'] != ''))
    missing_en_with_id = missing_en & has_indonesian
    translatable_count = missing_en_with_id.sum()
    
    logging.info(f"Total entries missing English: {total_missing}")
    logging.info(f"Entries with Indonesian that can be translated: {translatable_count}")
    
    return missing_en_with_id

def translate_batch(texts, translator, source_lang='id', target_lang='en', batch_size=50):
    """Translate a batch of texts with rate limiting"""
    
    translations = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_translations = []
        
        for text in batch:
            try:
                if text and str(text).strip() and str(text).strip().lower() != 'nan':
                    # Translate the text
                    result = translator.translate(str(text).strip(), src=source_lang, dest=target_lang)
                    translation = result.text.lower().strip()
                    batch_translations.append(translation)
                    
                    # Small delay to avoid rate limiting
                    time.sleep(0.1)
                else:
                    batch_translations.append('')
                    
            except Exception as e:
                logging.warning(f"Translation failed for '{text}': {e}")
                batch_translations.append('')
                time.sleep(0.5)  # Longer delay on error
        
        translations.extend(batch_translations)
        
        # Progress update
        logging.info(f"Translated batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
        
        # Longer delay between batches
        if i + batch_size < len(texts):
            time.sleep(1)
    
    return translations

def fill_english_translations(df, limit=None):
    """Fill missing English translations"""

    # Initialize translator
    translator = Translator()

    # Find entries that need translation
    missing_en_mask = analyze_missing_english(df)
    entries_to_translate = df[missing_en_mask].copy()

    # Apply limit if specified
    if limit and len(entries_to_translate) > limit:
        entries_to_translate = entries_to_translate.head(limit)
        logging.info(f"Limited translation to first {limit} entries")

    if len(entries_to_translate) == 0:
        logging.info("No entries need translation")
        return df

    logging.info(f"Starting translation of {len(entries_to_translate)} entries...")

    # Prepare texts for translation
    texts_to_translate = []
    for _, row in entries_to_translate.iterrows():
        # Prefer formal_id over id for translation
        if pd.notna(row['formal_id']) and str(row['formal_id']).strip():
            text = str(row['formal_id']).strip()
        elif pd.notna(row['id']) and str(row['id']).strip():
            text = str(row['id']).strip()
        else:
            text = ''
        texts_to_translate.append(text)

    # Translate in batches
    try:
        translations = translate_batch(texts_to_translate, translator, batch_size=20)

        # Update the dataframe
        df_updated = df.copy()
        translation_idx = 0

        for idx in entries_to_translate.index:
            if translation_idx < len(translations) and translations[translation_idx]:
                df_updated.at[idx, 'en'] = translations[translation_idx]
            translation_idx += 1

        # Count successful translations
        successful_translations = sum(1 for t in translations if t and t.strip())
        logging.info(f"Successfully translated {successful_translations} entries")

        return df_updated

    except Exception as e:
        logging.error(f"Translation process failed: {e}")
        return df

def clean_translations(df):
    """Clean and validate translations"""
    
    # Remove very long translations (likely errors)
    long_translations = df['en'].str.len() > 50
    if long_translations.any():
        logging.info(f"Removing {long_translations.sum()} overly long translations")
        df.loc[long_translations, 'en'] = ''
    
    # Remove translations that are identical to source (translation failed)
    for idx, row in df.iterrows():
        if pd.notna(row['en']) and pd.notna(row['id']):
            if str(row['en']).strip().lower() == str(row['id']).strip().lower():
                df.at[idx, 'en'] = ''
    
    # Convert to lowercase for consistency
    df['en'] = df['en'].str.lower().str.strip()
    
    return df

def create_translation_summary(original_df, translated_df):
    """Create summary of translation process"""
    
    # Count translations
    original_en_count = (original_df['en'].notna() & (original_df['en'] != '')).sum()
    final_en_count = (translated_df['en'].notna() & (translated_df['en'] != '')).sum()
    new_translations = final_en_count - original_en_count
    
    summary = f"""
ENGLISH TRANSLATION SUMMARY
===========================

Translation Results:
- Original English entries: {original_en_count}
- Final English entries: {final_en_count}
- New translations added: {new_translations}
- Translation success rate: {(new_translations / (len(original_df) - original_en_count) * 100):.1f}%

Dataset Completeness:
- Total entries: {len(translated_df)}
- English coverage: {(final_en_count / len(translated_df) * 100):.1f}%
- Indonesian coverage: {((translated_df['id'].notna() & (translated_df['id'] != '')).sum() / len(translated_df) * 100):.1f}%
- Formal Indonesian coverage: {((translated_df['formal_id'].notna() & (translated_df['formal_id'] != '')).sum() / len(translated_df) * 100):.1f}%

Sample New Translations:
"""
    
    # Show sample translations
    new_translations_mask = (original_df['en'].isna() | (original_df['en'] == '')) & (translated_df['en'].notna() & (translated_df['en'] != ''))
    sample_translations = translated_df[new_translations_mask].head(20)
    
    for i, (_, row) in enumerate(sample_translations.iterrows(), 1):
        indonesian = row['formal_id'] if pd.notna(row['formal_id']) and row['formal_id'] else row['id']
        english = row['en']
        summary += f"  {i:2d}. {indonesian} -> {english}\n"
    
    summary += f"""
Quality Notes:
✅ Translations cleaned and validated
✅ Overly long translations removed
✅ Failed translations filtered out
✅ Consistent lowercase formatting applied

Usage Impact:
- Enhanced multilingual stopword matching
- Better cross-language text processing
- Improved English-Indonesian NLP applications
- More complete dataset for research use
"""
    
    return summary

def main():
    """Main function"""
    # Load dataset
    df = load_stopwords_dataset()
    if df is None:
        return

    # Keep original for comparison
    original_df = df.copy()

    # For testing, let's start with first 100 entries that need translation
    missing_en_mask = analyze_missing_english(df)

    print(f"Testing translation with first 100 entries...")
    print(f"Total entries needing translation: {missing_en_mask.sum()}")

    # Fill English translations for test entries only (limit to 100)
    logging.info("Starting translation process...")
    translated_df = fill_english_translations(df, limit=100)

    # Clean translations
    logging.info("Cleaning translations...")
    translated_df = clean_translations(translated_df)

    # Save updated dataset
    translated_df.to_csv('multilingual_stopwords_translated_test.csv', index=False)
    logging.info("Saved translated dataset as multilingual_stopwords_translated_test.csv")

    # Create and save summary
    summary = create_translation_summary(original_df, translated_df)

    with open('translation_summary_test.txt', 'w', encoding='utf-8') as f:
        f.write(summary)

    # Print summary
    print(summary)

    print(f"\n✅ Test translation complete!")
    print(f"📊 Dataset saved as: multilingual_stopwords_translated_test.csv")
    print(f"📋 Summary saved as: translation_summary_test.txt")
    print(f"\nTo translate all entries, modify the script to remove the .head(100) limit")

if __name__ == "__main__":
    main()
