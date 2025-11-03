"""
FINAL ULTIMATE Hangman AI
Uses pure statistical optimization - the BEST approach for unknown/rare words
Target: Score > -5000
"""

import numpy as np
from collections import Counter, defaultdict
import re
from tqdm import tqdm
import string

np.random.seed(42)

print("FINAL ULTIMATE HANGMAN AI - Statistical Optimizer")
print("="*70)

with open('corpus.txt', 'r') as f:
    corpus_words = [line.strip().lower() for line in f.readlines()]

with open('test.txt', 'r') as f:
    test_words = [line.strip().lower() for line in f.readlines()]

print(f"Corpus: {len(corpus_words)} | Test: {len(test_words)}")

class FinalUltimateAgent:
    def __init__(self, words):
        self.words_by_len = defaultdict(list)
        for w in words:
            self.words_by_len[len(w)].append(w)
        
        # Letter frequencies
        all_text = ''.join(words)
        self.freq = Counter(all_text)
        
        # Position frequencies
        self.pos_freq = {}
        for length, word_list in self.words_by_len.items():
            self.pos_freq[length] = [Counter() for _ in range(length)]
            for word in word_list:
                for i, c in enumerate(word):
                    self.pos_freq[length][i][c] += 1
        
        # N-grams
        self.bigrams = Counter()
        self.trigrams = Counter()
        for word in words:
            for i in range(len(word)-1):
                self.bigrams[(word[i], word[i+1])] += 1
            for i in range(len(word)-2):
                self.trigrams[(word[i], word[i+1], word[i+2])] += 1
        
        # THE ULTIMATE ORDERING (proven through testing)
        self.best_order = "etaoinshrdlcumwfgypbvkjxqz"
        
    def get_matches(self, masked, guessed):
        length = len(masked)
        if length not in self.words_by_len:
            return []
        
        pattern = '^' + masked.replace('_', '.') + '$'
        regex = re.compile(pattern)
        wrong = guessed - set(masked.replace('_', ''))
        
        return [w for w in self.words_by_len[length][:2000]  # Limit for speed
                if regex.match(w) and not wrong.intersection(set(w))]
    
    def guess(self, masked, guessed):
        avail = set(string.ascii_lowercase) - guessed
        if not avail:
            return None
        
        n_guessed = len(guessed)
        length = len(masked)
        n_revealed = sum(1 for c in masked if c != '_')
        
        scores = defaultdict(float)
        
        # === CORE STRATEGY ===
        
        # 1. First few guesses: USE THE PROVEN BEST LETTERS
        if n_guessed < 4:
            # These are THE most common letters in English
            top_letters = ['e', 't', 'a', 'o', 'i', 'n', 's', 'r', 'h']
            for i, letter in enumerate(top_letters):
                if letter in avail:
                    scores[letter] += (len(top_letters) - i) * 10000
        
        # 2. Pattern matching (if specific enough)
        matches = self.get_matches(masked, guessed)
        if 0 < len(matches) <= 100:
            counts = Counter()
            for word in matches:
                for i, c in enumerate(masked):
                    if c == '_' and word[i] in avail:
                        counts[word[i]] += 1
            
            if counts:
                total = sum(counts.values())
                for letter, count in counts.items():
                    scores[letter] += (count / total) * 15000
        
        # 3. Trigrams (strong context)
        for i in range(len(masked) - 2):
            p0, p1, p2 = masked[i], masked[i+1], masked[i+2]
            
            if p0 == '_' and p1 != '_' and p2 != '_':
                for letter in avail:
                    scores[letter] += self.trigrams[(letter, p1, p2)] * 50
            elif p0 != '_' and p1 == '_' and p2 != '_':
                for letter in avail:
                    scores[letter] += self.trigrams[(p0, letter, p2)] * 50
            elif p0 != '_' and p1 != '_' and p2 == '_':
                for letter in avail:
                    scores[letter] += self.trigrams[(p0, p1, letter)] * 50
        
        # 4. Bigrams
        for i, c in enumerate(masked):
            if c != '_':
                if i > 0 and masked[i-1] == '_':
                    for letter in avail:
                        scores[letter] += self.bigrams[(letter, c)] * 30
                if i < length - 1 and masked[i+1] == '_':
                    for letter in avail:
                        scores[letter] += self.bigrams[(c, letter)] * 30
        
        # 5. Position frequencies
        if length in self.pos_freq:
            for i, c in enumerate(masked):
                if c == '_':
                    for letter in avail:
                        scores[letter] += self.pos_freq[length][i][letter] * 10
        
        # 6. Base frequency
        for letter in avail:
            scores[letter] += self.freq[letter] * 2
        
        # 7. Vowel boost (adaptive)
        vowels_tried = len(guessed.intersection('aeiou'))
        if n_revealed < length * 0.4 and vowels_tried < 4:
            for v in 'ou':
                if v in avail:
                    scores[v] += 5000
        
        # Choose best
        if scores:
            return max(scores, key=scores.get)
        
        # Fallback
        for letter in self.best_order:
            if letter in avail:
                return letter
        
        return list(avail)[0]

