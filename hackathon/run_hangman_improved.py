"""
Hangman AI Agent - IMPROVED Version
Optimized for high win rate AND score < -5000
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
import random
import pickle
from tqdm import tqdm
import string
import time
import re

# Set random seeds
np.random.seed(42)
random.seed(42)

print("="*70)
print("HANGMAN AI AGENT - IMPROVED VERSION")
print("="*70)
print("\nLoading data...")

# Load corpus and test data
with open('corpus.txt', 'r') as f:
    corpus_words = [line.strip().lower() for line in f.readlines()]

with open('test.txt', 'r') as f:
    test_words = [line.strip().lower() for line in f.readlines()]

print(f"✓ Loaded {len(corpus_words)} corpus words")
print(f"✓ Loaded {len(test_words)} test words")

# IMPROVED HMM Implementation with better pattern matching
class ImprovedHangmanHMM:
    def __init__(self):
        self.length_models = {}
        self.letter_freq = Counter()
        self.alphabet = set(string.ascii_lowercase)
        self.word_list_by_length = {}
        self.all_words = []
    
    def train(self, words):
        print("\n" + "="*70)
        print("TRAINING IMPROVED HIDDEN MARKOV MODEL")
        print("="*70)
        
        self.all_words = words
        words_by_length = defaultdict(list)
        
        for word in words:
            words_by_length[len(word)].append(word)
            self.letter_freq.update(word)
        
        self.word_list_by_length = dict(words_by_length)
        
        for length, word_list in tqdm(words_by_length.items(), desc="Training HMM"):
            self.length_models[length] = self._train_length_model(word_list, length)
        
        print(f"✓ Trained models for {len(self.length_models)} word lengths")
    
    def _train_length_model(self, words, length):
        model = {
            'position_letter_counts': [Counter() for _ in range(length)],
            'bigram_counts': [Counter() for _ in range(length - 1)],
            'trigram_counts': [Counter() for _ in range(length - 2)] if length > 2 else [],
        }
        
        for word in words:
            for pos, letter in enumerate(word):
                model['position_letter_counts'][pos][letter] += 1
            
            for i in range(len(word) - 1):
                model['bigram_counts'][i][(word[i], word[i+1])] += 1
            
            # Add trigrams for better context
            for i in range(len(word) - 2):
                model['trigram_counts'][i][(word[i], word[i+1], word[i+2])] += 1
        
        return model
    
    def get_matching_words(self, masked_word, guessed_letters):
        """Get words that match the current pattern"""
        length = len(masked_word)
        if length not in self.word_list_by_length:
            return []
        
        # Create regex pattern
        pattern = masked_word.replace('_', '.')
        regex = re.compile(f'^{pattern}$')
        
        matching_words = []
        for word in self.word_list_by_length[length]:
            # Check if word matches pattern and doesn't contain guessed wrong letters
            if regex.match(word):
                # Check that revealed letters match
                match = True
                for i, char in enumerate(masked_word):
                    if char != '_' and word[i] != char:
                        match = False
                        break
                
                # Check that word doesn't contain letters we guessed wrong
                if match:
                    word_letters = set(word)
                    wrong_letters = guessed_letters - set(masked_word.replace('_', ''))
                    if not word_letters.intersection(wrong_letters):
                        matching_words.append(word)
        
        return matching_words
    
    def predict_letter_probabilities(self, masked_word, guessed_letters):
        """Improved prediction using word matching"""
        length = len(masked_word)
        remaining_letters = self.alphabet - guessed_letters
        
        if not remaining_letters:
            return {}
        
        # Strategy 1: Find matching words
        matching_words = self.get_matching_words(masked_word, guessed_letters)
        
        letter_scores = Counter()
        
        if matching_words:
            # Count letters from matching words
            for word in matching_words:
                for i, char in enumerate(masked_word):
                    if char == '_' and word[i] in remaining_letters:
                        letter_scores[word[i]] += 1
            
            # Weight heavily - this is our best information
            for letter in letter_scores:
                letter_scores[letter] *= 100
        
        # Strategy 2: Use HMM models if available
        if length in self.length_models:
            model = self.length_models[length]
            
            # Position-based frequencies
            for pos, char in enumerate(masked_word):
                if char == '_':
                    for letter in remaining_letters:
                        letter_scores[letter] += model['position_letter_counts'][pos].get(letter, 0) * 2
            
            # Bigram context
            for pos, char in enumerate(masked_word):
                if char != '_':
                    # Left neighbor
                    if pos > 0 and masked_word[pos-1] == '_':
                        for letter in remaining_letters:
                            letter_scores[letter] += model['bigram_counts'][pos-1].get((letter, char), 0) * 5
                    
                    # Right neighbor
                    if pos < length - 1 and masked_word[pos+1] == '_':
                        for letter in remaining_letters:
                            letter_scores[letter] += model['bigram_counts'][pos].get((char, letter), 0) * 5
            
            # Trigram context (if available)
            if len(model['trigram_counts']) > 0:
                for pos in range(length - 2):
                    chars = [masked_word[pos], masked_word[pos+1], masked_word[pos+2]]
                    
                    # Pattern: _XX
                    if chars[0] == '_' and chars[1] != '_' and chars[2] != '_':
                        for letter in remaining_letters:
                            letter_scores[letter] += model['trigram_counts'][pos].get((letter, chars[1], chars[2]), 0) * 8
                    
                    # Pattern: X_X
                    elif chars[0] != '_' and chars[1] == '_' and chars[2] != '_':
                        for letter in remaining_letters:
                            letter_scores[letter] += model['trigram_counts'][pos].get((chars[0], letter, chars[2]), 0) * 8
                    
                    # Pattern: XX_
                    elif chars[0] != '_' and chars[1] != '_' and chars[2] == '_':
                        for letter in remaining_letters:
                            letter_scores[letter] += model['trigram_counts'][pos].get((chars[0], chars[1], letter), 0) * 8
        
        # Strategy 3: Fallback to frequency
        if sum(letter_scores.values()) == 0:
            for letter in remaining_letters:
                letter_scores[letter] = self.letter_freq.get(letter, 1)
        
        # Normalize to probabilities
        total = sum(letter_scores.values())
        if total == 0:
            # Uniform distribution as last resort
            return {letter: 1.0 / len(remaining_letters) for letter in remaining_letters}
        
        probabilities = {letter: score / total for letter, score in letter_scores.items()}
        return probabilities

# Hangman Environment (same as before but with better rewards)
class HangmanEnvironment:
    def __init__(self, word, max_lives=6):
        self.word = word.lower()
        self.max_lives = max_lives
        self.reset()
    
    def reset(self):
        self.lives = self.max_lives
        self.guessed_letters = set()
        self.correct_guesses = set()
        self.wrong_guesses = 0
        self.repeated_guesses = 0
        self.masked_word = '_' * len(self.word)
        self.done = False
        return self.get_state()
    
    def get_state(self):
        return {
            'masked_word': self.masked_word,
            'guessed_letters': self.guessed_letters.copy(),
            'lives': self.lives,
            'done': self.done
        }
    
    def step(self, letter):
        letter = letter.lower()
        
        if letter in self.guessed_letters:
            self.repeated_guesses += 1
            return self.get_state(), -10, self.done  # Increased penalty
        
        self.guessed_letters.add(letter)
        
        if letter in self.word:
            self.correct_guesses.add(letter)
            self.masked_word = ''.join([c if c in self.correct_guesses else '_' for c in self.word])
            
            num_revealed = self.word.count(letter)
            reward = 15 * num_revealed  # Increased reward for correct guesses
            
            if '_' not in self.masked_word:
                self.done = True
                reward += 200  # Increased win bonus
        else:
            self.wrong_guesses += 1
            self.lives -= 1
            reward = -8  # Slightly reduced penalty to encourage exploration
            
            if self.lives == 0:
                self.done = True
                reward -= 100  # Increased loss penalty
        
        return self.get_state(), reward, self.done
    
    def get_stats(self):
        return {
            'won': self.done and self.lives > 0,
            'wrong_guesses': self.wrong_guesses,
            'repeated_guesses': self.repeated_guesses
        }

# Improved RL Agent - relies more on HMM
class ImprovedRLAgent:
    def __init__(self, hmm, epsilon=0.2, epsilon_decay=0.998, epsilon_min=0.02):
        self.hmm = hmm
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.learning_rate = 0.15  # Slightly higher learning rate
        self.discount_factor = 0.95  # Higher discount for long-term thinking
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.alphabet = set(string.ascii_lowercase)
    
    def _state_to_key(self, masked_word, guessed_letters, lives):
        guessed_str = ''.join(sorted(guessed_letters))
        return f"{masked_word}:{guessed_str}:{lives}"
    
    def choose_action(self, state, training=True):
        masked_word = state['masked_word']
        guessed_letters = state['guessed_letters']
        lives = state['lives']
        
        available_letters = self.alphabet - guessed_letters
        if not available_letters:
            return None
        
        # Get HMM predictions
        hmm_probs = self.hmm.predict_letter_probabilities(masked_word, guessed_letters)
        
        # During training, use epsilon-greedy
        if training and random.random() < self.epsilon:
            # Exploration: weighted by HMM
            if hmm_probs:
                letters = list(hmm_probs.keys())
                weights = list(hmm_probs.values())
                return random.choices(letters, weights=weights, k=1)[0]
            else:
                return random.choice(list(available_letters))
        
        # Exploitation: combine Q-values with HMM (trust HMM more)
        state_key = self._state_to_key(masked_word, guessed_letters, lives)
        action_values = {}
        
        for letter in available_letters:
            q_value = self.q_table[state_key][letter]
            hmm_bonus = hmm_probs.get(letter, 0) * 200  # Increased HMM weight
            action_values[letter] = q_value + hmm_bonus
        
        return max(action_values.items(), key=lambda x: x[1])[0]
    
    def update_q_value(self, state, action, reward, next_state):
        state_key = self._state_to_key(state['masked_word'], state['guessed_letters'], state['lives'])
        
        if next_state['done']:
            max_next_q = 0
        else:
            next_state_key = self._state_to_key(next_state['masked_word'], 
                                               next_state['guessed_letters'], 
                                               next_state['lives'])
            available_letters = self.alphabet - next_state['guessed_letters']
            if available_letters:
                max_next_q = max([self.q_table[next_state_key][letter] for letter in available_letters])
            else:
                max_next_q = 0
        
        current_q = self.q_table[state_key][action]
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state_key][action] = new_q
    
    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

# Training function with more episodes
def train_agent(agent, words, num_episodes=8000):
    print("\n" + "="*70)
    print(f"TRAINING IMPROVED RL AGENT ({num_episodes} episodes)")
    print("="*70)
    
    episode_rewards = []
    episode_wins = []
    
    start_time = time.time()
    
    for episode in tqdm(range(num_episodes), desc="Training RL Agent"):
        word = random.choice(words)
        env = HangmanEnvironment(word)
        state = env.reset()
        
        total_reward = 0
        
        while not state['done']:
            action = agent.choose_action(state, training=True)
            if action is None:
                break
            
            next_state, reward, done = env.step(action)
            agent.update_q_value(state, action, reward, next_state)
            
            total_reward += reward
            state = next_state
        
        stats = env.get_stats()
        episode_rewards.append(total_reward)
        episode_wins.append(1 if stats['won'] else 0)
        
        agent.decay_epsilon()
        
        if (episode + 1) % 1000 == 0:
            recent_wins = sum(episode_wins[-1000:]) / 10
            recent_reward = sum(episode_rewards[-1000:]) / 1000
            print(f"\n  Episode {episode + 1}: Win rate = {recent_wins:.1f}%, "
                  f"Avg reward = {recent_reward:.1f}, ε = {agent.epsilon:.3f}")
    
    training_time = time.time() - start_time
    print(f"\n✓ Training completed in {training_time:.1f} seconds")
    print(f"✓ Final epsilon: {agent.epsilon:.3f}")
    print(f"✓ Q-table size: {len(agent.q_table)} states")
    
    return {'rewards': episode_rewards, 'wins': episode_wins}

# Evaluation function
def evaluate_agent(agent, test_words):
    print("\n" + "="*70)
    print(f"EVALUATING ON TEST SET ({len(test_words)} games)")
    print("="*70)
    
    wins = 0
    total_wrong_guesses = 0
    total_repeated_guesses = 0
    game_results = []
    
    for word in tqdm(test_words, desc="Playing test games"):
        env = HangmanEnvironment(word)
        state = env.reset()
        
        while not state['done']:
            action = agent.choose_action(state, training=False)
            if action is None:
                break
            state, reward, done = env.step(action)
        
        stats = env.get_stats()
        if stats['won']:
            wins += 1
        total_wrong_guesses += stats['wrong_guesses']
        total_repeated_guesses += stats['repeated_guesses']
        
        game_results.append({
            'word': word,
            'won': stats['won'],
            'wrong_guesses': stats['wrong_guesses'],
            'repeated_guesses': stats['repeated_guesses']
        })
    
    success_rate = wins / len(test_words)
    final_score = (success_rate * len(test_words)) - (total_wrong_guesses * 5) - (total_repeated_guesses * 2)
    
    return {
        'success_rate': success_rate,
        'wins': wins,
        'total_games': len(test_words),
        'total_wrong_guesses': total_wrong_guesses,
        'total_repeated_guesses': total_repeated_guesses,
        'avg_wrong_guesses': total_wrong_guesses / len(test_words),
        'avg_repeated_guesses': total_repeated_guesses / len(test_words),
        'final_score': final_score,
        'game_results': game_results
    }

# Main execution
if __name__ == "__main__":
    # Train improved HMM
    hmm = ImprovedHangmanHMM()
    hmm.train(corpus_words)
    
    # Initialize and train improved RL agent
    agent = ImprovedRLAgent(hmm, epsilon=0.2, epsilon_decay=0.9988, epsilon_min=0.02)
    training_results = train_agent(agent, corpus_words, num_episodes=8000)
    
    # Evaluate on test set
    test_results = evaluate_agent(agent, test_words)
    
    # Print final results
    print("\n" + "="*70)
    print("FINAL EVALUATION RESULTS")
    print("="*70)
    print(f"Total Games:              {test_results['total_games']}")
    print(f"Games Won:                {test_results['wins']}")
    print(f"Success Rate:             {test_results['success_rate']*100:.2f}%")
    print(f"Total Wrong Guesses:      {test_results['total_wrong_guesses']}")
    print(f"Total Repeated Guesses:   {test_results['total_repeated_guesses']}")
    print(f"Avg Wrong per Game:       {test_results['avg_wrong_guesses']:.2f}")
    print(f"Avg Repeated per Game:    {test_results['avg_repeated_guesses']:.2f}")
    print("="*70)
    print(f"FINAL SCORE:              {test_results['final_score']:.2f}")
    print("="*70)
    
    # Score analysis
    score_components = {
        'Success Points': test_results['success_rate'] * test_results['total_games'],
        'Wrong Penalty': -test_results['total_wrong_guesses'] * 5,
        'Repeated Penalty': -test_results['total_repeated_guesses'] * 2
    }
    
    print("\nScore Breakdown:")
    for component, value in score_components.items():
        print(f"  {component}: {value:.2f}")
    
    if test_results['final_score'] < -5000:
        print("\n✅ SUCCESS! Score is below -5000 target!")
    else:
        print("\n⚠️  Score is above -5000.")
    
    # Save detailed results
    with open('evaluation_summary_improved.txt', 'w') as f:
        f.write(f"IMPROVED HANGMAN AI - FINAL EVALUATION\n")
        f.write(f"======================================\n\n")
        f.write(f"Total Games: {test_results['total_games']}\n")
        f.write(f"Games Won: {test_results['wins']}\n")
        f.write(f"Success Rate: {test_results['success_rate']*100:.2f}%\n\n")
        f.write(f"Total Wrong Guesses: {test_results['total_wrong_guesses']}\n")
        f.write(f"Avg Wrong per Game: {test_results['avg_wrong_guesses']:.2f}\n\n")
        f.write(f"Total Repeated Guesses: {test_results['total_repeated_guesses']}\n")
        f.write(f"Avg Repeated per Game: {test_results['avg_repeated_guesses']:.2f}\n\n")
        f.write(f"FINAL SCORE: {test_results['final_score']:.2f}\n\n")
        f.write(f"Score Breakdown:\n")
        for component, value in score_components.items():
            f.write(f"  {component}: {value:.2f}\n")
    
    # Save game results
    pd.DataFrame(test_results['game_results']).to_csv('test_results_improved.csv', index=False)
    
    print("\n✓ Results saved to evaluation_summary_improved.txt")
    print("✓ Game details saved to test_results_improved.csv")
    print("\n" + "="*70)
    print("IMPROVEMENT SUMMARY:")
    print("="*70)
    print("Key improvements over original:")
    print("✓ Better word matching with regex patterns")
    print("✓ Trigram context (3-letter sequences) for better predictions")
    print("✓ Increased HMM weight (200x vs 50x)")
    print("✓ More training episodes (8000 vs 5000)")
    print("✓ Better reward structure encouraging wins")
    print("✓ Lower exploration rate (trusts HMM more)")
    print("="*70)
