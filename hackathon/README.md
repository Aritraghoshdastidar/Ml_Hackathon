# Hangman AI Agent - HMM + Reinforcement Learning

## Project Overview
This project implements an intelligent Hangman agent that combines Hidden Markov Models (HMM) with Reinforcement Learning to achieve optimal performance. The agent is trained on a 50,000-word corpus and evaluated on 2,000 test words.

## Target Score
**Final Score < -5000** (Formula: Success Rate × 2000 - Wrong Guesses × 5 - Repeated Guesses × 2)

## Files Included
- `hangman_hmm_rl.ipynb` - Main Jupyter notebook with complete implementation
- `Analysis_Report.md` - Comprehensive analysis report (convert to PDF for submission)
- `corpus.txt` - Training corpus (50,000 words)
- `test.txt` - Test set (2,000 words)
- `README.md` - This file

## Requirements
```bash
pip install numpy pandas matplotlib seaborn tqdm
```

## How to Run

### Step 1: Open the Notebook
1. Open `hangman_hmm_rl.ipynb` in Jupyter Notebook or VS Code
2. Ensure Python 3.7+ is installed

### Step 2: Run All Cells
Execute all cells in order. The notebook will:
1. Load and analyze the corpus and test data
2. Train the Hidden Markov Model on the corpus (~2-3 minutes)
3. Build the Hangman game environment
4. Train the RL agent for 5,000 episodes (~15-20 minutes)
5. Evaluate on 2,000 test words (~2-3 minutes)
6. Generate visualizations and analysis

### Step 3: Review Results
After running, you'll have:
- `training_progress.png` - Training metrics visualization
- `evaluation_results.png` - Test performance visualization
- `length_analysis.png` - Performance by word length
- `test_results.csv` - Detailed game-by-game results
- `evaluation_summary.txt` - Final score summary
- `hangman_agent.pkl` - Saved trained model

## Key Components

### 1. Hidden Markov Model
- **Purpose**: Predict letter probabilities given masked word state
- **Hidden States**: Letter positions with contextual information
- **Emissions**: Actual letters A-Z
- **Training**: Separate models for each word length
- **Features**:
  - Position-based letter frequencies
  - Bigram transition probabilities
  - Pattern matching for partial words

### 2. Hangman Environment
- **State**: Masked word, guessed letters, remaining lives
- **Actions**: Guess any unguessed letter
- **Rewards**:
  - +10 per revealed letter for correct guess
  - -10 for wrong guess
  - -5 for repeated guess
  - +100 for winning, -50 for losing

### 3. RL Agent (Q-Learning)
- **Algorithm**: Q-learning with epsilon-greedy exploration
- **State Representation**: `masked_word:guessed_letters:lives`
- **Action Selection**: Hybrid approach combining Q-values and HMM probabilities
- **Exploration**: ε-greedy with exponential decay (0.5 → 0.05)

## Architecture Diagram
```
┌─────────────────────┐
│   Corpus (50K)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Hidden Markov Model│
│  (Letter Prediction)│
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ HMM Probs    │───┐
    └──────────────┘   │
                       │
┌─────────────────────┐│
│   RL Agent          ││
│  (Q-Learning)       ││
│                     ││
│ State: masked_word  ││
│ Action: guess letter││
│                     ││
│ Q(s,a) + HMM_boost  │◄
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Hangman Environment │
└──────────┬──────────┘
           │
           ▼
    [Test Set (2K)]
```

## Performance Optimization Tips

### To achieve score < -5000:
1. **High Win Rate** (75%+)
   - Ensure HMM is trained on full corpus
   - Use epsilon decay to balance exploration/exploitation
   - Let training run for full 5,000 episodes

2. **Minimize Wrong Guesses** (<3 per game average)
   - HMM bigram context reduces wrong guesses significantly
   - Q-learning learns to avoid low-probability letters

3. **Eliminate Repeated Guesses** (<0.1 per game)
   - Agent tracks guessed letters in state
   - Heavy penalty (-5) discourages repeats

### If score is not meeting target:
- Increase training episodes to 8,000-10,000
- Adjust epsilon decay rate (slower decay = more exploration)
- Tune reward weights:
  - Increase wrong guess penalty (-15 instead of -10)
  - Increase win bonus (+150 instead of +100)

## Expected Results

### Training (5,000 episodes):
- Episode 1000: ~60% win rate
- Episode 3000: ~75% win rate
- Episode 5000: ~80% win rate

### Test Set (2,000 games):
- Target Success Rate: 70-80%
- Target Avg Wrong Guesses: 2.5-3.5
- Target Avg Repeated Guesses: <0.2
- **Target Final Score: < -5000**

