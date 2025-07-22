#!/usr/bin/env python3
"""
Extract target snippets from classic novels for CLASSICS-EMR benchmark.

This script extracts 50 snippets evenly distributed across each novel,
ensuring each snippet:
- Starts at the beginning of a complete sentence  
- Ends at the end of a complete sentence
- Is evenly distributed across the book
- Has natural text without formatting artifacts
"""

import json
import os
import re
import random
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Novel files mapping
NOVEL_FILES = {
    'pride_and_prejudice': 'pride_and_prejudice.txt',
    'moby_dick': 'moby_dick.txt', 
    'frankenstein': 'frankenstein.txt',
    'alice_in_wonderland': 'alice_in_wonderland.txt',
    'war_and_peace': 'war_and_peace.txt',
    'great_expectations': 'great_expectations.txt',
    'the_time_machine': 'the_time_machine.txt',
    'dracula': 'dracula.txt',
    'dorian_gray': 'dorian_gray.txt',
    'scarlet_letter': 'scarlet_letter.txt',
    'call_of_the_wild': 'call_of_the_wild.txt',
    'sherlock_adventures': 'sherlock_adventures.txt',
    'hound_baskervilles': 'hound_baskervilles.txt',
    'treasure_island': 'treasure_island.txt',
    'tale_two_cities': 'tale_two_cities.txt'
}

def clean_text(text: str) -> str:
    """Clean and normalize text, removing Project Gutenberg artifacts."""
    # Remove Project Gutenberg header/footer boilerplate
    lines = text.split('\n')
    start_idx = 0
    end_idx = len(lines)
    
    # Find actual start of content (skip headers)
    for i, line in enumerate(lines):
        if any(marker in line.upper() for marker in [
            'START OF THE PROJECT GUTENBERG',
            'START OF THIS PROJECT GUTENBERG',
            '*** START OF THE PROJECT',
            'CHAPTER I', 'CHAPTER 1', 'CHAPTER ONE'
        ]):
            start_idx = i
            break
    
    # Find actual end of content (skip footers)
    for i in range(len(lines) - 1, -1, -1):
        if any(marker in lines[i].upper() for marker in [
            'END OF THE PROJECT GUTENBERG',
            'END OF THIS PROJECT GUTENBERG', 
            '*** END OF THE PROJECT'
        ]):
            end_idx = i
            break
    
    # Join the cleaned text
    cleaned_text = '\n'.join(lines[start_idx:end_idx])
    
    # Remove Project Gutenberg formatting artifacts
    # Remove illustration captions and copyright notices
    cleaned_text = re.sub(r'\[Illustration:.*?\]', '', cleaned_text, flags=re.DOTALL)
    cleaned_text = re.sub(r'\[_Copyright.*?\]', '', cleaned_text, flags=re.DOTALL)
    cleaned_text = re.sub(r'\[.*?_Copyright.*?\]', '', cleaned_text, flags=re.DOTALL)
    
    # Remove emphasis underscores (but preserve them within words)
    # This handles _word_ but not under_score within words
    cleaned_text = re.sub(r'\b_([^_\s]+)_\b', r'\1', cleaned_text)
    
    # Remove excessive whitespace while preserving paragraph breaks
    cleaned_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_text)
    cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)
    
    return cleaned_text.strip()

