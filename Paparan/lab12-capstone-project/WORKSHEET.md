# Lab 12 Student Worksheets: Planning & Tracking

Use these worksheets to organize your project work and track progress.

---

## Worksheet 1: Project Selection & Domain Choice

**Date Started:** _____________

### Your Project Information

**Project Title:** _______________________________________________

**Chosen Domain:** (Check one)
- [ ] Cybersecurity: Malware Detection
- [ ] Business Intelligence: Customer Churn Prediction
- [ ] Healthcare: Disease Risk Prediction
- [ ] NLP: Sentiment Analysis
- [ ] Computer Vision: Binary Image Classification
- [ ] Other: _________________________________

### Why You Chose This Domain

**Three reasons why this project interests you:**
1. _________________________________________________________________
2. _________________________________________________________________
3. _________________________________________________________________

**One skill you want to develop through this project:**
_________________________________________________________________

### Initial Research

**Dataset(s) you found:**
1. Name: __________________ | Source: __________________ | Size: __________
2. Name: __________________ | Source: __________________ | Size: __________
3. Name: __________________ | Source: __________________ | Size: __________

**Best choice:** __________________ (which one and why?)
_________________________________________________________________

**Key challenges you anticipate:**
1. _________________________________________________________________
2. _________________________________________________________________
3. _________________________________________________________________

---

## Worksheet 2: Risk Assessment

**Complete before starting any coding!**

### Identify Potential Risks

Fill out the following risk table:

| # | Risk | Probability | Impact | Severity | Mitigation Strategy |
|---|------|-------------|--------|----------|---------------------|
| 1 | Data not available on time | H/M/L | C/H/M | [ ] | [What will you do?] |
| 2 | Dataset too large | H/M/L | C/H/M | [ ] | [What will you do?] |
| 3 | Class imbalance | H/M/L | C/H/M | [ ] | [What will you do?] |
| 4 | Model won't converge | H/M/L | C/H/M | [ ] | [What will you do?] |
| 5 | Not enough features | H/M/L | C/H/M | [ ] | [What will you do?] |
| 6 | _________________ | H/M/L | C/H/M | [ ] | [What will you do?] |

**Legend:** Probability: H=High, M=Medium, L=Low | Impact: C=Critical, H=High, M=Medium | Severity: [Check if critical]

### Risk Mitigation Plan

**For each critical risk, write a detailed mitigation plan:**

**Critical Risk #1:** _________________________________
- **What will trigger this risk?** _________________________________
- **How will you prevent it?** _________________________________
- **Backup plan if it happens:** _________________________________
- **Who/what can help?** _________________________________

**Critical Risk #2:** _________________________________
- **What will trigger this risk?** _________________________________
- **How will you prevent it?** _________________________________
- **Backup plan if it happens:** _________________________________
- **Who/what can help?** _________________________________

---

## Worksheet 3: Feature Engineering Ideas

**Complete during EDA phase**

### Features to Create

**Domain Knowledge Questions:**
What do YOU know about this domain that a computer doesn't?

1. _________________________________________________________________
2. _________________________________________________________________
3. _________________________________________________________________

### Feature Ideas

**Brainstorm:** List 10 potential new features to create

| # | Feature Name | How to Calculate | Expected Impact | Priority |
|---|--------------|------------------|-----------------|----------|
| 1 | __________ | _________________ | High/Med/Low | 1/2/3 |
| 2 | __________ | _________________ | High/Med/Low | 1/2/3 |
| 3 | __________ | _________________ | High/Med/Low | 1/2/3 |
| 4 | __________ | _________________ | High/Med/Low | 1/2/3 |
| 5 | __________ | _________________ | High/Med/Low | 1/2/3 |
| 6 | __________ | _________________ | High/Med/Low | 1/2/3 |
| 7 | __________ | _________________ | High/Med/Low | 1/2/3 |
| 8 | __________ | _________________ | High/Med/Low | 1/2/3 |
| 9 | __________ | _________________ | High/Med/Low | 1/2/3 |
| 10 | __________ | _________________ | High/Med/Low | 1/2/3 |

**Top 3 Priority Features to Implement:**
1. ___________________________
2. ___________________________
3. ___________________________

**Why these three?** _________________________________________________________________

---

## Worksheet 4: Experiment Tracking

**Keep detailed records of every model experiment**

### Experiment Log Template

**Experiment #1: Baseline Model**

