# phishing-email-detector
AI-powered phishing email detection system developed by Nexus Team for the Samsung Innovation Campus Graduation Project.

## Run the integrated application

```powershell
python -m pip install -r requirements.txt
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

In a second terminal:

```powershell
cd frontend
npm ci
npm run dev
```

For deployment, set `VITE_API_BASE_URL` to the public backend origin before
building the frontend, and set backend `CORS_ORIGINS` to the public frontend
origin (multiple origins are comma-separated). The browser extension also needs
its `API_BASE_URL`, `NEXUS_APP_URL`, and `manifest.json` host permissions updated
from localhost to the deployed origins.

The extension now defaults to the live API. Demo fixtures must never be enabled
in a production package.
# phishing-email-detector
AI-powered phishing email detection system developed by Nexus Team for the Samsung Innovation Campus Graduation Project.

# SIC Capstone Project

An AI-based project developed as part of the **Samsung Innovation Campus (SIC) Capstone Project**.

The project is developed collaboratively by a six-member team, with each member responsible for a specific technical module.

The repository follows a structured Git workflow where every major project module has its own dedicated feature branch. All completed work is reviewed and integrated into the stable `main` branch through Pull Requests.

---

## Project Overview

The system is designed around multiple AI and software engineering components, including:

- Dataset preparation and preprocessing
- Natural Language Processing (NLP)
- Machine Learning
- URL and Email Header Analysis
- Backend and API development
- Frontend and Dashboard development

Each component is developed independently before being integrated into the final system.

---

## Team Responsibilities

| Team Member | Responsibility | Branch |
|---|---|---|
| Eng. Heba | Dataset & Data Preprocessing | `feature/data-preprocessing` |
| Eng. Buthaina | NLP & Text Features | `feature/nlp` |
| Eng. Suliman | Machine Learning | `feature/ml` |
| Eng. Rayan | URL & Email Header Analysis | `feature/url-analysis` |
| Eng. Anas | Backend & API | `feature/backend` |
| Eng. Amal | Frontend & Dashboard | `feature/frontend` |

---

## Branch Structure

The repository contains one main integration branch and six dedicated feature branches.

```text
main
│
├── feature/data-preprocessing
│
├── feature/nlp
│
├── feature/ml
│
├── feature/url-analysis
│
├── feature/backend
│
└── feature/frontend
```

### `main`

The `main` branch represents the stable and integrated version of the project.

Direct development on `main` should be avoided.

Completed work from feature branches must be integrated into `main` through a **Pull Request** after review.

---

## Project Workflow Overview

<p align="center">
  <img src="docs/images/project-workflow.jpg" alt="Nexus Project Structure, Branches and Git Workflow" width="750">
</p>

<p align="center">
  <em>Visual overview of the project structure, team branches, and Git collaboration workflow.</em>
</p>

---

# Project Modules

## 1. Dataset & Data Preprocessing

**Responsible:** Eng. Heba
**Branch:** `feature/data-preprocessing`

This module is responsible for preparing the dataset before it is used by the AI and Machine Learning components.

Main responsibilities include:

- Dataset collection and organization
- Data inspection
- Data cleaning
- Handling missing or invalid values
- Removing unnecessary or duplicate records
- Data transformation
- Label preparation
- Dataset balancing when required
- Preparing training and testing datasets
- Exporting cleaned data for other modules

The output of this module should provide a clean and reliable dataset that can be consumed by the NLP and Machine Learning modules.

---

## 2. NLP & Text Features

**Responsible:** Eng. Buthaina
**Branch:** `feature/nlp`

This module is responsible for processing textual content and extracting useful features from text.

Main responsibilities include:

- Text cleaning
- Text normalization
- Tokenization
- Removing unnecessary characters
- Handling stop words when appropriate
- Text feature extraction
- Keyword analysis
- Statistical text features
- Preparing text features for Machine Learning
- Converting textual information into model-compatible representations

The extracted NLP features will later be combined with other features and used by the Machine Learning module.

---

## 3. Machine Learning

**Responsible:** Eng. Sulaiman
**Branch:** `feature/ml`

This module is responsible for building, training, evaluating, and selecting the Machine Learning model.

Main responsibilities include:

- Loading prepared features
- Splitting data into training and testing sets
- Training Machine Learning models
- Comparing multiple algorithms
- Hyperparameter tuning when required
- Evaluating model performance
- Measuring classification metrics
- Selecting the best-performing model
- Saving the trained model
- Preparing the prediction pipeline
- Providing model outputs for backend integration

Important evaluation metrics may include:

- Accuracy
- Precision
- Recall
- F1-Score
- Confusion Matrix
- ROC-AUC when applicable

Model performance should be evaluated carefully, especially when working with imbalanced datasets.

---

## 4. URL & Email Header Analysis

**Responsible:** Eng. Rayan
**Branch:** `feature/url-analysis`

This module is responsible for extracting and analyzing technical features related to URLs and email metadata.

Main responsibilities include:

- URL extraction
- URL structure analysis
- Domain analysis
- URL length analysis
- Suspicious character detection
- IP-based URL detection
- Subdomain analysis
- Protocol analysis
- Email header parsing
- Sender information extraction
- Email metadata analysis
- Extraction of useful technical features

The extracted features should be transformed into a structured format that can be used by the Machine Learning model.

---

## 5. Backend & API

**Responsible:** Eng. Anas
**Branch:** `feature/backend`

This module is responsible for integrating the different system components and exposing their functionality through a backend API.

Main responsibilities include:

- Backend architecture
- API development
- Request validation
- Input processing
- Integration with the trained Machine Learning model
- Integration with NLP features
- Integration with URL analysis
- Prediction processing
- Response formatting
- Error handling
- API documentation
- Communication with the frontend
- System integration

The backend acts as the main communication layer between the AI components and the user interface.

Example architecture:

```text
Frontend / Dashboard
        │
        ▼
     Backend API
        │
        ├── NLP Module
        │
        ├── URL Analysis Module
        │
        └── Machine Learning Model
        │
        ▼
 Prediction Result