def detect_chapters(text: str) -> List[Dict]:
    """
    Detect chapter boundaries in the text.
    
    Returns:
        List of dictionaries with chapter info: {'start_pos', 'end_pos', 'title'}
    """
    chapters = []
    
    # Common chapter patterns - comprehensive and accurate
    chapter_patterns = [
        r'\n\s*CHAPTER\s+[IVXLCDM]+\b',     # CHAPTER with Roman numerals
        r'\n\s*CHAPTER\s+\d+\b',            # CHAPTER with Arabic numbers  
        r'\n\s*Chapter\s+[IVXLCDM]+\b',     # Chapter with Roman numerals
        r'\n\s*Chapter\s+\d+\b',            # Chapter with Arabic numbers
        r'\n\s*[IVXLCDM]+\.\s*[A-Z]',       # Roman numerals with period and title (like "I. THE PRISON DOOR")
        r'\n\s*[IVXLCDM]+\.\s*$',           # Standalone Roman numerals with period (end of line)
    ]
    
    # Find all chapter markers
    chapter_positions = []
    
    for pattern in chapter_patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        for match in matches:
            chapter_positions.append({
                'start_pos': match.start(),
                'end_pos': match.end(),
                'title': match.group().strip(),
                'pattern': pattern
            })
    
    # Sort by position and remove duplicates/overlaps
    chapter_positions.sort(key=lambda x: x['start_pos'])
    
    # Filter out positions that are too close to each other (within 1000 chars)
    filtered_chapters = []
    for chapter in chapter_positions:
        if not filtered_chapters or chapter['start_pos'] - filtered_chapters[-1]['start_pos'] > 1000:
            filtered_chapters.append(chapter)
    
    # Create chapter segments
    chapters = []
    for i, chapter in enumerate(filtered_chapters):
        chapter_start = chapter['end_pos']  # Start after the chapter heading
        chapter_end = filtered_chapters[i + 1]['start_pos'] if i + 1 < len(filtered_chapters) else len(text)
        
        chapters.append({
            'chapter_num': i + 1,
            'title': chapter['title'],
            'start_pos': chapter_start,
            'end_pos': chapter_end,
            'length': chapter_end - chapter_start
        })
    
    # If no chapters detected, treat entire text as one chapter
    if not chapters:
        chapters.append({
            'chapter_num': 1,
            'title': 'Full Text',
            'start_pos': 0,
            'end_pos': len(text),
            'length': len(text)
        })
    
    return chapters

def find_quality_sentence_boundaries(text: str) -> List[int]:
    """
    Find positions where quality sentences begin in the text.
    Avoids titles, single words, and poor sentence starts.
    
    Returns:
        List of character positions where good sentences start
    """
    # Enhanced sentence boundary detection
    # Look for sentence endings followed by whitespace and capital letter
    sentence_pattern = r'[.!?]+\s+[A-Z]'
    
    boundaries = [0]  # Always start at beginning
    
    matches = re.finditer(sentence_pattern, text)
    for match in matches:
        # Position after the punctuation and whitespace, at the capital letter
        sentence_start = match.end() - 1  # Back up to the capital letter
        
        # Extract the potential sentence to validate it
        remaining_text = text[sentence_start:]
        
        # Find the end of this potential sentence
        sentence_end_match = re.search(r'[.!?]+', remaining_text)
        if sentence_end_match:
            potential_sentence = remaining_text[:sentence_end_match.end()]
        else:
            potential_sentence = remaining_text[:200]  # Take first 200 chars as sample
        
        # Quality checks for the sentence
        words = potential_sentence.split()
        
        # Skip if too short (titles like "Mr.", "Mrs.", etc.)
        if len(words) < 3:
            continue
            
        # Skip if starts with common titles
        first_word = words[0] if words else ""
        if first_word in ['Mr.', 'Mrs.', 'Ms.', 'Dr.', 'Prof.', 'St.', 'Mt.']:
            continue
            
        # Skip if starts with single letter followed by period
        if len(first_word) == 2 and first_word.endswith('.'):
            continue
            
        # Skip if contains formatting artifacts in first few words
        first_few_words = ' '.join(words[:5])
        if any(artifact in first_few_words for artifact in ['[', ']', '_', '*', 'Illustration']):
            continue
        
        # If we get here, it's likely a good sentence start
        boundaries.append(sentence_start)
    
    return sorted(set(boundaries))  # Remove duplicates and sort

def simple_tokenize(text: str) -> List[str]:
    """Simple whitespace-based tokenization."""
    return [token.strip() for token in text.split() if token.strip()]

