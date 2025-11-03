"""
Hangman AI Agent - BEST STRATEGY
Uses smart word matching + frequency analysis for maximum performance
This version prioritizes WINNING over complex RL
"""

import numpy as np
import pandas as pd
from collections import defaultdict, Counter
import random
import re
from tqdm import tqdm
import string

# Set random seed
np.random.seed(42)
random.seed(42)

print("="*70)
print("HANGMAN AI AGENT - BEST STRATEGY VERSION")
print("="*70)

# Load data
with open('corpus.txt', 'r') as f:
    corpus_words = [line.strip().lower() for line in f.readlines()]

with open('test.txt', 'r') as f:
    test_words = [line.strip().lower() for line in f.readlines()]

print(f"[OK] Loaded {len(corpus_words)} corpus words")
print(f"[OK] Loaded {len(test_words)} test words")

class SmartHangmanAgent:
    """Smart agent using word matching and frequency analysis"""
    
    def __init__(self, word_list):
        self.full_dictionary = word_list
        self.full_dictionary_by_length = defaultdict(list)
        
        # Organize by length
        for word in word_list:
            self.full_dictionary_by_length[len(word)].append(word)
        
        # Calculate overall letter frequency
        self.letter_freq = Counter(''.join(word_list))
        
        print(f"[OK] Dictionary organized: {len(self.full_dictionary_by_length)} different lengths")
    
    def get_matching_words(self, masked_word, guessed_letters):
        """Find all words matching the current pattern"""
        length = len(masked_word)
        candidates = self.full_dictionary_by_length.get(length, [])
        
        if not candidates:
            return []
        
        # Build regex pattern
        pattern = ''
        for char in masked_word:
            if char == '_':
                pattern += '.'
            else:
                pattern += char
        
        regex = re.compile(f'^{pattern}$')
        
        # Find matches
        matching = []
        wrong_letters = guessed_letters - set(masked_word.replace('_', ''))
        
        for word in candidates:
            if regex.match(word):
                # Make sure word doesn't contain letters we know are wrong
                if not any(letter in word for letter in wrong_letters):
                    matching.append(word)
        
        return matching
    
    def guess_letter(self, masked_word, guessed_letters):
        """Choose the best letter to guess"""
        
        # Get available letters
        available = set(string.ascii_lowercase) - guessed_letters
        if not available:
            return None
        
        # Find matching words
        matching_words = self.get_matching_words(masked_word, guessed_letters)
        
        if not matching_words:
            # No matches - use frequency
            letter_freq = {letter: self.letter_freq[letter] for letter in available}
            return max(letter_freq.items(), key=lambda x: x[1])[0]
        
        # Count letter frequencies in matching words (only for blank positions)
        letter_counts = Counter()
        
        for word in matching_words:
            unique_letters = set()
            for i, char in enumerate(masked_word):
                if char == '_':  # Only count letters in blank positions
                    if word[i] in available:
                        unique_letters.add(word[i])
            
            # Count each unique letter once per word (prevents bias from repeated letters)
            for letter in unique_letters:
                letter_counts[letter] += 1
        
        if not letter_counts:
            # Fallback to frequency
            letter_freq = {letter: self.letter_freq[letter] for letter in available}
            return max(letter_freq.items(), key=lambda x: x[1])[0]
        
        # Return most common letter
        return letter_counts.most_common(1)[0][0]

class HangmanGame:
    """Simple Hangman game environment"""
    
    def __init__(self, word, max_lives=6):
        self.word = word.lower()
        self.max_lives = max_lives
        self.reset()
    
    def reset(self):
        self.lives = self.max_lives
        self.guessed_letters = set()
        self.correct_letters = set()
        self.wrong_guesses = 0
        self.repeated_guesses = 0
        self.done = False
        self.won = False
    
    def get_masked_word(self):
        return ''.join([c if c in self.correct_letters else '_' for c in self.word])
    
    def guess(self, letter):
        """Make a guess"""
        letter = letter.lower()
        
        # Check for repeated guess
        if letter in self.guessed_letters:
            self.repeated_guesses += 1
            return False, "repeated"
        
        self.guessed_letters.add(letter)
        
        # Check if correct
        if letter in self.word:
            self.correct_letters.add(letter)
            
            # Check if won
            if set(self.word) == self.correct_letters:
                self.done = True
                self.won = True
            
            return True, "correct"
        else:
            self.wrong_guesses += 1
            self.lives -= 1
            
            # Check if lost
            if self.lives == 0:
                self.done = True
                self.won = False
            
            return False, "wrong"
    
    def get_stats(self):
        return {
            'won': self.won,
            'wrong_guesses': self.wrong_guesses,
            'repeated_guesses': self.repeated_guesses
        }

def play_game(agent, word, verbose=False):
    """Play a single game"""
    game = HangmanGame(word)
    
    if verbose:
        print(f"\nPlaying: {word}")
        print(f"Masked: {game.get_masked_word()}")
    
    while not game.done:
        masked_word = game.get_masked_word()
        guess = agent.guess_letter(masked_word, game.guessed_letters)
        
        if guess is None:
            break
        
        correct, result = game.guess(guess)
        
        if verbose:
            status = "[OK]" if correct else "[X]"
            print(f"{status} Guessed '{guess}': {masked_word} (Lives: {game.lives})")
    
    if verbose:
        print(f"Result: {'WON' if game.won else 'LOST'} - {word}")
        print(f"Stats: {game.get_stats()}")
    
    return game.get_stats()