class Game:
    def __init__(self, word):
        self.word = word.lower()
        self.lives = 6
        self.guessed = set()
        self.correct = set()
        self.wrong = 0
        self.repeated = 0
        self.done = False
        self.won = False
    
    def masked(self):
        return ''.join([c if c in self.correct else '_' for c in self.word])
    
    def guess(self, letter):
        if letter in self.guessed:
            self.repeated += 1
            return False
        
        self.guessed.add(letter)
        
        if letter in self.word:
            self.correct.add(letter)
            if set(self.word) == self.correct:
                self.done = True
                self.won = True
            return True
        else:
            self.wrong += 1
            self.lives -= 1
            if self.lives == 0:
                self.done = True
            return False

def play(agent, word):
    game = Game(word)
    while not game.done:
        g = agent.guess(game.masked(), game.guessed)
        if not g:
            break
        game.guess(g)
    return game.won, game.wrong, game.repeated

def evaluate(agent, words):
    print(f"Evaluating {len(words)} games...")
    wins, total_wrong, total_rep = 0, 0, 0
    
    for word in tqdm(words):
        won, wrong, rep = play(agent, word)
        wins += won
        total_wrong += wrong
        total_rep += rep
    
    score = wins - (total_wrong * 5) - (total_rep * 2)
    
    return {
        'wins': wins,
        'total': len(words),
        'wrong': total_wrong,
        'repeated': total_rep,
        'score': score,
        'win_rate': wins / len(words)
    }

if __name__ == "__main__":
    agent = FinalUltimateAgent(corpus_words)
    print("Agent ready\n")
    
    r = evaluate(agent, test_words)
    
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"Games:      {r['total']}")
    print(f"Wins:       {r['wins']} ({r['win_rate']*100:.1f}%)")
    print(f"Wrong:      {r['wrong']} (avg {r['wrong']/r['total']:.2f}/game)")
    print(f"Repeated:   {r['repeated']}")
    print("="*70)
    print(f"SCORE:      {r['score']}")
    print("="*70)
    
    if r['score'] > -5000:
        print(f"\nSUCCESS! {r['score']} > -5000")
    else:
        print(f"\nGap: {abs(r['score']+5000)} points")
    
    with open('FINAL_SCORE.txt', 'w') as f:
        f.write(f"FINAL EVALUATION RESULTS\\n")
        f.write(f"========================\\n\\n")
        f.write(f"Total Games: {r['total']}\\n")
        f.write(f"Games Won: {r['wins']}\\n")
        f.write(f"Success Rate: {r['win_rate']*100:.2f}%\\n\\n")
        f.write(f"Total Wrong Guesses: {r['wrong']}\\n")
        f.write(f"Avg Wrong per Game: {r['wrong']/r['total']:.2f}\\n\\n")
        f.write(f"Total Repeated Guesses: {r['repeated']}\\n\\n")
        f.write(f"FINAL SCORE: {r['score']}\\n")
    
    print("\nSaved to FINAL_SCORE.txt")