- **Date:** ________________
- **Model Type:** ________________
- **Hyperparameters:** _______________________________________________
- **Features Used:** [#features] ________________________________________
- **Preprocessing:** _______________________________________________
- **Training Time:** _________ minutes
- **Results:**
  - Accuracy: _______
  - Precision: _______
  - Recall: _______
  - F1-Score: _______
  - AUC-ROC: _______
- **Notes:** _______________________________________________
- **Next Step:** _______________________________________________

---

**Experiment #2: [Model Name]**

- **Date:** ________________
- **Model Type:** ________________
- **Hyperparameters:** _______________________________________________
- **Features Used:** [#features] ________________________________________
- **Preprocessing:** _______________________________________________
- **Training Time:** _________ minutes
- **Results:**
  - Accuracy: _______
  - Precision: _______
  - Recall: _______
  - F1-Score: _______
  - AUC-ROC: _______
- **Notes:** _______________________________________________
- **Next Step:** _______________________________________________

---

**Experiment #3: [Model Name]**

- **Date:** ________________
- **Model Type:** ________________
- **Hyperparameters:** _______________________________________________
- **Features Used:** [#features] ________________________________________
- **Preprocessing:** _______________________________________________
- **Training Time:** _________ minutes
- **Results:**
  - Accuracy: _______
  - Precision: _______
  - Recall: _______
  - F1-Score: _______
  - AUC-ROC: _______
- **Notes:** _______________________________________________
- **Next Step:** _______________________________________________

---

## Worksheet 5: Hyperparameter Tuning Results

### Grid Search / RandomSearch Results

**Model Selected for Tuning:** _________________________________

**Parameter Grid Tested:**

| Parameter | Range Tested | Best Value | Impact |
|-----------|--------------|-----------|--------|
| _________ | ____________ | _________ | High/Med/Low |
| _________ | ____________ | _________ | High/Med/Low |
| _________ | ____________ | _________ | High/Med/Low |
| _________ | ____________ | _________ | High/Med/Low |

### Tuning Results

**Baseline (no tuning):**
- Accuracy: _______
- F1-Score: _______

**After Tuning:**
- Accuracy: _______
- F1-Score: _______

**Improvement:** +_______ points (______% improvement)

**Best Hyperparameters Found:**
```python
{
  'param1': value1,
  'param2': value2,
  'param3': value3,
}
```

---

## Worksheet 6: Model Comparison Summary

### Final Model Comparison

**Compare all models you trained:**

| Rank | Model | Accuracy | Precision | Recall | F1 | AUC | Training Time | Notes |
|------|-------|----------|-----------|--------|----|----|---|---|
| 1 | ______ | ___ | ___ | ___ | ___ | ___ | ____ | ________ |
| 2 | ______ | ___ | ___ | ___ | ___ | ___ | ____ | ________ |
| 3 | ______ | ___ | ___ | ___ | ___ | ___ | ____ | ________ |
| 4 | ______ | ___ | ___ | ___ | ___ | ___ | ____ | ________ |

### Model Selection Decision

**Best Model:** _________________________________

**Why this model was selected:**
1. ___________________________________________________________________
2. ___________________________________________________________________
3. ___________________________________________________________________

**Trade-offs considered:**
- Accuracy vs Interpretability: _____________________________________
- Speed vs Performance: _____________________________________________
- Complexity vs Results: ___________________________________________

---

## Worksheet 7: Cross-Validation Results

### K-Fold Cross-Validation Summary

**Model:** _________________________________
**K-Folds:** _____
**Validation Strategy:** _________________________________

| Fold | Accuracy | Precision | Recall | F1 | Notes |
|------|----------|-----------|--------|-------|-------|
| 1 | ___ | ___ | ___ | ___ | ______ |
| 2 | ___ | ___ | ___ | ___ | ______ |
| 3 | ___ | ___ | ___ | ___ | ______ |
| 4 | ___ | ___ | ___ | ___ | ______ |
| 5 | ___ | ___ | ___ | ___ | ______ |
| **Mean** | **___** | **___** | **___** | **___** | ______ |
| **Std Dev** | **±___** | **±___** | **±___** | **±___** | ______ |

### Overfitting Check

**Training Accuracy:** _______
**Validation Accuracy:** _______
**Test Accuracy:** _______

**Overfitting Assessment:**
- Train-Test Gap: _______ percentage points
- Is gap <15%? [ ] Yes [ ] No
- Assessment: _________________________________________________________________

---

## Worksheet 8: Error Analysis

### Where Does Your Model Fail?

**Analyze False Positives:**
- Count: _______
- Common characteristics: _________________________________________________________________
- Why does model make these mistakes? _________________________________________________________________

**Analyze False Negatives:**
- Count: _______
- Common characteristics: _________________________________________________________________
- Why does model miss these? _________________________________________________________________

### Error Patterns

| Error Type | Count | % of Errors | Pattern | Root Cause |
|-----------|-------|-------------|---------|-----------|
| False Positive | _____ | ____% | _____________ | ________________ |
| False Negative | _____ | ____% | _____________ | ________________ |

### Implications

**What does this error pattern mean for production use?**
_________________________________________________________________
_________________________________________________________________

**How can you mitigate these errors?**
_________________________________________________________________
_________________________________________________________________

---

## Worksheet 9: Deployment Checklist

### Pre-Deployment Tasks

- [ ] Model trained and saved
- [ ] Preprocessor trained and saved
- [ ] Model metrics documented
- [ ] FastAPI app written and tested
- [ ] API endpoints working (test with curl or Postman)
- [ ] Docker image builds successfully
- [ ] Docker container runs without errors
- [ ] Health check endpoint responds
- [ ] Model card completed
- [ ] README updated
- [ ] All dependencies in requirements.txt

### API Testing

**Test Cases Completed:**

1. **Health Check**
   - Endpoint: `/health`
   - Expected: 200 OK
   - Actual: [ ] Pass [ ] Fail

2. **Info Endpoint**
   - Endpoint: `/info`
   - Expected: Model metadata returned
   - Actual: [ ] Pass [ ] Fail

3. **Single Prediction**
   - Input: [Sample input]
   - Expected: Valid prediction with confidence
   - Actual: [ ] Pass [ ] Fail

4. **Batch Prediction**
   - Input: [Batch of 10 samples]
   - Expected: 10 predictions returned
   - Actual: [ ] Pass [ ] Fail

5. **Error Handling**
   - Input: [Invalid input]
   - Expected: 400/500 error with message
   - Actual: [ ] Pass [ ] Fail

### Docker Testing

- [ ] Image builds: `docker build -t capstone:v1 .`
- [ ] Container runs: `docker run -p 8000:8000 capstone:v1`
- [ ] API accessible at http://localhost:8000
- [ ] Swagger docs accessible at http://localhost:8000/docs

---

## Worksheet 10: Presentation Preparation

### Presentation Outline

**Slide 1: Title**
- Project title: _________________________________
- Your name: _________________________________

**Slide 2-3: Problem Statement** (what and why)
- Main points:
  1. _________________________________________________________________
  2. _________________________________________________________________
  3. _________________________________________________________________

**Slide 4: Data Overview**
- Dataset size: _________ samples x _________ features
- Class distribution: _________________________________________________________________
- Key characteristics: _________________________________________________________________

**Slide 5-6: Approach** (how you solved it)
- Algorithm: _________________________________
- Key preprocessing: _________________________________________________________________
- Feature engineering: _________________________________________________________________

**Slide 7-9: Results** (what you found)
- Best model performance:
  - Accuracy: _____ | Precision: _____ | Recall: _____ | F1: _____
- Model comparison table/chart
- Diagnostic plots (confusion matrix, ROC curve)

**Slide 10: Feature Importance**
- Top 5 important features:
  1. _________________ (importance: _____%)
  2. _________________ (importance: _____%)
  3. _________________ (importance: _____%)
  4. _________________ (importance: _____%)
  5. _________________ (importance: _____%)

**Slide 11: Deployment & Demo**
- API architecture diagram
- Response time: _______ ms
- Demo live or screenshot

**Slide 12: Limitations**
- Known limitation 1: _________________________________________________________________
- Known limitation 2: _________________________________________________________________
- Known limitation 3: _________________________________________________________________

**Slide 13: Future Work**
- Improvement 1: _________________________________________________________________
- Improvement 2: _________________________________________________________________
- Improvement 3: _________________________________________________________________

**Slide 14: Conclusion**
- Key takeaway: _________________________________________________________________

### Practice Schedule

- [ ] Practice 1: _____________ (Date: _____) | Duration: _____ min | Notes: _____________
- [ ] Practice 2: _____________ (Date: _____) | Duration: _____ min | Notes: _____________
- [ ] Practice 3: _____________ (Date: _____) | Duration: _____ min | Notes: _____________

### Anticipated Questions & Answers

**Q: Why did you choose this model?**
A: _________________________________________________________________

**Q: How does this compare to existing solutions?**
A: _________________________________________________________________

**Q: What's the biggest limitation?**
A: _________________________________________________________________

**Q: How would you improve this in the future?**
A: _________________________________________________________________

**Q: Why is accuracy/recall the right metric?**
A: _________________________________________________________________

---

## Worksheet 11: Weekly Progress Tracker

### Week 13 Progress

**Monday:**
- [ ] Project proposal finalized
- [ ] Data loaded and examined
- [ ] Initial EDA started
- **Blockers:** _________________________________________________________________

**Wednesday:**
- [ ] EDA completed
- [ ] Data preprocessing done
- [ ] Baseline model trained
- [ ] Results: Accuracy ______, F1 ______
- **Blockers:** _________________________________________________________________

**Friday (Homework):**
- [ ] Feature engineering started
- [ ] 2-3 additional models trained
- [ ] Model comparison started
- **Blockers:** _________________________________________________________________

### Week 14 Progress

**Monday:**
- [ ] Model selection finalized
- [ ] Hyperparameter tuning completed
- [ ] FastAPI app written
- [ ] Docker container working
- **Blockers:** _________________________________________________________________

**Wednesday:**
- [ ] Technical report drafted
- [ ] Model card completed
- [ ] Presentation slides ready
- [ ] Demo tested and working
- **Blockers:** _________________________________________________________________

**Friday:**
- [ ] Final presentation delivered
- [ ] All deliverables submitted
- [ ] Celebration! 🎉

---

## Worksheet 12: Final Submission Checklist

**Before submitting, verify you have completed:**

### Code & Implementation
- [ ] Jupyter notebook with complete pipeline
- [ ] All code runs without errors
- [ ] requirements.txt with pinned versions
- [ ] No hardcoded paths or credentials
- [ ] Code properly commented and documented

### Data & Analysis
- [ ] Dataset loaded and described
- [ ] EDA report with insights
- [ ] Data preprocessing documented
- [ ] Train/val/test splits properly created
- [ ] All data issues (missing, outliers) handled

### Model Development
- [ ] Baseline model trained and documented
- [ ] 3+ models compared systematically
- [ ] Hyperparameter tuning performed
- [ ] Cross-validation results reported
- [ ] Best model selected with justification
- [ ] Feature importance analyzed

### Evaluation & Results
- [ ] Multiple metrics computed and reported
- [ ] Results compared to baseline
- [ ] Error analysis completed
- [ ] Diagnostic plots created
- [ ] Results reproducible

### Deployment
- [ ] Model saved (pickle/joblib)
- [ ] Preprocessor saved
- [ ] FastAPI app working
- [ ] Docker image builds and runs
- [ ] Health check implemented
- [ ] API documentation complete

### Documentation
- [ ] Project Proposal completed
- [ ] README.md comprehensive
- [ ] Model Card filled out completely
- [ ] Technical Report finished (15-25 pages)
- [ ] EDA Report documented
- [ ] All code is well-commented

### Presentation
- [ ] Slides prepared (14-16 slides)
- [ ] Presentation practiced (3+ times)
- [ ] Demo working or backed up with screenshots
- [ ] Q&A answers prepared
- [ ] Presentation file saved and tested

### Git & Version Control
- [ ] All files committed
- [ ] Clean commit history with meaningful messages
- [ ] .gitignore properly configured
- [ ] No large files in repository
- [ ] README.md at repository root

### Final Quality Check
- [ ] Code runs end-to-end without errors
- [ ] Results are reproducible
- [ ] No warnings or errors in execution
- [ ] All metrics reported accurately
- [ ] Professional presentation quality
- [ ] Submitted before deadline

---

## Notes & Additional Observations

**Things that went well:**
1. _________________________________________________________________
2. _________________________________________________________________
3. _________________________________________________________________

**Things that were challenging:**
1. _________________________________________________________________
2. _________________________________________________________________
3. _________________________________________________________________

**Key learnings from this project:**
1. _________________________________________________________________
2. _________________________________________________________________
3. _________________________________________________________________

**Skills developed:**
1. _________________________________________________________________
2. _________________________________________________________________
3. _________________________________________________________________

**Time spent by phase (estimate hours):**
- Planning & Proposal: _______ hours
- EDA & Data Prep: _______ hours
- Model Development: _______ hours
- Evaluation & Analysis: _______ hours
- Deployment: _______ hours
- Documentation: _______ hours
- Presentation: _______ hours
- **Total:** _______ hours

**Would you do anything differently?**
_________________________________________________________________
_________________________________________________________________

---

**Completed By:** _________________________ **Date:** _____________

**Instructor Sign-Off:** _________________________ **Date:** _____________
