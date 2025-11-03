"""
Hangman AI Agent - FINAL OPTIMIZED VERSION
Hybrid strategy for maximum performance on UNSEEN words
"""

import numpy as np
from collections import Counter
import random
import re
from tqdm import tqdm
import string

np.random.seed(42)
random.seed(42)

print("="*70)
print("HANGMAN AI - FINAL OPTIMIZED VERSION")
print("="*70)

# Load data
with open('corpus.txt', 'r') as f:
    corpus_words = [line.strip().lower() for line in f.readlines()]

with open('test.txt', 'r') as f:
    test_words = [line.strip().lower() for line in f.readlines()]

print(f"Loaded {len(corpus_words)} corpus words")
print(f"Loaded {len(test_words)} test words")

class HybridHangmanAgent:
    """Hybrid agent: smart frequency + pattern matching + context"""
    
    def __init__(self, word_list):
        self.dictionary = word_list
        self.dict_by_length = {}
        
        # Organize by length
        for word in word_list:
            length = len(word)
            if length not in self.dict_by_length:
                self.dict_by_length[length] = []
            self.dict_by_length[length].append(word)
        
        # Calculate letter frequencies
        self.overall_freq = Counter(''.join(word_list))
        
        # Position-based frequencies for each length
        self.position_freq = {}
        for length, words in self.dict_by_length.items():
            self.position_freq[length] = [Counter() for _ in range(length)]
            for word in words:
                for pos, letter in enumerate(word):
                    self.position_freq[length][pos][letter] += 1
        
        # Common starting letters
        self.start_letters = Counter([w[0] for w in word_list if w])
        
        # Common ending letters
        self.end_letters = Counter([w[-1] for w in word_list if w])
        
        # Bigram frequencies
        self.bigrams = Counter()
        for word in word_list:
            for i in range(len(word)-1):
                self.bigrams[(word[i], word[i+1])] += 1
        
        print(f"Agent trained on corpus")
        print(f"  - {len(self.dict_by_length)} different word lengths")
        print(f"  - Top 5 letters: {[l for l, c in self.overall_freq.most_common(5)]}")
    
    def get_pattern_matches(self, masked_word, guessed_letters):
        """Find words matching pattern"""
        length = len(masked_word)
        if length not in self.dict_by_length:
            return []
        
        pattern = masked_word.replace('_', '.')
        regex = re.compile(f'^{pattern}$')
        
        wrong_letters = guessed_letters - set(masked_word.replace('_', ''))
        
        matches = []
        for word in self.dict_by_length[length]:
            if regex.match(word):
                if not any(letter in word for letter in wrong_letters):
                    matches.append(word)
        
        return matches
    
    def guess_letter(self, masked_word, guessed_letters):
        """Choose best letter using hybrid strategy"""
        
        available = set(string.ascii_lowercase) - guessed_letters
        if not available:
            return None
        
        length = len(masked_word)
        letter_scores = Counter()
        
        # Strategy 1: Pattern matching (if we have matches)
        matches = self.get_pattern_matches(masked_word, guessed_letters)
        
        if matches and len(matches) < 100:  # Only use if reasonably specific
            for word in matches:
                for i, char in enumerate(masked_word):
                    if char == '_' and word[i] in available:
                        letter_scores[word[i]] += 50  # High weight
        
        # Strategy 2: Position-specific frequencies
        if length in self.position_freq:
            for pos, char in enumerate(masked_word):
                if char == '_':
                    for letter in available:
                        letter_scores[letter] += self.position_freq[length][pos].get(letter, 0) * 3
        
        # Strategy 3: Bigram context
        for pos, char in enumerate(masked_word):
            if char != '_':
                # Check left position
                if pos > 0 and masked_word[pos-1] == '_':
                    for letter in available:
                        letter_scores[letter] += self.bigrams.get((letter, char), 0) * 5
                
                # Check right position
                if pos < length - 1 and masked_word[pos+1] == '_':
                    for letter in available:
                        letter_scores[letter] += self.bigrams.get((char, letter), 0) * 5
        
        # Strategy 4: Start/end position boost
        if masked_word[0] == '_':
            for letter in available:
                letter_scores[letter] += self.start_letters.get(letter, 0) * 2
        
        if masked_word[-1] == '_':
            for letter in available:
                letter_scores[letter] += self.end_letters.get(letter, 0) * 2
        
        # Strategy 5: Overall frequency (always include)
        for letter in available:
            letter_scores[letter] += self.overall_freq.get(letter, 1)
        
        # Strategy 6: Vowel priority early on
        num_guessed = len(guessed_letters)
        if num_guessed < 3:
            vowels = set('aeiou') & available
            for vowel in vowels:
                letter_scores[vowel] += 1000  # Strong boost for early vowels
        
        # Choose best letter
        if letter_scores:
            return letter_scores.most_common(1)[0][0]
        
        # Fallback: most common overall
        return max(available, key=lambda x: self.overall_freq.get(x, 0))

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
    print("\n" + "="*70)
    print(f"EVALUATING ON {len(test_words)} TEST GAMES")
    print("="*70)
    
    wins = 0
    total_wrong = 0
    total_repeated = 0
    
    for word in tqdm(test_words, desc="Playing"):
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
    print("INITIALIZING AGENT")
    print("="*70)
    
    agent = HybridHangmanAgent(corpus_words)
    
    # Evaluate
    results = evaluate(agent, test_words)
    
    # Print results
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"Total Games:              {results['total_games']}")
    print(f"Wins:                     {results['wins']}")
    print(f"Success Rate:             {results['success_rate']*100:.2f}%")
    print(f"Total Wrong Guesses:      {results['total_wrong']}")
    print(f"Total Repeated Guesses:   {results['total_repeated']}")
    print(f"Avg Wrong per Game:       {results['avg_wrong']:.2f}")
    print(f"Avg Repeated per Game:    {results['avg_repeated']:.2f}")
    print("="*70)
    print(f"FINAL SCORE:              {results['final_score']:.2f}")
    print("="*70)
    
    print("\nScore Breakdown:")
    print(f"  Success Points:    {results['success_rate'] * results['total_games']:.2f}")
    print(f"  Wrong Penalty:     -{results['total_wrong'] * 5:.2f}")
    print(f"  Repeated Penalty:  -{results['total_repeated'] * 2:.2f}")
    
    if results['final_score'] < -5000:
        print("\n[SUCCESS] Score < -5000 TARGET ACHIEVED!")
    else:
        print(f"\n[INFO] Score is {results['final_score']:.2f}")
    
    # Save
    with open('evaluation_final.txt', 'w') as f:
        f.write(f"FINAL HANGMAN AI EVALUATION\\n")
        f.write(f"===========================\\n\\n")
        f.write(f"Total Games: {results['total_games']}\\n")
        f.write(f"Games Won: {results['wins']}\\n")
        f.write(f"Success Rate: {results['success_rate']*100:.2f}%\\n\\n")
        f.write(f"Total Wrong Guesses: {results['total_wrong']}\\n")
        f.write(f"Avg Wrong per Game: {results['avg_wrong']:.2f}\\n\\n")
        f.write(f"Total Repeated Guesses: {results['total_repeated']}\\n")
        f.write(f"Avg Repeated per Game: {results['avg_repeated']:.2f}\\n\\n")
        f.write(f"FINAL SCORE: {results['final_score']:.2f}\\n")
    
    print("\nResults saved to evaluation_final.txt")
    print("="*70)
