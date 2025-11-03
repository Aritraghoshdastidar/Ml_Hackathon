"""
CHAMPION Hangman AI - Optimized for ALL word lengths
Special focus on short words which are killing our score
Target: > 60% win rate, score > -5000
"""

import numpy as np
from collections import Counter, defaultdict
import re
from tqdm import tqdm
import string

np.random.seed(42)

print("="*70)
print("CHAMPION HANGMAN AI - SCORE > -5000 OPTIMIZER")
print("="*70)

with open('corpus.txt', 'r') as f:
    corpus_words = [line.strip().lower() for line in f.readlines()]

with open('test.txt', 'r') as f:
    test_words = [line.strip().lower() for line in f.readlines()]

print(f"Loaded {len(corpus_words)} corpus, {len(test_words)} test words")

class ChampionAgent:
    """Champion agent optimized for maximum wins"""
    
    def __init__(self, word_list):
        self.dictionary = word_list
        self.dict_by_length = defaultdict(list)
        
        for word in word_list:
            self.dict_by_length[len(word)].append(word)
        
        # Overall letter frequency
        self.letter_freq = Counter(''.join(word_list))
        
        # Position-specific frequencies
        self.pos_freq = {}
        for length, words in self.dict_by_length.items():
            self.pos_freq[length] = [Counter() for _ in range(length)]
            for word in words:
                for pos, letter in enumerate(word):
                    self.pos_freq[length][pos][letter] += 1
        
        # Bigrams and trigrams
        self.bigrams = Counter()
        self.trigrams = Counter()
        for word in word_list:
            for i in range(len(word)-1):
                self.bigrams[(word[i], word[i+1])] += 1
            for i in range(len(word)-2):
                self.trigrams[(word[i], word[i+1], word[i+2])] += 1
        
        # CRITICAL: Tested letter order for maximum success
        # This is based on actual English frequency in typical words
        self.priority_letters = list("etaoinshrdlcumwfgypbvkjxqz")
        
        print(f"Champion agent initialized")
        print(f"  Letter priority: {self.priority_letters[:15]}")
    
    def get_matches(self, masked_word, guessed_letters):
        """Fast pattern matching"""
        length = len(masked_word)
        if length not in self.dict_by_length:
            return []
        
        pattern = '^' + ''.join([c if c != '_' else '.' for c in masked_word]) + '$'
        regex = re.compile(pattern)
        
        wrong_letters = guessed_letters - set(masked_word.replace('_', ''))
        
        matches = [w for w in self.dict_by_length[length] 
                   if regex.match(w) and not wrong_letters.intersection(set(w))]
        
        return matches[:500]  # Limit for speed
    
    def guess_letter(self, masked_word, guessed_letters):
        """Smart adaptive guessing"""
        
        available = set(string.ascii_lowercase) - guessed_letters
        if not available:
            return None
        
        length = len(masked_word)
        num_guessed = len(guessed_letters)
        num_blanks = masked_word.count('_')
        percent_revealed = 1 - (num_blanks / length)
        
        scores = defaultdict(float)
        
        # ========== ADAPTIVE STRATEGY ==========
        
        # STAGE 1: First 3 guesses - use universal best letters
        if num_guessed < 3:
            # These letters appear in 70%+ of English words
            for i, letter in enumerate(['e', 't', 'a', 'o', 'i', 'n', 's', 'h', 'r']):
                if letter in available:
                    scores[letter] += (10 - i) * 5000  # Heavily favor early optimal letters
        
        # STAGE 2: Pattern matching (if we have good matches)
        matches = self.get_matches(masked_word, guessed_letters)
        
        if matches and len(matches) <= 200:
            # Count letters that would complete words
            letter_coverage = Counter()
            for word in matches:
                seen = set()
                for i, char in enumerate(masked_word):
                    if char == '_' and word[i] in available and word[i] not in seen:
                        letter_coverage[word[i]] += 1
                        seen.add(word[i])
            
            # Weight by coverage percentage
            if letter_coverage:
                max_coverage = max(letter_coverage.values())
                for letter, count in letter_coverage.items():
                    coverage_pct = count / len(matches)
                    scores[letter] += coverage_pct * 8000
        
        # STAGE 3: Context from revealed letters
        
        # Trigram context (strongest)
        for i in range(len(masked_word) - 2):
            chars = [masked_word[i], masked_word[i+1], masked_word[i+2]]
            
            # _XX pattern
            if chars[0] == '_' and chars[1] != '_' and chars[2] != '_':
                for letter in available:
                    scores[letter] += self.trigrams.get((letter, chars[1], chars[2]), 0) * 30
            
            # X_X pattern
            elif chars[0] != '_' and chars[1] == '_' and chars[2] != '_':
                for letter in available:
                    scores[letter] += self.trigrams.get((chars[0], letter, chars[2]), 0) * 30
            
            # XX_ pattern
            elif chars[0] != '_' and chars[1] != '_' and chars[2] == '_':
                for letter in available:
                    scores[letter] += self.trigrams.get((chars[0], chars[1], letter), 0) * 30
        
        # Bigram context
        for pos, char in enumerate(masked_word):
            if char != '_':
                # Left neighbor blank
                if pos > 0 and masked_word[pos-1] == '_':
                    for letter in available:
                        scores[letter] += self.bigrams.get((letter, char), 0) * 20
                
                # Right neighbor blank
                if pos < length - 1 and masked_word[pos+1] == '_':
                    for letter in available:
                        scores[letter] += self.bigrams.get((char, letter), 0) * 20
        
        # STAGE 4: Position-specific frequencies
        if length in self.pos_freq:
            for pos, char in enumerate(masked_word):
                if char == '_':
                    for letter in available:
                        scores[letter] += self.pos_freq[length][pos].get(letter, 0) * 8
        
        # STAGE 5: Overall frequency baseline
        for letter in available:
            scores[letter] += self.letter_freq.get(letter, 0) * 1
        
        # STAGE 6: Adaptive vowel management
        # If many blanks remain and we haven't tried many vowels
        vowels_guessed = len(guessed_letters.intersection(set('aeiou')))
        if num_blanks > length * 0.5 and vowels_guessed < 4:
            for vowel in ['u', 'o']:  # Less common vowels
                if vowel in available:
                    scores[vowel] += 4000
        
        # STAGE 7: Late game - try common consonants if stuck
        if percent_revealed > 0.6 and num_guessed > 5:
            for consonant in ['r', 'd', 'l', 'c', 'm', 'w', 'f', 'g', 'y', 'p', 'b']:
                if consonant in available:
                    scores[consonant] += 2000
        
        # Choose best scored letter
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        # Emergency fallback: priority order
        for letter in self.priority_letters:
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
            return False
        
        self.guessed.add(letter)
        
        if letter in self.word:
            self.correct.add(letter)
            if set(self.word) == self.correct:
                self.done = True
                self.won = True
            return True
        else:
            self.wrong_count += 1
            self.lives -= 1
            if self.lives == 0:
                self.done = True
                self.won = False
            return False
    
    def get_stats(self):
        return {
            'won': self.won,
            'wrong': self.wrong_count,
            'repeated': self.repeated_count
        }

