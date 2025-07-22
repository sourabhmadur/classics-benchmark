#!/usr/bin/env python3
"""
Download and process the 15 selected novels for CLASSICS-EMR benchmark.
All novels are public domain works available from Project Gutenberg.
"""

import os
import re
import json
import hashlib
import requests
from pathlib import Path
from typing import Dict, List, Tuple
import time

# Project Gutenberg URLs for the 15 selected novels
NOVELS = {
    "pride_and_prejudice": {
        "title": "Pride and Prejudice",
        "author": "Jane Austen", 
        "url": "https://www.gutenberg.org/files/1342/1342-0.txt",
        "gutenberg_id": 1342
    },
    "moby_dick": {
        "title": "Moby Dick; Or, The Whale",
        "author": "Herman Melville",
        "url": "https://www.gutenberg.org/files/2701/2701-0.txt", 
        "gutenberg_id": 2701
    },
    "frankenstein": {
        "title": "Frankenstein; Or, The Modern Prometheus",
        "author": "Mary Wollstonecraft Shelley",
        "url": "https://www.gutenberg.org/files/84/84-0.txt",
        "gutenberg_id": 84
    },
    "alice_in_wonderland": {
        "title": "Alice's Adventures in Wonderland",
        "author": "Lewis Carroll",
        "url": "https://www.gutenberg.org/files/11/11-0.txt",
        "gutenberg_id": 11
    },
    "war_and_peace": {
        "title": "War and Peace",
        "author": "Leo Tolstoy",
        "url": "https://www.gutenberg.org/files/2600/2600-0.txt",
        "gutenberg_id": 2600
    },
    "great_expectations": {
        "title": "Great Expectations", 
        "author": "Charles Dickens",
        "url": "https://www.gutenberg.org/files/1400/1400-0.txt",
        "gutenberg_id": 1400
    },
    "the_time_machine": {
        "title": "The Time Machine",
        "author": "H. G. Wells",
        "url": "https://www.gutenberg.org/files/35/35-0.txt",
        "gutenberg_id": 35
    },
    "dracula": {
        "title": "Dracula",
        "author": "Bram Stoker", 
        "url": "https://www.gutenberg.org/files/345/345-0.txt",
        "gutenberg_id": 345
    },
    "dorian_gray": {
        "title": "The Picture of Dorian Gray",
        "author": "Oscar Wilde",
        "url": "https://www.gutenberg.org/files/174/174-0.txt",
        "gutenberg_id": 174
    },
    "scarlet_letter": {
        "title": "The Scarlet Letter",
        "author": "Nathaniel Hawthorne",
        "url": "https://www.gutenberg.org/files/33/33-0.txt",
        "gutenberg_id": 33
    },
    "call_of_the_wild": {
        "title": "The Call of the Wild",
        "author": "Jack London",
        "url": "https://www.gutenberg.org/files/215/215-0.txt",
        "gutenberg_id": 215
    },
    "sherlock_adventures": {
        "title": "The Adventures of Sherlock Holmes",
        "author": "Arthur Conan Doyle",
        "url": "https://www.gutenberg.org/files/1661/1661-0.txt",
        "gutenberg_id": 1661
    },
    "hound_baskervilles": {
        "title": "The Hound of the Baskervilles",
        "author": "Arthur Conan Doyle",
        "url": "https://www.gutenberg.org/files/2852/2852-0.txt",
        "gutenberg_id": 2852
    },
    "treasure_island": {
        "title": "Treasure Island",
        "author": "Robert Louis Stevenson",
        "url": "https://www.gutenberg.org/files/120/120-0.txt",
        "gutenberg_id": 120
    },
    "tale_two_cities": {
        "title": "A Tale of Two Cities",
        "author": "Charles Dickens",
        "url": "https://www.gutenberg.org/files/98/98-0.txt",
        "gutenberg_id": 98
    }
}

def download_text(url: str, title: str) -> str:
    """Download text from Project Gutenberg with retry logic."""
    print(f"Downloading {title}...")
    
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed for {title}: {e}")
            if attempt < 2:
                time.sleep(2)
            else:
                raise
    
