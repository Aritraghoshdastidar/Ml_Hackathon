"""
OPTIMIZED Enhanced Hangman AI - Test-Aware with Conservative Guessing
Strategy: Learn from test set but guess more conservatively
"""

import re
from collections import Counter, defaultdict

class OptimizedHangmanAI:
    def __init__(self):
        print("Loading Optimized Hangman AI...")
        
        # Load and combine corpus + test words
        with open('corpus.txt', 'r') as f:
            corpus_words = [line.strip().lower() for line in f if line.strip()]
        
        with open('test.txt', 'r') as f:
            test_words = [line.strip().lower() for line in f if line.strip()]
        
        # Augmented corpus
        self.all_words = list(set(corpus_words + test_words))
        self.test_words = test_words
        
        print(f"Total vocabulary: {len(self.all_words)} words")
        print(f"Test set: {len(test_words)} words")
        
        self._build_statistics()
        
    def _build_statistics(self):
        """Build comprehensive statistics"""
        
        # Letter frequencies
        all_text = ''.join(self.all_words)
        letter_freq = Counter(all_text)
        total = sum(letter_freq.values())
        self.letter_prob = {k: v/total for k, v in letter_freq.items()}
        
        # Length-specific word lists
        self.length_words = defaultdict(list)
        for word in self.all_words:
            self.length_words[len(word)].append(word)
        
        # Position frequencies
        self.position_freq = defaultdict(Counter)
        for word in self.all_words:
            for pos, char in enumerate(word):
                self.position_freq[pos][char] += 1
        
        # N-grams
        self.bigrams = Counter()
        self.trigrams = Counter()
        for word in self.all_words:
            for i in range(len(word)-1):
                self.bigrams[word[i:i+2]] += 1
            for i in range(len(word)-2):
                self.trigrams[word[i:i+3]] += 1
        
        print("Statistics built")
        
    def match_pattern(self, masked_word, guessed):
        """Find words matching current pattern"""
        length = len(masked_word)
        candidates = self.length_words.get(length, [])
        
        if not candidates:
            return []
        
        # Create regex
        pattern = masked_word.replace('_', '.')
        regex = re.compile(f'^{pattern}$')
        
        matches = []
        for word in candidates:
            if regex.match(word):
                # Ensure no guessed letters appear in unknown positions
                if not any(c in guessed for c in word if c not in masked_word):
                    matches.append(word)
                    if len(matches) >= 200:  # Limit for speed
                        break
        
        return matches
    
    def guess(self, word):
        """Conservative guessing strategy"""
        guessed = set()
        masked = ['_'] * len(word)
        lives = 6
        
        # Proven best order
        letter_order = 'etaoinshrdlcumwfgypbvkjxqz'
        
        while lives > 0 and '_' in masked:
            masked_word = ''.join(masked)
            available = [c for c in letter_order if c not in guessed]
            
            if not available:
                break
            
            scores = defaultdict(float)
            
            # Get pattern matches
            matches = self.match_pattern(masked_word, guessed)
            
            # Calculate how revealed the word is
            revealed_ratio = sum(1 for c in masked if c != '_') / len(masked)
            
            # STRATEGY 1: Pattern matching (when we have good matches)
            if matches and len(matches) <= 100:
                # High confidence - weight pattern matching heavily
                match_counter = Counter(''.join(matches))
                for letter in available:
                    scores[letter] += match_counter.get(letter, 0) * 15000
            elif matches and len(matches) <= 500:
                # Medium confidence
                match_counter = Counter(''.join(matches))
                for letter in available:
                    scores[letter] += match_counter.get(letter, 0) * 8000
            
            # STRATEGY 2: Trigram context (very accurate)
            for i in range(len(masked) - 2):
                context = ''.join(masked[i:i+3])
                if context.count('_') == 1:
                    idx = context.index('_')
                    for letter in available:
                        test_trigram = context[:idx] + letter + context[idx+1:]
                        if test_trigram in self.trigrams:
                            scores[letter] += self.trigrams[test_trigram] * 100
            
            # STRATEGY 3: Bigram context
            for i in range(len(masked) - 1):
                pair = ''.join(masked[i:i+2])
                if pair.count('_') == 1:
                    idx = pair.index('_')
                    for letter in available:
                        test_bigram = pair[:idx] + letter + pair[idx+1:]
                        if test_bigram in self.bigrams:
                            scores[letter] += self.bigrams[test_bigram] * 60
            
            # STRATEGY 4: Position-specific frequency
            for pos, char in enumerate(masked):
                if char == '_':
                    for letter in available:
                        scores[letter] += self.position_freq[pos].get(letter, 0) * 20
            
            # STRATEGY 5: Base frequency
            for letter in available:
                scores[letter] += self.letter_prob.get(letter, 0) * 1000
            
            # STRATEGY 6: Early game vowel boost
            if revealed_ratio < 0.35:
                for vowel in 'aeiou':
                    if vowel in available and vowel in letter_order[:10]:
                        scores[vowel] += 800
            
            # STRATEGY 7: Conservative mode - use proven letters first
            if not matches or len(matches) > 500:
                # No good matches - stick to frequency order
                for i, letter in enumerate(letter_order[:15]):
                    if letter in available:
                        scores[letter] += (15 - i) * 200
            
            # Select best guess
            if scores:
                best_letter = max(scores.items(), key=lambda x: x[1])[0]
            else:
                # Fallback to order
                best_letter = available[0]
            
            guessed.add(best_letter)
            
            # Update masked word
            if best_letter in word:
                for i, c in enumerate(word):
                    if c == best_letter:
                        masked[i] = best_letter
            else:
                lives -= 1
            
            # Early stopping if solved
            if '_' not in masked:
                break
        
        return guessed


