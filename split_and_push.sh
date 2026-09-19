#!/usr/bin/env bash
# Splits the pending single commit (c0d3248) into 3 focused commits + pushes.
# Run from the repo root: bash split_and_push.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

FILE=notebooks/url_analysis/pj1.py
cp "$FILE" "$FILE.full"   # snapshot of the final, complete script

# ---- 0) Undo the single oversized local commit ----
# Safe: git status shows this commit is only local, never pushed to origin yet.
git reset HEAD~1

# ---- 0b) Track large generated ML artifacts with Git LFS instead of committing them raw ----
# (train_data.csv is 184MB - over GitHub's 100MB hard limit - so this is required, not optional)
git lfs track \
  "notebooks/url_analysis/artifacts/*.csv" \
  "notebooks/url_analysis/artifacts/*.npz" \
  "notebooks/url_analysis/artifacts/*.npy" \
  "notebooks/url_analysis/artifacts/*.pkl" \
  "/tfidf_vectorizer.pkl"
git add .gitattributes

# ============================================================
# COMMIT 1 — data-prep fixes + TF-IDF/chi2 exploratory word analysis
# (everything up to, but not including, the PHISHING_KEYWORDS section)
# ============================================================
awk '/^#most common words in legitimate and phishing emails/{exit} {print}' "$FILE.full" > "$FILE"
git add "$FILE" .gitattributes
git commit -m "Fix data-prep bugs; add TF-IDF and chi2 discriminative word analysis

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
git push origin feature/nlp

# ============================================================
# COMMIT 2 — phishing keyword counts + statistical text features
# (everything up to, but not including, the final TF-IDF vectorization section)
# ============================================================
awk '/^#using TF-IDF vectorization to convert the text data into numerical features for machine learning models/{exit} {print}' "$FILE.full" > "$FILE"
git add "$FILE"
git commit -m "Add phishing keyword counts and statistical text features

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
git push origin feature/nlp

# ============================================================
# COMMIT 3 — final TF-IDF feature matrix + save train/test artifacts (LFS-tracked)
# ============================================================
cp "$FILE.full" "$FILE"
rm "$FILE.full"
git add "$FILE" \
  notebooks/url_analysis/artifacts/*.csv \
  notebooks/url_analysis/artifacts/*.npz \
  notebooks/url_analysis/artifacts/*.npy \
  notebooks/url_analysis/artifacts/*.pkl \
  tfidf_vectorizer.pkl
git commit -m "Build final TF-IDF feature matrix and save train/test artifacts via Git LFS

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
git push origin feature/nlp

echo "Done. 3 commits pushed to origin/feature/nlp."
