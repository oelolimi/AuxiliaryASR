#!/usr/bin/env python3
"""
Quick script to find and remove corrupted audio files from your dataset
"""
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
        if sr <= 0:
            return False, "Invalid sample rate"
        return True, f"OK - {len(wave)} samples, {sr} Hz"
    except Exception as e:
        return False, str(e)

def clean_dataset(input_file, output_file=None):
    """Clean dataset by removing lines with corrupted audio files"""
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_cleaned{ext}"
    
    corrupted_files = []
    valid_lines = []
    total_lines = 0
    
    print(f"🔍 Checking audio files in {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        total_lines += 1
        line = line.strip()
        
        if not line:
            continue
            
        # Parse the line - assumes format: audio_path|text|speaker_id
        parts = line.split('|')
        if len(parts) < 1:
            print(f"⚠️  Line {i+1}: Invalid format - {line}")
            continue
            
        audio_path = parts[0]
        
        # Check if file exists
        if not os.path.exists(audio_path):
            corrupted_files.append((i+1, audio_path, "File not found"))
            print(f"❌ Line {i+1}: File not found - {audio_path}")
            continue
            
        # Check if file can be read
        is_valid, message = check_audio_file(audio_path)
        
        if not is_valid:
            corrupted_files.append((i+1, audio_path, message))
            print(f"❌ Line {i+1}: {audio_path} - {message}")
        else:
            valid_lines.append(line)
            if i % 100 == 0:  # Print progress every 100 files
                print(f"✅ Processed {i+1}/{len(lines)} files...")
    
    # Write cleaned dataset
    print(f"\n💾 Writing cleaned dataset to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in valid_lines:
            f.write(line + '\n')
    
    # Print summary
    print(f"\n📊 Summary:")
    print(f"Total lines: {total_lines}")
    print(f"Valid files: {len(valid_lines)}")
    print(f"Corrupted files: {len(corrupted_files)}")
    print(f"Success rate: {len(valid_lines) / total_lines * 100:.1f}%")
    print(f"Cleaned dataset saved to: {output_file}")
    
    if corrupted_files:
        # Save corrupted files list
        corrupted_file = f"{os.path.splitext(input_file)[0]}_corrupted.txt"
        with open(corrupted_file, 'w', encoding='utf-8') as f:
            f.write("Line\tFile\tError\n")
            for line_num, file_path, error in corrupted_files:
                f.write(f"{line_num}\t{file_path}\t{error}\n")
        print(f"Corrupted files list saved to: {corrupted_file}")
    
    return len(corrupted_files) == 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_audio_fix.py <dataset_file> [output_file]")
        print("Example: python quick_audio_fix.py train_list.txt train_list_cleaned.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_file):
        print(f"❌ Dataset file not found: {input_file}")
        sys.exit(1)
    
    success = clean_dataset(input_file, output_file)
    
    if success:
        print(f"\n🎉 All files are valid! No cleaning needed.")
    else:
        print(f"\n⚠️  Some files were corrupted and removed.")
        print(f"Use the cleaned dataset file for training.")

if __name__ == "__main__":
    main()
