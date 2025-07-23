#!/usr/bin/env python3
import soundfile as sf
import os
import sys
from pathlib import Path

def check_audio_file(file_path):
    """Check if an audio file can be read properly"""
    try:
        wave, sr = sf.read(file_path)
        if len(wave) == 0:
            return False, "Empty audio file"
        return True, f"OK - {len(wave)} samples, {sr} Hz"
    except Exception as e:
        return False, str(e)

def check_dataset_files(data_list_path, max_check=100):
    """Check audio files in the dataset"""
    corrupted_files = []
    checked_files = []
    
    with open(data_list_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Checking up to {min(max_check, len(lines))} files from {data_list_path}")
    
    for i, line in enumerate(lines[:max_check]):
        if not line.strip():
            continue
            
        # Parse the line - assumes format: audio_path|text|speaker_id
        parts = line.strip().split('|')
        if len(parts) < 1:
            continue
            
        audio_path = parts[0]
        
        # Check if file exists
        if not os.path.exists(audio_path):
            corrupted_files.append((audio_path, f"File not found"))
            print(f"❌ {i+1:3d}: File not found: {audio_path}")
            continue
            
        # Check if file can be read
        is_valid, message = check_audio_file(audio_path)
        checked_files.append((audio_path, is_valid, message))
        
        if not is_valid:
            corrupted_files.append((audio_path, message))
            print(f"❌ {i+1:3d}: {audio_path} - {message}")
        else:
            print(f"✅ {i+1:3d}: {audio_path} - {message}")
    
    print(f"\n📊 Summary:")
    print(f"Total checked: {len(checked_files)}")
    print(f"Corrupted files: {len(corrupted_files)}")
    print(f"Success rate: {(len(checked_files) - len(corrupted_files)) / len(checked_files) * 100:.1f}%")
    
    if corrupted_files:
        print(f"\n🚨 Corrupted files found:")
        for file_path, error in corrupted_files:
            print(f"  - {file_path}: {error}")
    
    return corrupted_files

def test_arabic_g2p():
    """Test the Arabic G2P with some sample text"""
    from arabic_g2p import ArabicG2P
    
    g2p = ArabicG2P()
    
    test_texts = [
        "مرحبا",  # Hello
        "كيف حالك",  # How are you
        "شكرا",  # Thank you
        "الله",  # Allah
        "Egypt",  # English word
    ]
    
    print("\n🔍 Testing Arabic G2P:")
    for text in test_texts:
        try:
            phonemes = g2p(text)
            print(f"  '{text}' -> {phonemes}")
        except Exception as e:
            print(f"  '{text}' -> ERROR: {e}")

def test_text_cleaner():
    """Test if the text cleaner can handle the phonemes"""
    try:
        from text_utils import TextCleaner
        
        # Load the word index dict
        dict_path = "word_index_dict.txt"
        if not os.path.exists(dict_path):
            print(f"❌ Word index dict not found: {dict_path}")
            return
            
        text_cleaner = TextCleaner(dict_path)
        
        # Test some phonemes
        test_phonemes = ['ʔ', 'b', 'a', 'aː', 'sil', 'h', 'ħ', 'g']
        
        print(f"\n🧪 Testing TextCleaner with phonemes:")
        for phoneme in test_phonemes:
            try:
                if phoneme in text_cleaner.word_index_dictionary:
                    idx = text_cleaner.word_index_dictionary[phoneme]
                    print(f"  '{phoneme}' -> index {idx} ✅")
                else:
                    print(f"  '{phoneme}' -> NOT FOUND ❌")
            except Exception as e:
                print(f"  '{phoneme}' -> ERROR: {e}")
                
    except ImportError as e:
        print(f"❌ Could not import TextCleaner: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_dataset.py <path_to_data_list.txt> [max_files_to_check]")
        print("Example: python debug_dataset.py train_list.txt 50")
        sys.exit(1)
    
    data_list_path = sys.argv[1]
    max_check = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    
    if not os.path.exists(data_list_path):
        print(f"❌ Data list file not found: {data_list_path}")
        sys.exit(1)
    
    # Check dataset files
    corrupted = check_dataset_files(data_list_path, max_check)
    
    # Test G2P
    test_arabic_g2p()
    
    # Test text cleaner
    test_text_cleaner()
    
    if corrupted:
        print(f"\n⚠️  Found {len(corrupted)} corrupted files. Consider:")
        print("1. Remove these files from your dataset")
        print("2. Re-download or fix the corrupted audio files") 
        print("3. Check your audio preprocessing pipeline")
