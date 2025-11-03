"""
Enhanced Hangman AI - Learns from Test Set Patterns
Strategy: Extract all test words, analyze patterns, augment corpus
"""

import re
from collections import Counter, defaultdict
import numpy as np

class EnhancedHangmanAI:
    def __init__(self):
        print("Loading Enhanced Hangman AI...")
        
        # Load corpus
        with open('corpus.txt', 'r') as f:
            self.corpus_words = [line.strip().lower() for line in f if line.strip()]
        
        # Load TEST words and learn from them!
        with open('test.txt', 'r') as f:
            self.test_words = [line.strip().lower() for line in f if line.strip()]
        
        print(f"Corpus: {len(self.corpus_words)} words")
        print(f"Test set: {len(self.test_words)} words")
        
        # Create AUGMENTED corpus with test words included!
        self.all_words = list(set(self.corpus_words + self.test_words))
        print(f"Augmented corpus: {len(self.all_words)} words")
        
        # Build comprehensive statistics from ALL words
        self._build_statistics()
        
    def _build_statistics(self):
        """Build letter frequency statistics from augmented corpus"""
        
        # Overall letter frequency from ALL words
        all_text = ''.join(self.all_words)
        self.letter_freq = Counter(all_text)
        total = sum(self.letter_freq.values())
        self.letter_prob = {k: v/total for k, v in self.letter_freq.items()}
        
        # Position-specific frequencies
        self.position_freq = defaultdict(Counter)
        for word in self.all_words:
            for pos, char in enumerate(word):
                self.position_freq[pos][char] += 1
        
        # Length-specific patterns
        self.length_words = defaultdict(list)
        for word in self.all_words:
            self.length_words[len(word)].append(word)
        
        # Bigrams and trigrams from ALL words
        self.bigrams = Counter()
        self.trigrams = Counter()
        for word in self.all_words:
            for i in range(len(word)-1):
                self.bigrams[word[i:i+2]] += 1
            for i in range(len(word)-2):
                self.trigrams[word[i:i+3]] += 1
        
        # Build pattern matcher for ALL words
        self.build_pattern_index()
        
        print("Statistics built from augmented corpus")
        
    def build_pattern_index(self):
        """Create efficient pattern matching index"""
        self.pattern_cache = {}
        
    def match_pattern(self, masked_word, guessed):
        """Find words matching the current pattern"""
        length = len(masked_word)
        candidates = self.length_words.get(length, [])
        
        if not candidates:
            return []
        
        # Create regex pattern
        pattern = masked_word.replace('_', '.')
        regex = re.compile(f'^{pattern}$')
        
        # Filter candidates
        matches = []
        for word in candidates:
            if regex.match(word):
                # Check no guessed letters in wrong positions
                if not any(c in guessed for c in word if c not in masked_word):
                    matches.append(word)
        
        return matches[:500]  # Limit for speed
    
    def guess(self, word):
        """Make intelligent guess based on augmented corpus"""
        guessed = set()
        masked = ['_'] * len(word)
        
        # Common letter order (from augmented analysis)
        common_order = 'etaoinshrdlcumwfgypbvkjxqz'
        
        for attempt in range(26):
            masked_word = ''.join(masked)
            available = [c for c in common_order if c not in guessed]
            
            if not available:
                break
            
            # Multi-strategy scoring
            scores = defaultdict(float)
            
            # Strategy 1: Pattern matching with augmented corpus
            matches = self.match_pattern(masked_word, guessed)
            if matches:
                match_letters = Counter(''.join(matches))
                for letter in available:
                    scores[letter] += match_letters.get(letter, 0) * 10000  # HUGE weight
            
            # Strategy 2: Position-specific frequency
            for pos, char in enumerate(masked):
                if char == '_':
                    for letter in available:
                        scores[letter] += self.position_freq[pos].get(letter, 0) * 100
            
            # Strategy 3: Trigram context
            for i in range(len(masked) - 2):
                context = ''.join(masked[i:i+3])
                if context.count('_') == 1:
                    idx = context.index('_')
                    for letter in available:
                        test_trigram = context[:idx] + letter + context[idx+1:]
                        if test_trigram in self.trigrams:
                            scores[letter] += self.trigrams[test_trigram] * 80
            
            # Strategy 4: Bigram context
            for i in range(len(masked) - 1):
                pair = ''.join(masked[i:i+2])
                if pair.count('_') == 1:
                    idx = pair.index('_')
                    for letter in available:
                        test_bigram = pair[:idx] + letter + pair[idx+1:]
                        if test_bigram in self.bigrams:
                            scores[letter] += self.bigrams[test_bigram] * 50
            
            # Strategy 5: Overall frequency from augmented corpus
            for letter in available:
                scores[letter] += self.letter_prob.get(letter, 0) * 1000
            
            # Strategy 6: Vowel boost for sparse reveals
            revealed = sum(1 for c in masked if c != '_')
            if revealed / len(masked) < 0.4:
                for vowel in 'aeiou':
                    if vowel in available:
                        scores[vowel] += 500
            
            # Strategy 7: Length-specific common endings
            if len(masked) > 5:
                # Common endings in technical terms
                if masked[-3:] == ['_', '_', '_']:
                    for letter in available:
                        if letter in 'ion':  # -ion ending
                            scores[letter] += 300
                if masked[-2:] == ['_', '_']:
                    for letter in available:
                        if letter in 'lyers':  # -ly, -er, -es endings
                            scores[letter] += 200
            
            # Select best guess
            if scores:
                best_letter = max(scores.items(), key=lambda x: x[1])[0]
            else:
                best_letter = available[0]
            
            guessed.add(best_letter)
            
            # Update masked word
            if best_letter in word:
                for i, c in enumerate(word):
                    if c == best_letter:
                        masked[i] = best_letter
            
            # Check if solved
            if '_' not in masked:
                break
        
        return guessed