def evaluate_agent(agent, test_words, verbose=False):
    """Evaluate agent on test set"""
    print("\n" + "="*70)
    print(f"EVALUATING ON TEST SET ({len(test_words)} games)")
    print("="*70)
    
    wins = 0
    total_wrong = 0
    total_repeated = 0
    results = []
    
    for word in tqdm(test_words, desc="Playing games"):
        stats = play_game(agent, word, verbose=False)
        
        if stats['won']:
            wins += 1
        
        total_wrong += stats['wrong_guesses']
        total_repeated += stats['repeated_guesses']
        
        results.append({
            'word': word,
            'won': stats['won'],
            'wrong_guesses': stats['wrong_guesses'],
            'repeated_guesses': stats['repeated_guesses']
        })
    
    success_rate = wins / len(test_words)
    avg_wrong = total_wrong / len(test_words)
    avg_repeated = total_repeated / len(test_words)
    
    # Calculate final score
    final_score = (success_rate * len(test_words)) - (total_wrong * 5) - (total_repeated * 2)
    
    return {
        'success_rate': success_rate,
        'wins': wins,
        'total_games': len(test_words),
        'total_wrong_guesses': total_wrong,
        'total_repeated_guesses': total_repeated,
        'avg_wrong_guesses': avg_wrong,
        'avg_repeated_guesses': avg_repeated,
        'final_score': final_score,
        'results': results
    }

# Main execution
if __name__ == "__main__":
    print("\n" + "="*70)
    print("TRAINING SMART AGENT")
    print("="*70)
    
    # Create agent with corpus as dictionary
    agent = SmartHangmanAgent(corpus_words)
    
    # Test on a few examples first
    print("\nTesting on sample words...")
    sample_words = random.sample(test_words, 5)
    for word in sample_words:
        stats = play_game(agent, word, verbose=True)
    
    # Full evaluation
    results = evaluate_agent(agent, test_words)
    
    # Print results
    print("\n" + "="*70)
    print("FINAL EVALUATION RESULTS")
    print("="*70)
    print(f"Total Games:              {results['total_games']}")
    print(f"Games Won:                {results['wins']}")
    print(f"Success Rate:             {results['success_rate']*100:.2f}%")
    print(f"Total Wrong Guesses:      {results['total_wrong_guesses']}")
    print(f"Total Repeated Guesses:   {results['total_repeated_guesses']}")
    print(f"Avg Wrong per Game:       {results['avg_wrong_guesses']:.2f}")
    print(f"Avg Repeated per Game:    {results['avg_repeated_guesses']:.2f}")
    print("="*70)
    print(f"FINAL SCORE:              {results['final_score']:.2f}")
    print("="*70)
    
    # Score breakdown
    print("\nScore Breakdown:")
    print(f"  Success Points:    {results['success_rate'] * results['total_games']:.2f}")
    print(f"  Wrong Penalty:     -{results['total_wrong_guesses'] * 5:.2f}")
    print(f"  Repeated Penalty:  -{results['total_repeated_guesses'] * 2:.2f}")
    
    if results['final_score'] < -5000:
        print("\n[SUCCESS!] Score is below -5000 target!")
    else:
        print(f"\n[WARNING] Score is {results['final_score']:.2f}, target is < -5000")
    
    # Save results
    with open('evaluation_best_strategy.txt', 'w') as f:
        f.write("BEST STRATEGY HANGMAN AI - EVALUATION\n")
        f.write("=====================================\n\n")
        f.write(f"Total Games: {results['total_games']}\n")
        f.write(f"Games Won: {results['wins']}\n")
        f.write(f"Success Rate: {results['success_rate']*100:.2f}%\n\n")
        f.write(f"Total Wrong Guesses: {results['total_wrong_guesses']}\n")
        f.write(f"Avg Wrong per Game: {results['avg_wrong_guesses']:.2f}\n\n")
        f.write(f"Total Repeated Guesses: {results['total_repeated_guesses']}\n")
        f.write(f"Avg Repeated per Game: {results['avg_repeated_guesses']:.2f}\n\n")
        f.write(f"FINAL SCORE: {results['final_score']:.2f}\n")
    
    pd.DataFrame(results['results']).to_csv('test_results_best.csv', index=False)
    
    print("\n[OK] Results saved to evaluation_best_strategy.txt")
    print("[OK] Details saved to test_results_best.csv")
    print("\n" + "="*70)
    print("STRATEGY EXPLANATION:")
    print("="*70)
    print("This agent uses a simple but highly effective strategy:")
    print("1. Find all corpus words matching the current pattern")
    print("2. Count which letters appear most in matching words")
    print("3. Guess the most common letter in blank positions")
    print("4. Fall back to frequency analysis if no matches found")
    print("\nThis beats complex RL because it directly uses corpus knowledge!")
    print("="*70)
