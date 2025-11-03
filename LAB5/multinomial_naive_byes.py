# =============================================
# PART A: Multinomial Naive Bayes from Scratch
# =============================================

# --- Imports ---
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------
# STEP 0: Helper function to load data
# ---------------------------------------------
def load_pubmed_rct_file(filepath):
    """
    Reads a .txt file from the PubMed 20k RCT dataset.
    Returns X (sentences) and y (labels) as lists.
    """
    labels, sentences = [], []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or '\t' not in line:
                continue
            label, sent = line.split('\t', maxsplit=1)
            labels.append(label)
            sentences.append(sent)
    return sentences, labels


# ---------------------------------------------
# STEP 1: Data Loading
# ---------------------------------------------
print("Loading data...")
X_train, y_train = load_pubmed_rct_file("train.txt")
X_dev, y_dev     = load_pubmed_rct_file("dev.txt")
X_test, y_test   = load_pubmed_rct_file("test.txt")

print(f"Train samples: {len(X_train)}")
print(f"Dev samples: {len(X_dev)}")
print(f"Test samples: {len(X_test)}")


# ---------------------------------------------
# STEP 2: Custom Multinomial Naive Bayes class
# ---------------------------------------------
class NaiveBayesClassifier:
    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.classes_ = None
        self.class_count_ = None
        self.feature_count_ = None
        self.feature_log_prob_ = None
        self.class_log_prior_ = None
        self.vocab_size_ = None

    def fit(self, X_counts, y):
        # Convert to dense array if sparse
        X = X_counts.toarray() if not isinstance(X_counts, np.ndarray) else X_counts
        y = np.array(y)

        self.classes_, class_counts = np.unique(y, return_counts=True)
        n_classes = len(self.classes_)
        n_features = X.shape[1]
        self.vocab_size_ = n_features

        # Feature counts per class
        self.feature_count_ = np.zeros((n_classes, n_features), dtype=np.float64)
        for idx, c in enumerate(self.classes_):
            self.feature_count_[idx, :] = X[y == c].sum(axis=0)

        # Laplace smoothing
        smoothed_fc = self.feature_count_ + self.alpha
        smoothed_denom = smoothed_fc.sum(axis=1).reshape(-1, 1)
        self.feature_log_prob_ = np.log(smoothed_fc) - np.log(smoothed_denom)

        # Class prior probabilities
        self.class_count_ = class_counts
        self.class_log_prior_ = np.log(class_counts) - np.log(class_counts.sum())
        return self

    def _joint_log_likelihood(self, X_counts):
        X = X_counts.toarray() if not isinstance(X_counts, np.ndarray) else X_counts
        jll = X @ self.feature_log_prob_.T + self.class_log_prior_
        return jll

    def predict(self, X_counts):
        jll = self._joint_log_likelihood(X_counts)
        indices = np.argmax(jll, axis=1)
        return self.classes_[indices]

    def predict_proba(self, X_counts):
        jll = self._joint_log_likelihood(X_counts)
        # log-sum-exp trick
        amax = np.max(jll, axis=1, keepdims=True)
        exp = np.exp(jll - amax)
        proba = exp / exp.sum(axis=1, keepdims=True)
        return proba


# ---------------------------------------------
# STEP 3: Feature Extraction using CountVectorizer
# ---------------------------------------------
vect = CountVectorizer(ngram_range=(1, 2), min_df=3)
X_train_counts = vect.fit_transform(X_train)
X_test_counts  = vect.transform(X_test)


# ---------------------------------------------
# STEP 4: Train and Evaluate the Custom NB Model
# ---------------------------------------------
nb = NaiveBayesClassifier(alpha=1.0)
nb.fit(X_train_counts, y_train)

# Predictions
y_pred = nb.predict(X_test_counts)

# Evaluation Metrics
print("=== Custom Naive Bayes Classifier (from Scratch) ===")
print("Accuracy:", round(accuracy_score(y_test, y_pred), 4))
print("Macro F1:", round(f1_score(y_test, y_pred, average='macro'), 4))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# ---------------------------------------------
# STEP 5: Confusion Matrix Visualization
# ---------------------------------------------
cm = confusion_matrix(y_test, y_pred, labels=nb.classes_)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d',
            xticklabels=nb.classes_,
            yticklabels=nb.classes_,
            cmap='Blues')
plt.xlabel("Predicted")
plt.ylabel("True")
plt.title("Confusion Matrix - Custom Multinomial Naive Bayes")
plt.show()