def play(agent, word):
    game = HangmanGame(word)
    
    while not game.done:
        guess = agent.guess_letter(game.get_masked(), game.guessed)
        if guess is None:
            break
        game.guess(guess)
    
    return game.get_stats()

def evaluate(agent, words):
    print(f"\nEvaluating on {len(words)} games...")
    
    wins = 0
    total_wrong = 0
    total_repeated = 0
    
    for word in tqdm(words, desc="Playing"):
        stats = play(agent, word)
        wins += stats['won']
        total_wrong += stats['wrong']
        total_repeated += stats['repeated']
    
    score = wins - (total_wrong * 5) - (total_repeated * 2)
    
    return {
        'total': len(words),
        'wins': wins,
        'win_rate': wins / len(words),
        'total_wrong': total_wrong,
        'avg_wrong': total_wrong / len(words),
        'total_repeated': total_repeated,
        'score': score
    }

if __name__ == "__main__":
    print("\nInitializing Champion Agent...")
    agent = ChampionAgent(corpus_words)
    
    results = evaluate(agent, test_words)
    
    print("\n" + "="*70)
    print("CHAMPION AI - FINAL RESULTS")
    print("="*70)
    print(f"Total Games:          {results['total']}")
    print(f"Wins:                 {results['wins']}")
    print(f"Win Rate:             {results['win_rate']*100:.2f}%")
    print(f"Total Wrong:          {results['total_wrong']}")
    print(f"Avg Wrong/Game:       {results['avg_wrong']:.2f}")
    print(f"Total Repeated:       {results['total_repeated']}")
    print("="*70)
    print(f"FINAL SCORE:          {results['score']:.0f}")
    print("="*70)
    
    if results['score'] > -5000:
        print(f"\n*** TARGET ACHIEVED! Score {results['score']} > -5000 ***")
    else:
        gap = abs(results['score'] + 5000)
        print(f"\nGap: {gap} points")
        print(f"Need ~{gap/results['total']:.1f} more points/game")
    
    # Save
    with open('evaluation_champion.txt', 'w') as f:
        f.write(f"CHAMPION HANGMAN AI\\n")
        f.write(f"===================\\n\\n")
        f.write(f"Total Games: {results['total']}\\n")
        f.write(f"Wins: {results['wins']}\\n")
        f.write(f"Win Rate: {results['win_rate']*100:.2f}%\\n\\n")
        f.write(f"Total Wrong: {results['total_wrong']}\\n")
        f.write(f"Avg Wrong/Game: {results['avg_wrong']:.2f}\\n\\n")
        f.write(f"Total Repeated: {results['total_repeated']}\\n\\n")
        f.write(f"FINAL SCORE: {results['score']}\\n")
    
    print("\nSaved to evaluation_champion.txt")
    print("="*70)
