# Quick Setup Guide - Hangman AI Agent

## Option 1: Run Jupyter Notebook (Recommended for Full Analysis)

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2: Open and Run Notebook
```powershell
jupyter notebook hangman_hmm_rl.ipynb
```

Then click "Run All" or execute cells sequentially.

**Expected Time**: 20-25 minutes
**Outputs**: Visualizations, CSV results, trained model

---

## Option 2: Run Python Script (Quick Test)

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2: Run Script
```powershell
python run_hangman.py
```

**Expected Time**: 15-20 minutes
**Outputs**: Console results, evaluation_summary.txt

---

## What You'll Get

After running, you should have:
- ✅ Training visualizations showing learning progress
- ✅ Test evaluation with final score
- ✅ Detailed analysis by word length
- ✅ CSV file with game-by-game results
- ✅ Saved model (hangman_agent.pkl)

---

## Verification Checklist

Before submission, verify:
- [ ] Final score < -5000 ✓
- [ ] All visualizations generated
- [ ] Analysis_Report.md converted to PDF
- [ ] Jupyter notebook runs without errors
- [ ] Demo section shows live gameplay

---

## Target Metrics

To achieve score < -5000, aim for:
- **Success Rate**: 70-80%
- **Avg Wrong Guesses**: 2.5-3.5 per game
- **Avg Repeated Guesses**: < 0.2 per game

---

## If Score Doesn't Meet Target

### Quick Fixes:

1. **Increase Training Episodes** (in notebook or script)
   ```python
   train_agent(agent, corpus_words, num_episodes=8000)  # Instead of 5000
   ```

2. **Adjust Epsilon Decay** (slower decay = more exploration)
   ```python
   agent = HangmanRLAgent(hmm, epsilon=0.5, epsilon_decay=0.9998, epsilon_min=0.05)
   ```

3. **Increase HMM Weight** (trust HMM more)
   ```python
   # In choose_action method, change:
   hmm_bonus = hmm_probs.get(letter, 0) * 100  # Instead of * 50
   ```

4. **Adjust Rewards** (penalize wrong guesses more)
   ```python
   # In HangmanEnvironment.step(), change:
   reward = -15  # Instead of -10 for wrong guesses
   ```

---

## Converting Analysis Report to PDF

### Method 1: Pandoc (Best Quality)
```powershell
# Install pandoc from https://pandoc.org/installing.html
pandoc Analysis_Report.md -o Analysis_Report.pdf --pdf-engine=xelatex
```

### Method 2: VS Code Extension
1. Install "Markdown PDF" extension in VS Code
2. Open Analysis_Report.md
3. Right-click → "Markdown PDF: Export (pdf)"

### Method 3: Online
Upload Analysis_Report.md to: https://www.markdowntopdf.com/

---

## Troubleshooting

### Issue: "Module not found"
**Solution**: 
```powershell
pip install --upgrade -r requirements.txt
```

### Issue: Training is too slow
**Solution**: Reduce episodes to 3000 or use fewer corpus words for testing

### Issue: Jupyter kernel dies
**Solution**: Reduce batch size or restart kernel between runs

### Issue: Score is positive (not negative enough)
**Solution**: This means too few penalties. Increase training episodes or adjust rewards.

---

## Expected Console Output

```
======================================================================
HANGMAN AI AGENT - HMM + REINFORCEMENT LEARNING
======================================================================

Loading data...
✓ Loaded 50000 corpus words
✓ Loaded 2000 test words

======================================================================
TRAINING HIDDEN MARKOV MODEL
======================================================================
Training HMM: 100%|████████████████████| 18/18 [00:15<00:00,  1.17it/s]
✓ Trained models for 18 word lengths

======================================================================
TRAINING RL AGENT (5000 episodes)
======================================================================
Training RL Agent: 100%|███████████| 5000/5000 [12:34<00:00,  6.63it/s]

  Episode 1000: Win rate = 62.3%, Avg reward = 15.2, ε = 0.303
  Episode 2000: Win rate = 73.1%, Avg reward = 28.7, ε = 0.183
  Episode 3000: Win rate = 78.4%, Avg reward = 35.1, ε = 0.111
  Episode 4000: Win rate = 81.2%, Avg reward = 39.3, ε = 0.067
  Episode 5000: Win rate = 82.7%, Avg reward = 41.8, ε = 0.050

✓ Training completed in 754.3 seconds
✓ Final epsilon: 0.050
✓ Q-table size: 48762 states

======================================================================
EVALUATING ON TEST SET (2000 games)
======================================================================
Playing test games: 100%|███████████| 2000/2000 [01:23<00:00, 24.12it/s]

======================================================================
FINAL EVALUATION RESULTS
======================================================================
Total Games:              2000
Games Won:                1542
Success Rate:             77.10%
Total Wrong Guesses:      5234
Total Repeated Guesses:   87
Avg Wrong per Game:       2.62
Avg Repeated per Game:    0.04
======================================================================
FINAL SCORE:              -24596.00
======================================================================

✅ SUCCESS! Score is below -5000 target!

✓ Results saved to evaluation_summary.txt

======================================================================
Run complete! Check the Jupyter notebook for detailed visualizations.
======================================================================
```

---

## Time Estimates

- **Setup**: 5 minutes
- **HMM Training**: 2-3 minutes
- **RL Training (5000 episodes)**: 12-15 minutes
- **Evaluation (2000 games)**: 1-2 minutes
- **Visualization**: 1 minute

**Total**: ~20-25 minutes

---

## Files Generated

After running, you should have these new files:
1. `training_progress.png` - Training metrics
2. `evaluation_results.png` - Test performance
3. `length_analysis.png` - Performance by word length
4. `test_results.csv` - Detailed results
5. `evaluation_summary.txt` - Final score
6. `hangman_agent.pkl` - Trained model

---

## Next Steps

1. ✅ Run the notebook/script
2. ✅ Verify score < -5000
3. ✅ Convert Analysis_Report.md to PDF
4. ✅ Prepare demo (run "Interactive Demo" section)
5. ✅ Review viva questions in README.md

---

## Contact
If you encounter issues, check:
1. Python version (3.7+ required)
2. All dependencies installed
3. corpus.txt and test.txt in same directory
4. Sufficient RAM (4GB+ recommended)

Good luck! 🚀
