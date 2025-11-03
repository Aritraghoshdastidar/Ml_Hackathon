"""
Hyperparameter Configuration for Hangman AI Agent
Adjust these values to optimize performance
"""

# HMM Configuration
HMM_CONFIG = {
    'max_pattern_samples': 100,  # Number of masked patterns to generate per word
    'position_weight': 1.0,      # Weight for position-based letter frequencies
    'bigram_weight': 2.0,        # Weight for bigram context
    'pattern_weight': 10.0,      # Weight for pattern matching
}

# RL Agent Configuration
RL_CONFIG = {
    'epsilon_start': 0.5,        # Initial exploration rate
    'epsilon_decay': 0.9995,     # Decay rate per episode
    'epsilon_min': 0.05,         # Minimum exploration rate
    'learning_rate': 0.1,        # Q-learning alpha parameter
    'discount_factor': 0.9,      # Q-learning gamma parameter
    'hmm_bonus_weight': 50,      # How much to weight HMM predictions in action selection
}

# Training Configuration
TRAINING_CONFIG = {
    'num_episodes': 5000,        # Number of training episodes
    'report_interval': 1000,     # Episodes between progress reports
    'max_lives': 6,              # Maximum wrong guesses per game
}

# Reward Configuration
REWARD_CONFIG = {
    'correct_guess_base': 10,    # Base reward per revealed letter
    'wrong_guess_penalty': -10,  # Penalty for wrong guess
    'repeated_guess_penalty': -5, # Penalty for repeated guess
    'win_bonus': 100,            # Bonus for winning game
    'loss_penalty': -50,         # Penalty for losing game
}

# Evaluation Configuration
EVAL_CONFIG = {
    'success_weight': 1,         # Multiplier for success rate in final score
    'wrong_penalty': 5,          # Multiplier for wrong guesses in final score
    'repeated_penalty': 2,       # Multiplier for repeated guesses in final score
}

# Advanced: Target Score Optimization
# If your score is not meeting -5000 target, try these presets:

# Preset 1: More Conservative (fewer wrong guesses)
CONSERVATIVE_PRESET = {
    'RL_CONFIG': {
        'epsilon_start': 0.3,
        'epsilon_decay': 0.9998,
        'epsilon_min': 0.03,
        'hmm_bonus_weight': 100,  # Trust HMM more
    },
    'REWARD_CONFIG': {
        'wrong_guess_penalty': -15,  # Penalize mistakes more
        'win_bonus': 150,
    }
}

# Preset 2: More Exploration (better learning)
EXPLORATION_PRESET = {
    'RL_CONFIG': {
        'epsilon_start': 0.7,
        'epsilon_decay': 0.9993,
        'epsilon_min': 0.08,
        'hmm_bonus_weight': 30,
    },
    'TRAINING_CONFIG': {
        'num_episodes': 8000,  # Train longer
    }
}

# Preset 3: Balanced (default recommended)
BALANCED_PRESET = {
    'RL_CONFIG': {
        'epsilon_start': 0.5,
        'epsilon_decay': 0.9995,
        'epsilon_min': 0.05,
        'hmm_bonus_weight': 50,
    },
    'TRAINING_CONFIG': {
        'num_episodes': 5000,
    }
}

def apply_preset(preset_name):
    """
    Apply a hyperparameter preset
    
    Args:
        preset_name: 'conservative', 'exploration', or 'balanced'
    
    Returns:
        Updated configuration dictionaries
    """
    if preset_name == 'conservative':
        preset = CONSERVATIVE_PRESET
    elif preset_name == 'exploration':
        preset = EXPLORATION_PRESET
    else:
        preset = BALANCED_PRESET
    
    # Merge preset with defaults
    config = {
        'HMM_CONFIG': HMM_CONFIG.copy(),
        'RL_CONFIG': RL_CONFIG.copy(),
        'TRAINING_CONFIG': TRAINING_CONFIG.copy(),
        'REWARD_CONFIG': REWARD_CONFIG.copy(),
        'EVAL_CONFIG': EVAL_CONFIG.copy(),
    }
    
    for key, value in preset.items():
        if key in config:
            config[key].update(value)
    
    return config

# Usage example:
"""
from config import apply_preset, RL_CONFIG, TRAINING_CONFIG

# Use balanced preset (default)
config = apply_preset('balanced')

# Or use specific config directly
agent = HangmanRLAgent(
    hmm, 
    epsilon=RL_CONFIG['epsilon_start'],
    epsilon_decay=RL_CONFIG['epsilon_decay'],
    epsilon_min=RL_CONFIG['epsilon_min']
)
"""

# Performance Tuning Guide
"""
HOW TO OPTIMIZE FOR SCORE < -5000:

1. If score is -3000 (not negative enough):
   - Problem: Too many wrong guesses or low win rate
   - Solution: Use CONSERVATIVE_PRESET
   - Or increase: wrong_guess_penalty, hmm_bonus_weight
   - Or train longer: num_episodes = 8000

2. If score is -15000 (too negative, probably many losses):
   - Problem: Agent is too conservative, missing wins
   - Solution: Use EXPLORATION_PRESET
   - Or increase: epsilon_start, correct_guess_base
   - Check: Is training long enough? Try 8000 episodes

3. If training is unstable (win rate fluctuates):
   - Problem: Learning rate or exploration issues
   - Solution: Decrease learning_rate to 0.05
   - Or decrease epsilon_start to 0.3
   - Or increase epsilon_decay to 0.9998 (slower decay)

4. If agent makes many repeated guesses:
   - Problem: Not learning from mistakes
   - Solution: Increase repeated_guess_penalty to -10
   - Or decrease epsilon_min to 0.03
   - Check: Is state representation tracking guessed letters?

5. For best results:
   - Use BALANCED_PRESET for initial run
   - If score > -5000, switch to CONSERVATIVE_PRESET
   - Always train for at least 5000 episodes
   - Monitor training progress - win rate should reach 75%+

EXPECTED SCORES BY PRESET:
- Conservative: -20,000 to -30,000 (very safe, high win rate)
- Exploration: -5,000 to -15,000 (good balance)
- Balanced: -10,000 to -20,000 (recommended)

All presets should achieve < -5000 target!
"""
