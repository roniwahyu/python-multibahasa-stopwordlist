#!/usr/bin/env python3
"""
Conservative translation script with better rate limiting and error handling
"""

import pandas as pd
import time
import logging
from googletrans import Translator
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def translate_with_retry(translator, text, max_retries=3):
    """Translate with retry logic"""
    
    for attempt in range(max_retries):
        try:
            result = translator.translate(text.strip(), src='id', dest='en')
            translation = result.text.lower().strip()
            
            # Basic validation
            if len(translation) > 50:  # Too long, likely error
                return ''
            elif translation == text.lower():  # Translation failed
                return ''
            
            return translation
            
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed for '{text}': {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return ''
    
    return ''

def translate_batch_conservative(df, start_idx=0, batch_size=100):
    """Translate a batch of entries conservatively"""
    
    # Get entries that need translation
    missing_en = (df['en'].isna() | (df['en'] == ''))
    has_indonesian = (df['id'].notna() & (df['id'] != '')) | (df['formal_id'].notna() & (df['formal_id'] != ''))
    candidates = df[missing_en & has_indonesian].copy()
    
    if len(candidates) == 0:
        print("No entries need translation")
        return df, 0
    
    # Apply start index and batch size
    end_idx = min(start_idx + batch_size, len(candidates))
    batch_candidates = candidates.iloc[start_idx:end_idx]
    
    print(f"Translating entries {start_idx + 1} to {end_idx} of {len(candidates)} total")
    
    # Initialize translator
    translator = Translator()
    
    # Process each entry
    df_updated = df.copy()
    translated_count = 0
    
    for i, (idx, row) in enumerate(batch_candidates.iterrows()):
        # Get text to translate
        if pd.notna(row['formal_id']) and str(row['formal_id']).strip():
            text = str(row['formal_id']).strip()
        elif pd.notna(row['id']) and str(row['id']).strip():
            text = str(row['id']).strip()
        else:
            continue
        
        # Skip if text is too long or looks like English
        if len(text) > 30 or any(word in text.lower() for word in ['the', 'and', 'for', 'with', 'you', 'are']):
            continue
        
        print(f"  {i + 1:3d}/{len(batch_candidates)}: Translating '{text}'...", end=' ')
        
        # Translate
        translation = translate_with_retry(translator, text)
        
        if translation:
            df_updated.at[idx, 'en'] = translation
            translated_count += 1
            print(f"-> '{translation}'")
        else:
            print("-> FAILED")
        
        # Rate limiting - wait between each translation
        time.sleep(1)
    
    print(f"\nBatch complete: {translated_count} translations successful")
    return df_updated, translated_count

def main():
    """Main function"""
    
    # Parse command line arguments
    start_idx = 0
    batch_size = 50  # Conservative batch size
    
    if len(sys.argv) > 1:
        try:
            batch_size = int(sys.argv[1])
        except ValueError:
            print("Invalid batch size, using default 50")
    
    if len(sys.argv) > 2:
        try:
            start_idx = int(sys.argv[2])
        except ValueError:
            print("Invalid start index, using 0")
    
    print(f"Starting translation with batch_size={batch_size}, start_idx={start_idx}")
    
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
    total_needing_translation = (missing_en & has_indonesian).sum()
    
    print(f"Total entries needing translation: {total_needing_translation}")
    
    # Process batch
    df_translated, count = translate_batch_conservative(df, start_idx, batch_size)
    
    # Save results
    output_file = f'multilingual_stopwords_batch_{start_idx}_{start_idx + batch_size}.csv'
    df_translated.to_csv(output_file, index=False)
    
    # Show summary
    original_en = (df['en'].notna() & (df['en'] != '')).sum()
    final_en = (df_translated['en'].notna() & (df_translated['en'] != '')).sum()
    
    print(f"\n=== TRANSLATION SUMMARY ===")
    print(f"Original English entries: {original_en}")
    print(f"Final English entries: {final_en}")
    print(f"New translations: {count}")
    print(f"Saved as: {output_file}")
    
    # Show next command
    next_start = start_idx + batch_size
    if next_start < total_needing_translation:
        print(f"\nTo continue translation, run:")
        print(f"python translate_conservative.py {batch_size} {next_start}")
    else:
        print(f"\nTranslation complete!")

if __name__ == "__main__":
    main()