```

---

## 6. Frontend & Dashboard

**Responsible:** Eng. Amal
**Branch:** `feature/frontend`

This module is responsible for building the user interface and presenting system results clearly.

Main responsibilities include:

- Dashboard development
- User interface design
- Backend API integration
- Input forms
- Analysis result presentation
- Prediction visualization
- Statistics display
- Charts and graphs
- Loading and error states
- Responsive interface
- Improving user experience

The frontend should communicate with the backend through the defined API endpoints rather than directly accessing Machine Learning components.

---

# Git Development Workflow

Each team member has a dedicated branch.

Development should be performed only inside the branch assigned to that member.

The basic workflow is:

```text
Feature Branch
      │
      │ Development
      ▼
   Commit
      │
      ▼
    Push
      │
      ▼
Pull Request
      │
      ▼
    Review
      │
      ▼
     main
```

---

## Getting the Repository

Clone the repository:

```bash
git clone <repository-url>
```

Enter the project directory:

```bash
cd <repository-name>
```

Fetch all remote branches:

```bash
git fetch origin
```

---

## Switching to Your Branch

Each team member must switch to their assigned branch before starting development.

### Dataset & Data Preprocessing

```bash
git checkout feature/data-preprocessing
```

### NLP

```bash
git checkout feature/nlp
```

### Machine Learning

```bash
git checkout feature/ml
```

### URL Analysis

```bash
git checkout feature/url-analysis
```

### Backend

```bash
git checkout feature/backend
```

### Frontend

```bash
git checkout feature/frontend
```

---

# Before Starting Work

Before starting new development, always make sure your local branch is synchronized with the remote repository.

Example:

```bash
git checkout feature/ml
git pull origin feature/ml
```

This reduces the possibility of working on an outdated version of the branch.

---

# Saving Your Changes

After completing a logical part of your work, check the modified files:

```bash
git status
```

Add the required files:

```bash
git add .
```

Create a commit:

```bash
git commit -m "feat: add initial model training pipeline"
```

Push the changes:

```bash
git push origin feature/ml
```

Replace `feature/ml` with your assigned branch.

---

# Commit Message Convention

Commit messages should be short, descriptive, and explain what was changed.

The recommended format is:

```text
type: short description
```

Common commit types:

| Type | Purpose |
|---|---|
| `feat` | Add a new feature |
| `fix` | Fix a bug |
| `refactor` | Improve existing code without changing functionality |
| `docs` | Documentation changes |
| `test` | Add or modify tests |
| `data` | Dataset-related changes |
| `model` | Machine Learning model changes |
| `chore` | Maintenance or configuration changes |

Examples:

```bash
git commit -m "data: clean missing dataset values"
```

```bash
git commit -m "feat: add text preprocessing pipeline"
```

```bash
git commit -m "model: train random forest classifier"
```

```bash
git commit -m "feat: add URL feature extraction"
```

```bash
git commit -m "feat: create prediction API endpoint"
```

```bash
git commit -m "feat: create dashboard results page"
```

```bash
git commit -m "fix: handle invalid API requests"
```

```bash
git commit -m "docs: update project documentation"
```

---

# Pull Request Workflow

When a feature or important development stage is ready, create a **Pull Request** from your feature branch into:

```text
main
```

Example:

```text
feature/ml
    │
    ▼