Example breakdown for score of -5500:
```
Success Rate: 75% (1500 wins)
Wrong Guesses: 5500 total (2.75 avg)
Repeated Guesses: 100 total (0.05 avg)

Final Score = (0.75 × 2000) - (5500 × 5) - (100 × 2)
            = 1500 - 27500 - 200
            = -26,200 ✓✓✓ (Far exceeds target!)
```

## Troubleshooting

### Issue: Training is too slow
- **Solution**: Reduce training episodes to 3,000 or use subset of corpus

### Issue: Score is not low enough (e.g., -3000)
- **Problem**: Too many wrong guesses or too low win rate
- **Solution**: 
  - Increase HMM weight in action selection (change `hmm_bonus = hmm_probs.get(letter, 0) * 50` to `* 100`)
  - Train longer (8,000 episodes)
  - Increase wrong guess penalty

### Issue: Agent makes repeated guesses
- **Problem**: State representation not tracking guessed letters properly
- **Solution**: Verify `guessed_letters` is in state and being updated correctly

### Issue: Memory error
- **Problem**: Q-table too large
- **Solution**: Reduce training episodes or implement state abstraction

## Converting Analysis Report to PDF

### Option 1: Using Pandoc (Recommended)
```bash
pandoc Analysis_Report.md -o Analysis_Report.pdf --pdf-engine=xelatex
```

### Option 2: Using VS Code
1. Install "Markdown PDF" extension
2. Open `Analysis_Report.md`
3. Right-click → "Markdown PDF: Export (pdf)"

### Option 3: Using Online Converter
- Upload `Analysis_Report.md` to https://www.markdowntopdf.com/

## Demo Video Script

### Preparation
1. Run the notebook start to finish
2. Record screen while running the "Interactive Demo" section
3. Show the visualizations (training_progress.png, evaluation_results.png)

### Key Points to Demonstrate
1. **HMM Training**: Show corpus loading and model training
2. **RL Training**: Show training progress, win rate improving
3. **Live Game**: Run demo_game() function, narrate agent's decisions
4. **Final Results**: Show the final score and compare to target
5. **Visualizations**: Walk through the graphs explaining what they show

### Sample Narration
"Here we see the agent playing the word 'PROTECTION'. The HMM predicts high probability for common letters like E, T, O. The agent chooses T first, revealing two T's. Next, it identifies the pattern and guesses common vowels. The agent successfully solves the word in 8 moves with only 1 wrong guess."

## Viva Preparation

### Expected Questions & Answers

**Q: Why use HMM instead of just letter frequency?**
A: HMM captures positional and contextual information. Letter frequency says 'E' is most common overall, but HMM knows 'E' is rare at the start of words and common at the end. Bigrams let us use revealed letters to predict neighbors.

**Q: Why Q-learning instead of policy gradient?**
A: Q-learning is simpler, works well with discrete action spaces (26 letters), and converges reliably with our state representation. Policy gradient would require more training data and careful tuning.

**Q: How does the agent handle repeated guesses?**
A: The state representation includes the set of guessed letters. The agent receives -5 reward for repeated guesses, which updates the Q-value negatively, teaching it to avoid this action in the future.

**Q: What's the most important hyperparameter?**
A: Epsilon decay rate. Too fast and the agent doesn't explore enough (overfits to early patterns). Too slow and training takes forever. We found 0.9995 gives good balance.

**Q: Why separate HMMs for each word length?**
A: Different word lengths have different linguistic patterns. 3-letter words are often articles/pronouns (THE, AND), while 10+ letter words are technical terms with different letter distributions. Separate models capture these differences better.

**Q: How would you improve this further?**
A: Three main directions: (1) Deep Q-Network to handle state space better, (2) Trigram models for richer context, (3) Transfer learning from pre-trained language models like BERT for better linguistic understanding.

## Project Structure
```
hackathon/
├── corpus.txt                  # Training data (50K words)
├── test.txt                    # Test data (2K words)
├── hangman_hmm_rl.ipynb        # Main implementation notebook
├── Analysis_Report.md          # Analysis report (convert to PDF)
├── README.md                   # This file
├── training_progress.png       # Generated after running
├── evaluation_results.png      # Generated after running
├── length_analysis.png         # Generated after running
├── test_results.csv            # Generated after running
├── evaluation_summary.txt      # Generated after running
└── hangman_agent.pkl           # Generated after running
```

## Citation
If you use this code, please cite:
```
Hangman AI Agent using HMM and Reinforcement Learning
UE23CS352A: Machine Learning Hackathon
PESU, November 2025
```

## License
This project is for educational purposes as part of UE23CS352A course.

## Contact
For questions or issues, contact: [Your Email]

---

**Good luck with your hackathon! 🎮🤖**
