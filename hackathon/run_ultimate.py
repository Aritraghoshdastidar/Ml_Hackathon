"""
ULTIMATE Hangman AI - Designed to MAXIMIZE SCORE
Strategy: Win as many as possible with minimal wrong guesses
Target: Score > -5000 (ideally -3000 to -1000)
"""

import numpy as np
from collections import Counter, defaultdict
import random
import re
from tqdm import tqdm
import string

np.random.seed(42)
random.seed(42)

print("="*70)
print("ULTIMATE HANGMAN AI - MAXIMUM SCORE OPTIMIZER")
print("="*70)

with open('corpus.txt', 'r') as f:
    corpus_words = [line.strip().lower() for line in f.readlines()]

with open('test.txt', 'r') as f:
    test_words = [line.strip().lower() for line in f.readlines()]

print(f"Loaded {len(corpus_words)} corpus, {len(test_words)} test words")

class UltimateAgent:
    """Ultimate agent with sophisticated multi-strategy approach"""
    
    def __init__(self, word_list):
        self.dictionary = word_list
        self.dict_by_length = defaultdict(list)
        
        for word in word_list:
            self.dict_by_length[len(word)].append(word)
        
        # Letter frequency by position and overall
        self.letter_freq = Counter(''.join(word_list))
        
        # Position-specific
        self.pos_freq = {}
        for length, words in self.dict_by_length.items():
            self.pos_freq[length] = [Counter() for _ in range(length)]
            for word in words:
                for pos, letter in enumerate(word):
                    self.pos_freq[length][pos][letter] += 1
        
        # N-grams
        self.bigrams = Counter()
        self.trigrams = Counter()
        for word in word_list:
            for i in range(len(word)-1):
                self.bigrams[(word[i], word[i+1])] += 1
            for i in range(len(word)-2):
                self.trigrams[(word[i], word[i+1], word[i+2])] += 1
        
        # The ULTIMATE frequency list (tested order)
        # This ordering is optimized for English words
        self.ultimate_order = [
            'e', 'a', 'i', 'o', 'r',  # Top vowels and R
            'n', 't', 's', 'l', 'c',  # Common consonants
            'd', 'u', 'm', 'p', 'h',  # Secondary frequency
            'g', 'b', 'f', 'y', 'w',  # Tertiary
            'k', 'v', 'x', 'z', 'j', 'q'  # Rare letters
        ]
        
        print(f"Agent ready with {len(self.dict_by_length)} length models")
    
    def get_matches(self, masked_word, guessed_letters):
        """Get matching words from dictionary"""
        length = len(masked_word)
        if length not in self.dict_by_length:
            return []
        
        pattern = '^' + masked_word.replace('_', '.') + '$'
        try:
            regex = re.compile(pattern)
        except:
            return []
        
        wrong_letters = guessed_letters - set(masked_word.replace('_', ''))
        
        matches = []
        for word in self.dict_by_length[length]:
            if regex.match(word):
                if not wrong_letters.intersection(set(word)):
                    matches.append(word)
        
        return matches
    
    def guess_letter(self, masked_word, guessed_letters):
        """Ultimate guessing strategy"""
        
        length = len(masked_word)
        available = set(string.ascii_lowercase) - guessed_letters
        
        if not available:
            return None
        
        num_guessed = len(guessed_letters)
        num_revealed = sum(1 for c in masked_word if c != '_')
        percent_revealed = num_revealed / length if length > 0 else 0
        
        letter_scores = defaultdict(float)
        
        # === PHASE 1: Early game (0-2 guesses) - Use proven best letters ===
        if num_guessed < 3:
            # Start with the absolute best letters in order
            for letter in ['e', 'a', 'i', 'o', 'r']:
                if letter in available:
                    letter_scores[letter] += 10000
        
        # === PHASE 2: Find pattern matches ===
        matches = self.get_matches(masked_word, guessed_letters)
        
        if matches and len(matches) <= 1000:
            # Count letters in blank positions only
            for word in matches:
                unique_letters = set()
                for i, char in enumerate(masked_word):
                    if char == '_' and word[i] in available:
                        unique_letters.add(word[i])
                for letter in unique_letters:
                    letter_scores[letter] += 500
        
        # === PHASE 3: Use all context clues ===
        
        # Trigrams (strongest context)
        for i in range(len(masked_word) - 2):
            p = [masked_word[i], masked_word[i+1], masked_word[i+2]]
            
            if p[0] == '_' and p[1] != '_' and p[2] != '_':
                for letter in available:
                    letter_scores[letter] += self.trigrams.get((letter, p[1], p[2]), 0) * 20
            
            if p[0] != '_' and p[1] == '_' and p[2] != '_':
                for letter in available:
                    letter_scores[letter] += self.trigrams.get((p[0], letter, p[2]), 0) * 20
            
            if p[0] != '_' and p[1] != '_' and p[2] == '_':
                for letter in available:
                    letter_scores[letter] += self.trigrams.get((p[0], p[1], letter), 0) * 20
        
        # Bigrams (strong context)
        for pos, char in enumerate(masked_word):
            if char != '_':
                if pos > 0 and masked_word[pos-1] == '_':
                    for letter in available:
                        letter_scores[letter] += self.bigrams.get((letter, char), 0) * 15
                
                if pos < length - 1 and masked_word[pos+1] == '_':
                    for letter in available:
                        letter_scores[letter] += self.bigrams.get((char, letter), 0) * 15
        
        # Position-specific frequencies
        if length in self.pos_freq:
            for pos, char in enumerate(masked_word):
                if char == '_':
                    for letter in available:
                        letter_scores[letter] += self.pos_freq[length][pos].get(letter, 0) * 5
        
        # Overall frequency (base score for all letters)
        for letter in available:
            letter_scores[letter] += self.letter_freq.get(letter, 0)
        
        # === PHASE 4: Vowel management ===
        # After first few guesses, if not many letters revealed, try more vowels
        if num_guessed >= 3 and percent_revealed < 0.4:
            for vowel in ['u', 'o', 'i']:  # Try less common vowels
                if vowel in available:
                    letter_scores[vowel] += 3000
        
        # === PHASE 5: Choose best letter ===
        if letter_scores:
            return max(letter_scores.items(), key=lambda x: x[1])[0]
        
        # Emergency fallback: use ultimate order
        for letter in self.ultimate_order:
            if letter in available:
                return letter
        
        return list(available)[0] if available else None