Pull Request
    │
    ▼
main
```

The Pull Request should clearly explain:

1. What was implemented
2. What files or modules were changed
3. How the implementation was tested
4. Whether another module is affected
5. Any known limitations or pending work

---

# Branch Rules

To keep the project stable and prevent conflicts, all team members should follow these rules.

### Rule 1 — Do Not Develop Directly on `main`

Do not implement features directly inside:

```text
main
```

All development must happen in the appropriate feature branch.

---

### Rule 2 — Use Your Assigned Branch

Each member should primarily work inside their assigned branch.

Example:

```text
Eng. Heba
└── feature/data-preprocessing

Eng. Buthaina
└── feature/nlp

Eng. Sulaiman
└── feature/ml

Eng. Rayan
└── feature/url-analysis

Eng. Anas
└── feature/backend

Eng. Amal
└── feature/frontend
```

---

### Rule 3 — Do Not Modify Another Member's Branch Without Coordination

If work from another module is required, coordinate with the member responsible for that module first.

Avoid directly changing another member's branch unless it has been discussed and agreed upon.

---

### Rule 4 — Pull Before Starting

Always pull the latest branch changes before starting new work.

```bash
git pull origin <branch-name>
```

---

### Rule 5 — Push Regularly

Do not keep important work only on your local computer.

Push completed and stable development stages to GitHub regularly.

---

### Rule 6 — Keep Commits Focused

Each commit should represent one logical change.

Avoid mixing unrelated changes into one large commit.

Good:

```text
feat: add URL length feature
```

Better than:

```text
update project
```

---

### Rule 7 — Use Pull Requests

Feature branches should be integrated into `main` through Pull Requests.

This provides:

- Code review
- Change tracking
- Conflict detection
- Better project history
- Safer integration

---

# Integration Between Modules

Although each module is developed separately, the final system depends on communication between several components.

Expected integration flow:

```text
Dataset
   │
   ▼
Data Preprocessing
   │
   ├───────────────┐
   ▼               ▼
NLP Features    URL/Header Features
   │               │
   └───────┬───────┘
           ▼
     Feature Dataset
           │
           ▼
   Machine Learning
           │
           ▼
      Trained Model
           │
           ▼
       Backend API
           │
           ▼
 Frontend / Dashboard
```

Because modules depend on each other, changes to shared data structures, feature names, API formats, or model inputs should be communicated with the team before implementation.

---

# Module Contracts

To simplify integration, modules should exchange structured and predictable outputs.

For example:

```text
Data Preprocessing
        ↓
Clean Dataset

NLP
        ↓
