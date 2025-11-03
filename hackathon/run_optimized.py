"""
Hangman AI Agent - OPTIMIZED FOR HIGH SCORE (> -5000)
Goal: Maximize wins, minimize wrong guesses
Target: Score between -5000 and 0 (higher is better!)
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
print("HANGMAN AI - OPTIMIZED FOR HIGH SCORE")
print("Goal: Win rate > 70%, Score > -5000")
print("="*70)

# Load data
with open('corpus.txt', 'r') as f:
    corpus_words = [line.strip().lower() for line in f.readlines()]

with open('test.txt', 'r') as f:
    test_words = [line.strip().lower() for line in f.readlines()]

print(f"Loaded {len(corpus_words)} corpus words")
print(f"Loaded {len(test_words)} test words")

class OptimizedHangmanAgent:
    """Optimized agent for maximum wins and minimum wrong guesses"""
    
    def __init__(self, word_list):
        self.dictionary = word_list
        self.dict_by_length = defaultdict(list)
        
        # Organize by length
        for word in word_list:
            self.dict_by_length[len(word)].append(word)
        
        # Overall letter frequency (sorted by popularity)
        self.letter_freq = Counter(''.join(word_list))
        self.sorted_letters = [letter for letter, count in self.letter_freq.most_common()]
        
        # Position-specific frequencies
        self.position_freq = {}
        for length, words in self.dict_by_length.items():
            self.position_freq[length] = [Counter() for _ in range(length)]
            for word in words:
                for pos, letter in enumerate(word):
                    self.position_freq[length][pos][letter] += 1
        
        # Bigrams for context
        self.bigrams = Counter()
        for word in word_list:
            for i in range(len(word)-1):
                self.bigrams[(word[i], word[i+1])] += 1
        
        # Trigrams for better context
        self.trigrams = Counter()
        for word in word_list:
            for i in range(len(word)-2):
                self.trigrams[(word[i], word[i+1], word[i+2])] += 1
        
        # Common patterns
        self.pattern_freq = defaultdict(Counter)
        for word in word_list:
            length = len(word)
            # Store first and last letters
            if length >= 2:
                self.pattern_freq[f"start_{length}"][word[0]] += 1
                self.pattern_freq[f"end_{length}"][word[-1]] += 1
            # Store common endings
            if length >= 3:
                self.pattern_freq[f"end3_{length}"][word[-3:]] += 1
            if length >= 2:
                self.pattern_freq[f"end2_{length}"][word[-2:]] += 1
        
        print(f"Agent initialized:")
        print(f"  - {len(self.dict_by_length)} word lengths")
        print(f"  - Top 10 letters: {self.sorted_letters[:10]}")
        print(f"  - Most common starting letters: {[l for l, c in Counter([w[0] for w in word_list]).most_common(5)]}")
    
    def get_matching_words(self, masked_word, guessed_letters):
        """Find corpus words matching the pattern"""
        length = len(masked_word)
        if length not in self.dict_by_length:
            return []
        
        # Build regex
        pattern = ''
        for char in masked_word:
            pattern += char if char != '_' else '.'
        
        try:
            regex = re.compile(f'^{pattern}$')
        except:
            return []
        
        # Filter out wrong letters
        wrong_letters = guessed_letters - set(masked_word.replace('_', ''))
        
        matches = []
        for word in self.dict_by_length[length]:
            if regex.match(word):
                # Ensure word doesn't contain any wrong letters
                if not wrong_letters.intersection(set(word)):
                    matches.append(word)
        
        return matches
    
    def score_letters(self, masked_word, guessed_letters, matches):
        """Score each available letter using multiple strategies"""
        
        length = len(masked_word)
        available = set(string.ascii_lowercase) - guessed_letters
        
        if not available:
            return {}
        
        scores = defaultdict(float)
        
        # === STRATEGY 1: Pattern Matching (HIGHEST PRIORITY) ===
        if matches and len(matches) <= 500:  # If we have specific matches
            letter_counts = Counter()
            for word in matches:
                # Only count letters in blank positions
                for i, char in enumerate(masked_word):
                    if char == '_' and word[i] in available:
                        letter_counts[word[i]] += 1
            
            # Heavy weight for pattern matches
            for letter, count in letter_counts.items():
                scores[letter] += count * 1000
        
        # === STRATEGY 2: Trigram Context (VERY HIGH PRIORITY) ===
        for i in range(len(masked_word) - 2):
            pattern = [masked_word[i], masked_word[i+1], masked_word[i+2]]
            
            # Pattern: _XX
            if pattern[0] == '_' and pattern[1] != '_' and pattern[2] != '_':
                for letter in available:
                    scores[letter] += self.trigrams.get((letter, pattern[1], pattern[2]), 0) * 50
            
            # Pattern: X_X
            elif pattern[0] != '_' and pattern[1] == '_' and pattern[2] != '_':
                for letter in available:
                    scores[letter] += self.trigrams.get((pattern[0], letter, pattern[2]), 0) * 50
            
            # Pattern: XX_
            elif pattern[0] != '_' and pattern[1] != '_' and pattern[2] == '_':
                for letter in available:
                    scores[letter] += self.trigrams.get((pattern[0], pattern[1], letter), 0) * 50
        
        # === STRATEGY 3: Bigram Context (HIGH PRIORITY) ===
        for pos, char in enumerate(masked_word):
            if char != '_':
                # Left context
                if pos > 0 and masked_word[pos-1] == '_':
                    for letter in available:
                        scores[letter] += self.bigrams.get((letter, char), 0) * 30
                
                # Right context
                if pos < length - 1 and masked_word[pos+1] == '_':
                    for letter in available:
                        scores[letter] += self.bigrams.get((char, letter), 0) * 30
        
        # === STRATEGY 4: Position-Specific Frequencies (MEDIUM PRIORITY) ===
        if length in self.position_freq:
            for pos, char in enumerate(masked_word):
                if char == '_':
                    for letter in available:
                        scores[letter] += self.position_freq[length][pos].get(letter, 0) * 10
        
        # === STRATEGY 5: Common Endings (MEDIUM PRIORITY) ===
        revealed_end = ''
        for i in range(length-1, -1, -1):
            if masked_word[i] != '_':
                revealed_end = masked_word[i] + revealed_end
            else:
                break
        
        if revealed_end:
            # Check what commonly comes before this ending
            if length >= 2 and masked_word[-1] != '_':
                for letter in available:
                    test_end = letter + revealed_end[-1]
                    scores[letter] += self.pattern_freq[f"end2_{length}"].get(test_end, 0) * 20
        
        # === STRATEGY 6: Common Starting Letters (MEDIUM PRIORITY) ===
        if masked_word[0] == '_':
            for letter in available:
                scores[letter] += self.pattern_freq[f"start_{length}"].get(letter, 0) * 20
        
        # === STRATEGY 7: Overall Frequency (BASE PRIORITY) ===
        for letter in available:
            scores[letter] += self.letter_freq.get(letter, 0) * 1
        
        # === STRATEGY 8: Vowel Boost Early Game (CONDITIONAL) ===
        num_guessed = len(guessed_letters)
        num_revealed = len([c for c in masked_word if c != '_'])
        
        # First 2 guesses: prioritize most common vowels
        if num_guessed < 2:
            for vowel in ['e', 'a', 'i', 'o']:
                if vowel in available:
                    scores[vowel] += 5000
        
        # If we have few letters revealed, boost remaining vowels
        elif num_revealed < length * 0.3:
            for vowel in ['e', 'a', 'i', 'o', 'u']:
                if vowel in available:
                    scores[vowel] += 2000
        
        return scores
    
    def guess_letter(self, masked_word, guessed_letters):
        """Choose the best letter to guess"""
        
        available = set(string.ascii_lowercase) - guessed_letters
        if not available:
            return None
        
        # Get matching words
        matches = self.get_matching_words(masked_word, guessed_letters)
        
        # Score all letters
        scores = self.score_letters(masked_word, guessed_letters, matches)
        
        if not scores:
            # Emergency fallback: most common unguessed letter
            for letter in self.sorted_letters:
                if letter in available:
                    return letter
            return list(available)[0]
        
        # Return highest scoring letter
        best_letter = max(scores.items(), key=lambda x: x[1])[0]
        return best_letter

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

def play_game(agent, word, verbose=False):
    game = HangmanGame(word)
    
    if verbose:
        print(f"\nPlaying: {word}")
    
    while not game.done:
        masked = game.get_masked()
        guess = agent.guess_letter(masked, game.guessed)
        
        if guess is None:
            break
        
        correct, result = game.guess(guess)
        
        if verbose:
            status = "[OK]" if correct else "[X]"
            print(f"  {status} Guess '{guess}': {masked} -> Lives: {game.lives}")
    
    if verbose:
        stats = game.get_stats()
        result_str = "WON" if stats['won'] else "LOST"
        print(f"  Result: {result_str} - Wrong: {stats['wrong_guesses']}, Repeated: {stats['repeated_guesses']}")
    
    return game.get_stats()

def evaluate(agent, test_words, show_samples=5):
    print("\n" + "="*70)
    print(f"EVALUATING ON {len(test_words)} TEST GAMES")
    print("="*70)
    
    # Show sample games
    if show_samples > 0:
        print(f"\nSample games (first {show_samples}):")
        samples = test_words[:show_samples]
        for word in samples:
            play_game(agent, word, verbose=True)
    
    print(f"\nPlaying all {len(test_words)} games...")
    
    wins = 0
    total_wrong = 0
    total_repeated = 0
    
    for word in tqdm(test_words, desc="Progress"):
        stats = play_game(agent, word)
        
        if stats['won']:
            wins += 1
        
        total_wrong += stats['wrong_guesses']
        total_repeated += stats['repeated_guesses']
    
    success_rate = wins / len(test_words)
    avg_wrong = total_wrong / len(test_words)
    avg_repeated = total_repeated / len(test_words)
    
    final_score = (success_rate * len(test_words)) - (total_wrong * 5) - (total_repeated * 2)
    
    return {
        'total_games': len(test_words),
        'wins': wins,
        'losses': len(test_words) - wins,
        'success_rate': success_rate,
        'total_wrong': total_wrong,
        'total_repeated': total_repeated,
        'avg_wrong': avg_wrong,
        'avg_repeated': avg_repeated,
        'final_score': final_score
    }

# Main
if __name__ == "__main__":
    print("\n" + "="*70)
    print("INITIALIZING OPTIMIZED AGENT")
    print("="*70)
    
    agent = OptimizedHangmanAgent(corpus_words)
    
    # Evaluate
    results = evaluate(agent, test_words, show_samples=5)
    
    # Print results
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"Total Games:              {results['total_games']}")
    print(f"Wins:                     {results['wins']}")
    print(f"Losses:                   {results['losses']}")
    print(f"Success Rate:             {results['success_rate']*100:.2f}%")
    print(f"")
    print(f"Total Wrong Guesses:      {results['total_wrong']}")
    print(f"Avg Wrong per Game:       {results['avg_wrong']:.2f}")
    print(f"")
    print(f"Total Repeated Guesses:   {results['total_repeated']}")
    print(f"Avg Repeated per Game:    {results['avg_repeated']:.2f}")
    print("="*70)
    print(f"FINAL SCORE:              {results['final_score']:.2f}")
    print("="*70)
    
    print("\nScore Breakdown:")
    success_points = results['success_rate'] * results['total_games']
    wrong_penalty = results['total_wrong'] * 5
    repeated_penalty = results['total_repeated'] * 2
    
    print(f"  Success Points:    +{success_points:.2f}")
    print(f"  Wrong Penalty:     -{wrong_penalty:.2f}")
    print(f"  Repeated Penalty:  -{repeated_penalty:.2f}")
    print(f"  --------------------------------")
    print(f"  TOTAL:             {results['final_score']:.2f}")
    
    if results['final_score'] > -5000:
        print(f"\n[SUCCESS!!!] Score {results['final_score']:.2f} is ABOVE -5000 target!")
        print(f"Target achieved! Score is better than -5000!")
    else:
        deficit = abs(results['final_score'] + 5000)
        print(f"\n[CLOSE] Score is {results['final_score']:.2f}")
        print(f"Need {deficit:.2f} more points to reach -5000")
        
        # Calculate what's needed
        needed_wins = deficit / results['total_games']
        print(f"Need approximately {needed_wins*100:.1f}% more win rate")
        print(f"OR reduce wrong guesses by {deficit/5:.0f} total")
    
    # Save
    with open('evaluation_optimized.txt', 'w') as f:
        f.write(f"OPTIMIZED HANGMAN AI EVALUATION\n")
        f.write(f"================================\n\n")
        f.write(f"Total Games: {results['total_games']}\n")
        f.write(f"Games Won: {results['wins']}\n")
        f.write(f"Games Lost: {results['losses']}\n")
        f.write(f"Success Rate: {results['success_rate']*100:.2f}%\n\n")
        f.write(f"Total Wrong Guesses: {results['total_wrong']}\n")
        f.write(f"Avg Wrong per Game: {results['avg_wrong']:.2f}\n\n")
        f.write(f"Total Repeated Guesses: {results['total_repeated']}\n")
        f.write(f"Avg Repeated per Game: {results['avg_repeated']:.2f}\n\n")
        f.write(f"FINAL SCORE: {results['final_score']:.2f}\n\n")
        f.write(f"Score Breakdown:\n")
        f.write(f"  Success Points: +{success_points:.2f}\n")
        f.write(f"  Wrong Penalty: -{wrong_penalty:.2f}\n")
        f.write(f"  Repeated Penalty: -{repeated_penalty:.2f}\n")
    
    print("\nResults saved to evaluation_optimized.txt")
    print("="*70)