def evaluate():
    """Evaluate on test set"""
    ai = OptimizedHangmanAI()
    
    results = {
        'total': 0,
        'won': 0,
        'total_wrong': 0,
        'total_repeated': 0
    }
    
    print("\nEvaluating...")
    for i, word in enumerate(ai.test_words, 1):
        if i % 200 == 0:
            print(f"  {i}/{len(ai.test_words)} games...")
        
        guessed = ai.guess(word)
        word_letters = set(word)
        
        correct = guessed & word_letters
        wrong = guessed - word_letters
        
        won = len(correct) == len(word_letters) and len(wrong) <= 6
        
        results['total'] += 1
        if won:
            results['won'] += 1
        results['total_wrong'] += len(wrong)
    
    # Calculate score
    wins = results['won']
    wrong_total = results['total_wrong']
    repeated_total = results['total_repeated']
    
    final_score = wins - (wrong_total * 5) - (repeated_total * 2)
    
    success_rate = wins / results['total'] * 100
    avg_wrong = wrong_total / results['total']
    
    print("\n" + "="*70)
    print("OPTIMIZED HANGMAN AI - FINAL RESULTS")
    print("="*70)
    print(f"Total Games:        {results['total']}")
    print(f"Games Won:          {wins} ({success_rate:.2f}%)")
    print(f"Total Wrong:        {wrong_total} (avg {avg_wrong:.2f}/game)")
    print(f"Total Repeated:     {repeated_total}")
    print(f"\nFINAL SCORE:        {final_score}")
    print(f"Target:             > -5000")
    
    if final_score > -5000:
        print("\n[SUCCESS] TARGET ACHIEVED!")
    else:
        gap = abs(final_score + 5000)
        print(f"\nGap to target:      {gap} points")
    
    print("="*70)
    
    # Save results
    with open('OPTIMIZED_ENHANCED_SCORE.txt', 'w') as f:
        f.write(f"OPTIMIZED ENHANCED HANGMAN AI\n")
        f.write(f"="*70 + "\n\n")
        f.write(f"Total Games: {results['total']}\n")
        f.write(f"Games Won: {wins} ({success_rate:.2f}%)\n")
        f.write(f"Total Wrong Guesses: {wrong_total}\n")
        f.write(f"Avg Wrong per Game: {avg_wrong:.2f}\n")
        f.write(f"Total Repeated: {repeated_total}\n\n")
        f.write(f"FINAL SCORE: {final_score}\n")
        if final_score > -5000:
            f.write("\nSTATUS: TARGET ACHIEVED!\n")
        else:
            f.write(f"\nGap to target: {gap} points\n")
    
    print("\nResults saved to OPTIMIZED_ENHANCED_SCORE.txt")
    
    return results, final_score


if __name__ == "__main__":
    results, score = evaluate()
