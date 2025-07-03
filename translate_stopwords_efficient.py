#!/usr/bin/env python3
"""
Efficient script to translate Indonesian stopwords to English using Google Translate
"""

import pandas as pd
import time
import logging
from googletrans import Translator
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_dataset():
    """Load the multilingual stopwords dataset"""
    try:
        df = pd.read_csv('multilingual_stopwords_final.csv')
        logging.info(f"Loaded dataset with {len(df)} entries")
        return df
    except FileNotFoundError:
        logging.error("multilingual_stopwords_final.csv not found!")
        return None

def get_translation_candidates(df):
    """Get entries that need English translation"""
    
    # Find entries missing English
    missing_en = (df['en'].isna() | (df['en'] == ''))
    
    # Find entries that have Indonesian text
    has_indonesian = (df['id'].notna() & (df['id'] != '')) | (df['formal_id'].notna() & (df['formal_id'] != ''))
    
    # Get candidates
    candidates = df[missing_en & has_indonesian].copy()
    
    # Prepare translation text
    candidates['text_to_translate'] = candidates.apply(
        lambda row: str(row['formal_id']).strip() if pd.notna(row['formal_id']) and str(row['formal_id']).strip() 
                   else str(row['id']).strip() if pd.notna(row['id']) and str(row['id']).strip() 
                   else '', axis=1
    )
    
    # Remove empty texts
    candidates = candidates[candidates['text_to_translate'] != '']
    
    logging.info(f"Found {len(candidates)} entries needing translation")
    return candidates

def translate_chunk(texts, translator, chunk_size=10):
    """Translate a chunk of texts with error handling"""
    
    translations = []
    
    for i, text in enumerate(texts):
        try:
            if text and text.strip():
                result = translator.translate(text.strip(), src='id', dest='en')
                translation = result.text.lower().strip()
                
                # Basic validation
                if len(translation) > 50:  # Too long, likely error
                    translation = ''
                elif translation == text.lower():  # Translation failed
                    translation = ''
                
                translations.append(translation)
                logging.info(f"  {i+1}/{len(texts)}: {text} -> {translation}")
            else:
                translations.append('')
                
            # Rate limiting
            time.sleep(0.3)
            
        except Exception as e:
            logging.warning(f"Translation failed for '{text}': {e}")
            translations.append('')
            time.sleep(1)  # Longer delay on error
    
    return translations

def process_translations(df, batch_size=50, max_entries=None):
    """Process translations in batches"""
    
    # Get candidates
    candidates = get_translation_candidates(df)
    
    if len(candidates) == 0:
        logging.info("No entries need translation")
        return df
    
    # Limit if specified
    if max_entries and len(candidates) > max_entries:
        candidates = candidates.head(max_entries)
        logging.info(f"Limited to first {max_entries} entries")
    
    # Initialize translator
    translator = Translator()
    
    # Process in batches
    df_updated = df.copy()
    total_translated = 0
    
    for batch_start in range(0, len(candidates), batch_size):
        batch_end = min(batch_start + batch_size, len(candidates))
        batch = candidates.iloc[batch_start:batch_end]
        
        logging.info(f"Processing batch {batch_start//batch_size + 1}/{(len(candidates)-1)//batch_size + 1} ({len(batch)} entries)")
        
        # Translate batch
        texts = batch['text_to_translate'].tolist()
        translations = translate_chunk(texts, translator)
        
        # Update dataframe
        for i, (idx, row) in enumerate(batch.iterrows()):
            if i < len(translations) and translations[i]:
                df_updated.at[idx, 'en'] = translations[i]
                total_translated += 1
        
        # Progress update
        logging.info(f"Batch complete. Total translated so far: {total_translated}")
        
        # Longer delay between batches
        if batch_end < len(candidates):
            logging.info("Waiting 3 seconds before next batch...")
            time.sleep(3)
    
    logging.info(f"Translation complete! Total translated: {total_translated}")
    return df_updated

def create_summary(original_df, translated_df):
    """Create translation summary"""
    
    original_en = (original_df['en'].notna() & (original_df['en'] != '')).sum()
    final_en = (translated_df['en'].notna() & (translated_df['en'] != '')).sum()
    new_translations = final_en - original_en
    
    summary = f"""
TRANSLATION SUMMARY
==================

Results:
- Original English entries: {original_en}
- Final English entries: {final_en}
- New translations added: {new_translations}
- Total dataset entries: {len(translated_df)}
- English coverage: {(final_en / len(translated_df) * 100):.1f}%

Sample new translations:
"""
    
    # Show sample new translations
    new_mask = (original_df['en'].isna() | (original_df['en'] == '')) & (translated_df['en'].notna() & (translated_df['en'] != ''))
    samples = translated_df[new_mask].head(20)
    
    for i, (_, row) in enumerate(samples.iterrows(), 1):
        indonesian = row['formal_id'] if pd.notna(row['formal_id']) and row['formal_id'] else row['id']
        english = row['en']
        summary += f"  {i:2d}. {indonesian} -> {english}\n"
    
    return summary

def main():
    """Main function"""
    
    # Check command line arguments
    max_entries = None
    if len(sys.argv) > 1:
        try:
            max_entries = int(sys.argv[1])
            print(f"Limiting translation to {max_entries} entries")
        except ValueError:
            print("Invalid number provided, translating all entries")
    
    # Load dataset
    df = load_dataset()
    if df is None:
        return
    
    # Keep original for comparison
    original_df = df.copy()
    
    # Process translations
    print(f"Starting translation process...")
    if max_entries:
        print(f"Limited to {max_entries} entries for testing")
    
    translated_df = process_translations(df, batch_size=20, max_entries=max_entries)
    
    # Save results
    output_file = 'multilingual_stopwords_translated.csv'
    if max_entries:
        output_file = f'multilingual_stopwords_translated_{max_entries}.csv'
    
    translated_df.to_csv(output_file, index=False)
    logging.info(f"Saved translated dataset as {output_file}")
    
    # Create and save summary
    summary = create_summary(original_df, translated_df)
    
    summary_file = 'translation_summary.txt'
    if max_entries:
        summary_file = f'translation_summary_{max_entries}.txt'
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(summary)
    print(f"\n✅ Translation complete!")
    print(f"📊 Dataset saved as: {output_file}")
    print(f"📋 Summary saved as: {summary_file}")
    
    if max_entries:
        print(f"\nTo translate all entries, run: python translate_stopwords_efficient.py")
    else:
        print(f"\nTo test with limited entries, run: python translate_stopwords_efficient.py 100")

if __name__ == "__main__":
    main()