Text Features

URL Analysis
        ↓
URL/Header Features

Machine Learning
        ↓
Prediction Model

Backend
        ↓
API Response

Frontend
        ↓
User Visualization
```

Changes to module outputs should be documented and communicated to dependent modules.

---

# Recommended Repository Structure

As the project grows, the repository may follow a structure similar to:

```text
project-root/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── README.md
│
├── preprocessing/
│
├── nlp/
│
├── url_analysis/
│
├── ml/
│
├── backend/
│
├── frontend/
│
├── notebooks/
│
├── tests/
│
├── docs/
│
├── requirements.txt
│
├── .gitignore
│
└── README.md
```

This structure may evolve as the project architecture becomes more stable.

---

# Collaboration Guidelines

Good communication is required whenever a change affects more than one module.

Examples include:

- Changing dataset column names
- Adding or removing Machine Learning features
- Changing model input structure
- Changing model output format
- Changing API request fields
- Changing API response structure
- Changing frontend/backend contracts

Before introducing breaking changes, inform the team member responsible for the affected module.

---

# Code Quality

All contributors should aim to keep the project:

- Modular
- Readable
- Maintainable
- Reusable
- Testable
- Clearly documented

Avoid unnecessary duplication and keep module responsibilities separated.

---

# Documentation

Important technical decisions should be documented inside the repository.

Documentation may include:

```text
docs/
├── architecture.md
├── dataset.md
├── model.md
├── api.md
└── integration.md
```

Documentation files can be introduced gradually as the project develops.

---

# Security

Do not commit sensitive information to GitHub.

Never commit files containing:

- Passwords
- API keys
- Access tokens
- Private credentials
- Environment secrets
- Personal sensitive information

Environment variables should be stored in local configuration files such as:

```text
.env
```

The `.env` file must be excluded using:

```text
.gitignore
```

Example:

```gitignore
.env
.venv/
venv/
__pycache__/
*.pyc
```

---

# Large Files and Datasets

Large datasets, trained models, generated artifacts, or unnecessary binary files should not automatically be committed to the repository.

Before uploading large files, coordinate with the team and determine the appropriate storage strategy.

This helps keep the Git repository lightweight and manageable.

---

# Conflict Resolution

If Git reports a merge conflict:

1. Do not randomly delete conflicting code.
2. Identify which modules are affected.
3. Contact the responsible team member if necessary.
4. Review both versions of the conflicting code.
5. Resolve the conflict carefully.
6. Test the project after resolution.
7. Commit the resolved changes.

For complex conflicts involving shared functionality, resolve them collaboratively.

---

# Project Development Principles

The team follows these core principles:

```text
Independent Development
        +
Clear Responsibilities
        +
Controlled Integration
        +
Code Review
        +
Documentation
        =
Stable Project
```

The objective of the branching strategy is not only to separate development work, but also to make collaboration, integration, and project tracking easier throughout the Capstone Project.

---

## Team

**Samsung Innovation Campus — SIC Capstone Team**

| Member | Area |
|---|---|
| Eng. Heba | Dataset & Data Preprocessing |
| Eng. Buthaina | NLP & Text Features |
| Eng. Sulaiman | Machine Learning |
| Eng. Rayan | URL & Email Header Analysis |
| Eng. Anas | Backend & API |
| Eng. Amal | Frontend & Dashboard |

---

## Repository Policy

```text
Stable Code        → main
Data Work          → feature/data-preprocessing
NLP Work           → feature/nlp
ML Work            → feature/ml
URL Analysis       → feature/url-analysis
Backend Work       → feature/backend
Frontend Work      → feature/frontend
```

**All team members are responsible for keeping their branches organized, synchronized, and ready for integration.**

---

## License

This repository is developed for the **Samsung Innovation Campus Capstone Project**.

Project usage, distribution, and licensing terms may be defined by the team as the project progresses.

---

## Copyright

© 2026 SIC Capstone Team. All Rights Reserved.

All rights to this project are collectively reserved to all members of the team.