class HangmanGame:
    def __init__(self, word, max_lives=6):
        self.word = word.lower()
        self.max_lives = max_lives
        self.reset()
    
    def reset(self):
        self.lives = self.max_lives
        self.guessed = set()
        self.correct = set()
        self.wrong_count = 0
        self.repeated_count = 0
        self.done = False
        self.won = False
    
    def get_masked(self):
        return ''.join([c if c in self.correct else '_' for c in self.word])
    
    def guess(self, letter):
        letter = letter.lower()
        
        if letter in self.guessed:
            self.repeated_count += 1
            return False, "repeated"
        
        self.guessed.add(letter)
        
        if letter in self.word:
            self.correct.add(letter)
            if set(self.word) == self.correct:
                self.done = True
                self.won = True
            return True, "correct"
        else:
            self.wrong_count += 1
            self.lives -= 1
            if self.lives == 0:
                self.done = True
                self.won = False
            return False, "wrong"
    
    def get_stats(self):
        return {
            'won': self.won,
            'wrong_guesses': self.wrong_count,
            'repeated_guesses': self.repeated_count
        }

def play_game(agent, word):
    game = HangmanGame(word)
    
    while not game.done:
        masked = game.get_masked()
        guess = agent.guess_letter(masked, game.guessed)
        
        if guess is None:
            break
        
        game.guess(guess)
    
    return game.get_stats()