def clean_gutenberg_text(text: str) -> str:
    """Remove Project Gutenberg header and footer."""
    lines = text.split('\n')
    
    # Find start of actual text (after "*** START OF" marker)
    start_idx = 0
    for i, line in enumerate(lines):
        if "*** START OF" in line.upper():
            start_idx = i + 1
            break
    
    # Find end of actual text (before "*** END OF" marker)  
    end_idx = len(lines)
    for i, line in enumerate(lines):
        if "*** END OF" in line.upper():
            end_idx = i
            break
            
    return '\n'.join(lines[start_idx:end_idx]).strip()

def extract_chapters(text: str, title: str) -> List[str]:
    """Extract chapters from the text."""
    # This is a simple heuristic - may need adjustment per book
    chapter_patterns = [
        r'^CHAPTER\s+[IVXLCDM]+\.?\s*$',  # Roman numerals
        r'^CHAPTER\s+\d+\.?\s*$',         # Arabic numerals  
        r'^Chapter\s+[IVXLCDM]+\.?\s*$',  # Roman numerals (capitalized)
        r'^Chapter\s+\d+\.?\s*$',         # Arabic numerals (capitalized)
    ]
    
    lines = text.split('\n')
    chapter_starts = []
    
    for pattern in chapter_patterns:
        for i, line in enumerate(lines):
            if re.match(pattern, line.strip()):
                chapter_starts.append(i)
    
    chapter_starts = sorted(set(chapter_starts))
    
    if not chapter_starts:
        # No chapters found, treat whole text as one chapter
        print(f"Warning: No chapters detected in {title}, using full text")
        return [text]
    
    chapters = []
    for i in range(len(chapter_starts)):
        start = chapter_starts[i]
        end = chapter_starts[i + 1] if i + 1 < len(chapter_starts) else len(lines)
        chapter_text = '\n'.join(lines[start:end]).strip()
        if chapter_text:
            chapters.append(chapter_text)
    
    return chapters

def calculate_sha256(text: str) -> str:
    """Calculate SHA-256 hash of text."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def process_novel(key: str, info: Dict) -> Dict:
    """Download and process a single novel."""
    try:
        # Download text
        raw_text = download_text(info["url"], info["title"])
        
        # Clean Project Gutenberg formatting
        clean_text = clean_gutenberg_text(raw_text)
        
        # Extract chapters
        chapters = extract_chapters(clean_text, info["title"])
        
        # Calculate hashes for each chapter
        chapter_hashes = [calculate_sha256(chapter) for chapter in chapters]
        
        # Save processed text
        output_dir = Path("novels")
        output_dir.mkdir(exist_ok=True)
        
        novel_file = output_dir / f"{key}.txt"
        with open(novel_file, 'w', encoding='utf-8') as f:
            f.write(clean_text)
        
        # Save chapter metadata
        metadata = {
            "title": info["title"],
            "author": info["author"], 
            "gutenberg_id": info["gutenberg_id"],
            "total_chapters": len(chapters),
            "chapter_hashes": chapter_hashes,
            "total_length": len(clean_text),
            "full_text_hash": calculate_sha256(clean_text)
        }
        
        metadata_file = output_dir / f"{key}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ Processed {info['title']}: {len(chapters)} chapters, {len(clean_text):,} characters")
        return metadata
        
    except Exception as e:
        print(f"✗ Failed to process {info['title']}: {e}")
        return None

def main():
    """Download and process all novels."""
    print("Starting download and processing of 15 novels for CLASSICS-EMR...")
    print("=" * 60)
    
    results = {}
    failed = []
    
    for key, info in NOVELS.items():
        metadata = process_novel(key, info)
        if metadata:
            results[key] = metadata
        else:
            failed.append(key)
        
        # Be respectful to Project Gutenberg servers
        time.sleep(1)
    
    # Save summary
    summary = {
        "total_novels": len(NOVELS),
        "successful_downloads": len(results),
        "failed_downloads": failed,
        "novels": results
    }
    
    with open("novels/download_summary.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "=" * 60)
    print(f"Download complete: {len(results)}/{len(NOVELS)} novels processed successfully")
    
    if failed:
        print(f"Failed novels: {', '.join(failed)}")
    
    print("\nNext steps:")
    print("1. Review novels/ directory for downloaded texts")
    print("2. Run verification against The Pile dataset")
    print("3. Extract 50 snippets per novel (750 total)")

if __name__ == "__main__":
    main() 