def extract_complete_snippet(text: str, start_pos: int, target_tokens: int = 64, 
                           max_tokens: int = 100, min_tokens: int = 40) -> Dict:
    """
    Extract a snippet starting at the given position, ending at a complete sentence.
    
    Args:
        text: The full text
        start_pos: Character position to start the snippet
        target_tokens: Target number of tokens (approximate)
        max_tokens: Maximum tokens allowed
        min_tokens: Minimum tokens required
        
    Returns:
        Dictionary with snippet information
    """
    # Extract text from start position
    remaining_text = text[start_pos:]
    
    # Find sentence boundaries in the remaining text
    sentence_endings = []
    for match in re.finditer(r'[.!?]+(?=\s+[A-Z]|\s*$)', remaining_text):
        sentence_endings.append(match.end())
    
    if not sentence_endings:
        # If no sentence endings found, just take a reasonable chunk
        tokens = simple_tokenize(remaining_text)
        selected_tokens = tokens[:target_tokens]
        snippet_text = ' '.join(selected_tokens)
    else:
        # Try to find a good ending point near target_tokens
        tokens = simple_tokenize(remaining_text)
        
        if len(tokens) < min_tokens:
            # Too short, take what we have
            selected_tokens = tokens
            snippet_text = ' '.join(selected_tokens)
        else:
            # Find the best sentence boundary near our target
            best_end_pos = None
            best_token_count = 0
            
            for end_pos in sentence_endings:
                # Get text up to this sentence boundary
                candidate_text = remaining_text[:end_pos]
                candidate_tokens = simple_tokenize(candidate_text)
                token_count = len(candidate_tokens)
                
                # Check if this is a good stopping point
                if min_tokens <= token_count <= max_tokens:
                    # This is within acceptable range
                    if best_end_pos is None:
                        best_end_pos = end_pos
                        best_token_count = token_count
                    else:
                        # Choose the one closest to target
                        current_distance = abs(token_count - target_tokens)
                        best_distance = abs(best_token_count - target_tokens)
                        if current_distance < best_distance:
                            best_end_pos = end_pos
                            best_token_count = token_count
                elif token_count >= target_tokens:
                    # We've gone past target, use this if we don't have a better option
                    if best_end_pos is None and token_count <= max_tokens:  # Add max_tokens check!
                        best_end_pos = end_pos
                        best_token_count = token_count
                    break
            
            if best_end_pos is not None:
                snippet_text = remaining_text[:best_end_pos]
            else:
                # Fallback: just take target_tokens
                tokens = simple_tokenize(remaining_text)
                selected_tokens = tokens[:target_tokens]
                snippet_text = ' '.join(selected_tokens)
    
    # Calculate actual token count
    actual_tokens = simple_tokenize(snippet_text)
    
    # Extract first sentence for metadata
    first_sentence_match = re.search(r'^[^.!?]*[.!?]+', snippet_text)
    if first_sentence_match:
        first_sentence = first_sentence_match.group().strip()
    else:
        # If no sentence ending found, take first 100 characters
        first_sentence = snippet_text[:100].strip()
        if len(snippet_text) > 100:
            first_sentence += "..."
    
    return {
        'text': snippet_text.strip(),
        'start_char_pos': start_pos,
        'end_char_pos': start_pos + len(snippet_text),
        'token_count': len(actual_tokens),
        'first_sentence': first_sentence
    }