def evaluate(agent, test_words):
    print(f"\nEvaluating on {len(test_words)} games...")
    
    wins = 0
    total_wrong = 0
    total_repeated = 0
    results = []
    
    for word in tqdm(test_words, desc="Playing"):
        stats = play_game(agent, word)
        
        if stats['won']:
            wins += 1
        
        total_wrong += stats['wrong_guesses']
        total_repeated += stats['repeated_guesses']
        
        results.append({
            'word': word,
            'won': stats['won'],
            'wrong': stats['wrong_guesses'],
            'repeated': stats['repeated_guesses']
        })
    
    success_rate = wins / len(test_words)
    final_score = (success_rate * len(test_words)) - (total_wrong * 5) - (total_repeated * 2)
    
    return {
        'total': len(test_words),
        'wins': wins,
        'losses': len(test_words) - wins,
        'success_rate': success_rate,
        'total_wrong': total_wrong,
        'total_repeated': total_repeated,
        'avg_wrong': total_wrong / len(test_words),
        'avg_repeated': total_repeated / len(test_words),
        'final_score': final_score,
        'results': results
    }

if __name__ == "__main__":
    print("\n" + "="*70)
    print("INITIALIZING ULTIMATE AGENT")
    print("="*70)
    
    agent = UltimateAgent(corpus_words)
    
    results = evaluate(agent, test_words)
    
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"Total Games:          {results['total']}")
    print(f"Wins:                 {results['wins']}")
    print(f"Losses:               {results['losses']}")
    print(f"Success Rate:         {results['success_rate']*100:.2f}%")
    print(f"")
    print(f"Total Wrong:          {results['total_wrong']}")
    print(f"Avg Wrong/Game:       {results['avg_wrong']:.2f}")
    print(f"")
    print(f"Total Repeated:       {results['total_repeated']}")
    print(f"Avg Repeated/Game:    {results['avg_repeated']:.2f}")
    print("="*70)
    print(f"FINAL SCORE:          {results['final_score']:.2f}")
    print("="*70)
    
    success_pts = results['success_rate'] * results['total']
    wrong_penalty = results['total_wrong'] * 5
    repeated_penalty = results['total_repeated'] * 2
    
    print(f"\nScore Breakdown:")
    print(f"  Wins ({results['wins']}/{results['total']}):  +{success_pts:.0f}")
    print(f"  Wrong guesses:                  -{wrong_penalty:.0f}")
    print(f"  Repeated guesses:               -{repeated_penalty:.0f}")
    print(f"  " + "-"*40)
    print(f"  TOTAL:                          {results['final_score']:.0f}")
    
    if results['final_score'] > -5000:
        print(f"\n*** SUCCESS! Score {results['final_score']:.0f} > -5000 ***")
    else:
        gap = abs(results['final_score'] + 5000)
        print(f"\nGap to -5000: {gap:.0f} points")
        print(f"Need {gap/(results['total']):.2f} more points per game")
        print(f"OR win {gap:.0f} more games")
        print(f"OR reduce wrong guesses by {gap/5:.0f}")
    
    # Save
    with open('evaluation_ultimate.txt', 'w') as f:
        f.write(f"ULTIMATE HANGMAN AI RESULTS\\n")
        f.write(f"==========================\\n\\n")
        f.write(f"Total Games: {results['total']}\\n")
        f.write(f"Wins: {results['wins']}\\n")
        f.write(f"Success Rate: {results['success_rate']*100:.2f}%\\n\\n")
        f.write(f"Wrong Guesses: {results['total_wrong']} (avg {results['avg_wrong']:.2f})\\n")
        f.write(f"Repeated: {results['total_repeated']} (avg {results['avg_repeated']:.2f})\\n\\n")
        f.write(f"FINAL SCORE: {results['final_score']:.2f}\\n")
    
    # Analysis by word length
    by_length = defaultdict(lambda: {'won': 0, 'total': 0, 'wrong': 0})
    for r in results['results']:
        length = len(r['word'])
        by_length[length]['total'] += 1
        if r['won']:
            by_length[length]['won'] += 1
        by_length[length]['wrong'] += r['wrong']
    
    print(f"\nPerformance by word length:")
    for length in sorted(by_length.keys()):
        data = by_length[length]
        win_rate = (data['won'] / data['total']) * 100
        avg_wrong = data['wrong'] / data['total']
        print(f"  Length {length:2d}: {data['won']:3d}/{data['total']:3d} wins ({win_rate:5.1f}%), avg wrong: {avg_wrong:.2f}")
    
    print("\nResults saved to evaluation_ultimate.txt")
    print("="*70)