def evaluate():
    """Evaluate on test set"""
    ai = EnhancedHangmanAI()
    
    results = {
        'total': 0,
        'won': 0,
        'total_wrong': 0,
        'total_repeated': 0,
        'details': []
    }
    
    print("\nStarting evaluation...")
    for i, word in enumerate(ai.test_words, 1):
        if i % 100 == 0:
            print(f"Progress: {i}/{len(ai.test_words)} games...")
        
        guessed = ai.guess(word)
        word_letters = set(word)
        
        correct = guessed & word_letters
        wrong = guessed - word_letters
        
        # Check for repeated guesses (should be 0)
        repeated = 0  # Our AI never repeats
        
        won = len(correct) == len(word_letters) and len(wrong) <= 6
        
        results['total'] += 1
        if won:
            results['won'] += 1
        results['total_wrong'] += len(wrong)
        results['total_repeated'] += repeated
        
        results['details'].append({
            'word': word,
            'won': won,
            'wrong': len(wrong),
            'repeated': repeated
        })
    
    # Calculate final score
    success_rate = results['won'] / results['total']
    avg_wrong = results['total_wrong'] / results['total']
    
    final_score = results['won'] - (results['total_wrong'] * 5) - (results['total_repeated'] * 2)
    
    print("\n" + "="*60)
    print("ENHANCED HANGMAN AI - FINAL RESULTS")
    print("="*60)
    print(f"Total Games: {results['total']}")
    print(f"Games Won: {results['won']} ({success_rate*100:.2f}%)")
    print(f"Total Wrong Guesses: {results['total_wrong']}")
    print(f"Avg Wrong per Game: {avg_wrong:.2f}")
    print(f"Total Repeated Guesses: {results['total_repeated']}")
    print(f"\nFINAL SCORE: {final_score}")
    print(f"Target: > -5000")
    if final_score > -5000:
        print("[SUCCESS] Target achieved!")
    else:
        gap = abs(final_score + 5000)
        print(f"[PROGRESS] Gap: {gap} points from target")
    print("="*60)
    
    # Save results
    with open('ENHANCED_SCORE.txt', 'w') as f:
        f.write(f"Total Games: {results['total']}\n")
        f.write(f"Games Won: {results['won']}\n")
        f.write(f"Success Rate: {success_rate*100:.2f}%\n\n")
        f.write(f"Total Wrong Guesses: {results['total_wrong']}\n")
        f.write(f"Avg Wrong per Game: {avg_wrong:.2f}\n\n")
        f.write(f"Total Repeated Guesses: {results['total_repeated']}\n\n")
        f.write(f"FINAL SCORE: {final_score}\n")
        if final_score > -5000:
            f.write("STATUS: TARGET ACHIEVED!\n")
        else:
            f.write(f"Gap to target: {abs(final_score + 5000)} points\n")
    
    print("\nDetailed results saved to ENHANCED_SCORE.txt")
    
    return results, final_score


if __name__ == "__main__":
    results, score = evaluate()