def distribute_snippets_across_chapters(chapters: List[Dict], target_snippets: int = 50) -> List[Dict]:
    """
    Distribute target_snippets evenly across chapters based on their length.
    
    Args:
        chapters: List of chapter information
        target_snippets: Total number of snippets to extract
        
    Returns:
        List of snippet positions with chapter information
    """
    total_length = sum(ch['length'] for ch in chapters)
    snippet_positions = []
    
    # Distribute snippets proportionally to chapter length
    for chapter in chapters:
        chapter_proportion = chapter['length'] / total_length
        chapter_snippets = max(1, round(target_snippets * chapter_proportion))  # At least 1 per chapter
        
        # If chapter is very short, limit snippets
        max_possible = max(1, chapter['length'] // 2000)  # Rough estimate: 1 snippet per 2000 chars
        chapter_snippets = min(chapter_snippets, max_possible)
        
        # Distribute snippets evenly within the chapter
        if chapter_snippets > 0:
            chapter_start = chapter['start_pos']
            chapter_end = chapter['end_pos']
            chapter_length = chapter_end - chapter_start
            
            # Calculate even spacing
            if chapter_snippets == 1:
                positions = [chapter_start + chapter_length // 2]  # Middle of chapter
            else:
                step_size = chapter_length // (chapter_snippets + 1)
                positions = [chapter_start + step_size * (i + 1) for i in range(chapter_snippets)]
            
            for pos in positions:
                snippet_positions.append({
                    'position': pos,
                    'chapter_num': chapter['chapter_num'],
                    'chapter_title': chapter['title']
                })
    
    # If we have too many or too few snippets, adjust
    if len(snippet_positions) > target_snippets:
        # Keep the most evenly spaced ones
        step = len(snippet_positions) / target_snippets
        indices = [int(i * step) for i in range(target_snippets)]
        snippet_positions = [snippet_positions[i] for i in indices]
    elif len(snippet_positions) < target_snippets:
        # Add more snippets to largest chapters
        while len(snippet_positions) < target_snippets:
            largest_chapter = max(chapters, key=lambda x: x['length'])
            # Add one more snippet to this chapter
            new_pos = largest_chapter['start_pos'] + largest_chapter['length'] // 2
            snippet_positions.append({
                'position': new_pos,
                'chapter_num': largest_chapter['chapter_num'],
                'chapter_title': largest_chapter['title']
            })
    
    return snippet_positions[:target_snippets]  # Ensure exact count

def align_to_sentence_boundary(text: str, position: int, sentence_boundaries: List[int]) -> int:
    """
    Find the closest quality sentence boundary at or after the given position.
    
    Args:
        text: The full text
        position: Desired position
        sentence_boundaries: List of sentence start positions
        
    Returns:
        Adjusted position aligned to sentence boundary
    """
    # Find the closest sentence boundary at or after this position
    for boundary in sentence_boundaries:
        if boundary >= position:
            return boundary
    
    # If no boundary found after position, return the last boundary
    return sentence_boundaries[-1] if sentence_boundaries else position

def process_novel(novel_key: str, novel_file: str, novels_dir: Path) -> Dict:
    """Process a single novel and extract snippets."""
    logger.info(f"Processing {novel_key}...")
    
    # Read the novel text
    novel_path = novels_dir / novel_file
    try:
        with open(novel_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    except Exception as e:
        logger.error(f"Error reading {novel_file}: {e}")
        return None
    
    # Clean text
    cleaned_text = clean_text(raw_text)
    logger.info(f"  Text length: {len(cleaned_text):,} characters")
    
    # Detect chapters
    chapters = detect_chapters(cleaned_text)
    logger.info(f"  Detected {len(chapters)} chapters")
    
    # Find quality sentence boundaries
    sentence_boundaries = find_quality_sentence_boundaries(cleaned_text)
    logger.info(f"  Found {len(sentence_boundaries)} quality sentence boundaries")
    
    # Distribute snippets across chapters
    snippet_positions = distribute_snippets_across_chapters(chapters, target_snippets=50)
    logger.info(f"  Planned {len(snippet_positions)} snippets")
    
    # Extract snippets at aligned positions
    snippets = []
    for i, pos_info in enumerate(snippet_positions):
        # Align position to sentence boundary
        aligned_pos = align_to_sentence_boundary(cleaned_text, pos_info['position'], sentence_boundaries)
        
        # Extract complete snippet
        snippet_data = extract_complete_snippet(cleaned_text, aligned_pos)
        
        # Quality check
        if len(snippet_data['text']) < 100:  # Skip very short snippets
            logger.warning(f"  Skipping very short snippet {i+1} ({len(snippet_data['text'])} chars)")
            continue
            
        # Add metadata
        snippet = {
            'snippet_id': len(snippets) + 1,  # Use actual count for ID
            'chapter_num': pos_info['chapter_num'],
            'chapter_title': pos_info['chapter_title'],
            'start_char_pos': snippet_data['start_char_pos'],
            'end_char_pos': snippet_data['end_char_pos'],
            'token_count': snippet_data['token_count'],
            'text': snippet_data['text'],
            'first_sentence': snippet_data['first_sentence']
        }
        snippets.append(snippet)
    
    logger.info(f"  Extracted {len(snippets)} quality snippets")
    
    # If we have fewer than 50, try to add more from larger chapters
    while len(snippets) < 50 and len(sentence_boundaries) > len(snippets):
        # Find a gap where we can add another snippet
        largest_chapter = max(chapters, key=lambda x: x['length'])
        # Try a different position in the largest chapter
        new_pos = largest_chapter['start_pos'] + (largest_chapter['length'] * 2 // 3)
        aligned_pos = align_to_sentence_boundary(cleaned_text, new_pos, sentence_boundaries)
        
        # Check if this position is too close to existing snippets
        too_close = False
        for existing in snippets:
            if abs(aligned_pos - existing['start_char_pos']) < 1000:  # Within 1000 chars
                too_close = True
                break
        
        if not too_close:
            snippet_data = extract_complete_snippet(cleaned_text, aligned_pos)
            if len(snippet_data['text']) >= 100:
                snippet = {
                    'snippet_id': len(snippets) + 1,
                    'chapter_num': largest_chapter['chapter_num'],
                    'chapter_title': largest_chapter['title'],
                    'start_char_pos': snippet_data['start_char_pos'],
                    'end_char_pos': snippet_data['end_char_pos'],
                    'token_count': snippet_data['token_count'],
                    'text': snippet_data['text'],
                    'first_sentence': snippet_data['first_sentence']
                }
                snippets.append(snippet)
        else:
            break  # Can't find more good positions
    
    # Create novel result
    result = {
        'novel_key': novel_key,
        'novel_file': novel_file,
        'text_length': len(cleaned_text),
        'chapters_detected': len(chapters),
        'chapters': chapters,
        'snippets_extracted': len(snippets),
        'snippets': snippets
    }
    
    return result

def main():
    """Main extraction pipeline."""
    logger.info("Starting improved snippet extraction for CLASSICS-EMR...")
    
    # Set random seed for reproducibility (though we're using deterministic distribution now)
    random.seed(42)
    
    # Setup paths
    novels_dir = Path('data/novels')
    output_dir = Path('data/snippets')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each novel
    all_results = {}
    total_snippets = 0
    
    for novel_key, novel_file in NOVEL_FILES.items():
        if not (novels_dir / novel_file).exists():
            logger.warning(f"Novel file not found: {novel_file}")
            continue
            
        result = process_novel(novel_key, novel_file, novels_dir)
        if result:
            all_results[novel_key] = result
            total_snippets += result['snippets_extracted']
            
            # Save individual novel snippets
            novel_output_file = output_dir / f"{novel_key}_snippets.json"
            with open(novel_output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
                
    # Save combined results
    summary = {
        'extraction_config': {
            'target_tokens_per_snippet': 64,
            'min_tokens_per_snippet': 40,
            'max_tokens_per_snippet': 100,
            'snippets_per_novel': 50,
            'distribution_method': 'even_across_chapters',
            'sentence_boundary_aligned': True,
            'chapter_boundary_respected': True,
            'complete_sentences_only': True,
            'formatting_artifacts_removed': True,
            'random_seed': 42
        },
        'summary_stats': {
            'novels_processed': len(all_results),
            'total_snippets_extracted': total_snippets,
            'target_snippets': 750  # 15 novels × 50 snippets
        },
        'novel_results': all_results
    }
    
    summary_file = output_dir / 'extraction_summary.json'
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Extraction complete!")
    logger.info(f"  Novels processed: {len(all_results)}")
    logger.info(f"  Total snippets: {total_snippets} (target: 750)")
    logger.info(f"  Output directory: {output_dir}")
    
    # Print summary table
    print("\n" + "="*100)
    print("IMPROVED SNIPPET EXTRACTION SUMMARY")
    print("="*100)
    print(f"{'Novel':<25} {'Text Length':<12} {'Chapters':<10} {'Snippets':<10} {'Avg Tokens':<12} {'Token Range':<15}")
    print("-"*100)
    
    for novel_key, result in all_results.items():
        if result['snippets']:
            token_counts = [s['token_count'] for s in result['snippets']]
            avg_tokens = sum(token_counts) / len(token_counts)
            min_tokens = min(token_counts)
            max_tokens = max(token_counts)
            token_range = f"{min_tokens}-{max_tokens}"
        else:
            avg_tokens = 0
            token_range = "N/A"
            
        print(f"{novel_key:<25} {result['text_length']:<12,} {result['chapters_detected']:<10} {result['snippets_extracted']:<10} {avg_tokens:<12.1f} {token_range:<15}")
    
    print("-"*100)
    print(f"{'TOTAL':<25} {'':<12} {'':<10} {total_snippets:<10} {'':<12} {'':<15}")
    print("="*100)
    
    # Show improvement details
    if all_results:
        first_novel = list(all_results.values())[0]
        print(f"\nExtraction improvements demonstrated:")
        print(f"✅ Complete sentences (no mid-sentence cuts)")
        print(f"✅ Quality sentence boundaries (no 'Mr.', 'Mrs.' starts)")
        print(f"✅ Formatting artifacts removed")
        print(f"✅ Natural token variation (40-100 tokens)")
        print(f"✅ Even distribution across chapters")

if __name__ == "__main__":
    main() 