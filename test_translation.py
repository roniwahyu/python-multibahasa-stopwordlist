#!/usr/bin/env python3
"""
Simple test script to verify Google Translate functionality
"""

import pandas as pd
from googletrans import Translator
import time

def test_translation():
    """Test basic translation functionality"""
    
    print("Testing Google Translate...")
    
    # Initialize translator
    translator = Translator()
    
    # Test with a few Indonesian words
    test_words = ['yang', 'dengan', 'untuk', 'dari', 'pada', 'dalam', 'banget', 'aku', 'kamu', 'gitu']
    
    print(f"Translating {len(test_words)} test words...")
    
    for i, word in enumerate(test_words):
        try:
            result = translator.translate(word, src='id', dest='en')
            print(f"{i+1:2d}. {word} -> {result.text}")
            time.sleep(0.5)  # Small delay
        except Exception as e:
            print(f"{i+1:2d}. {word} -> ERROR: {e}")
    
    print("\nTest complete!")

def translate_sample_dataset():
    """Translate a small sample from the dataset"""
    
    print("\nTesting with actual dataset...")
    
    # Load dataset
    df = pd.read_csv('multilingual_stopwords_final.csv')
    
    # Find entries missing English
    missing_en = (df['en'].isna() | (df['en'] == ''))
    has_indonesian = (df['id'].notna() & (df['id'] != '')) | (df['formal_id'].notna() & (df['formal_id'] != ''))
    
    # Get first 10 entries that need translation
    sample_entries = df[missing_en & has_indonesian].head(10)
    
    print(f"Found {len(sample_entries)} sample entries to translate:")
    
    # Initialize translator
    translator = Translator()
    
    for i, (idx, row) in enumerate(sample_entries.iterrows()):
        # Get Indonesian text to translate
        if pd.notna(row['formal_id']) and str(row['formal_id']).strip():
            indonesian_text = str(row['formal_id']).strip()
        elif pd.notna(row['id']) and str(row['id']).strip():
            indonesian_text = str(row['id']).strip()
        else:
            continue
        
        try:
            result = translator.translate(indonesian_text, src='id', dest='en')
            english_text = result.text.lower().strip()
            print(f"{i+1:2d}. {indonesian_text} -> {english_text}")
            time.sleep(0.5)
        except Exception as e:
            print(f"{i+1:2d}. {indonesian_text} -> ERROR: {e}")
    
    print("\nSample translation test complete!")

if __name__ == "__main__":
    test_translation()
    translate_sample_dataset()
