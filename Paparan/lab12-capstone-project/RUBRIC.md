# Lab 12 Capstone Project: Grading Rubric

**Total Points: 100**

---

## Category 1: Problem Definition & Planning (15 points)

### 1.1 Problem Statement (5 points)

| Excellent (5) | Good (4) | Fair (2) | Poor (0) |
|---|---|---|---|
| Clear, specific, measurable problem statement with strong business justification. SMART criteria explicitly met. Problem is well-scoped and achievable within timeline. | Clear problem statement with most SMART criteria. Good business justification. Scope is mostly realistic. | Problem statement is vague or over-scoped. Weak business justification. SMART criteria partially addressed. | Problem ill-defined, not measurable, or unrealistic scope. No clear success criteria. |

**Checklist:**
- [ ] Problem is specific (not just "build a model")
- [ ] Problem is measurable (has quantifiable metrics)
- [ ] Problem is achievable (realistic with available resources)
- [ ] Problem is relevant (clear business value)
- [ ] Problem is time-bound (specific deadline)
- [ ] Business context clearly explained

---

### 1.2 Data Planning (5 points)

| Excellent (5) | Good (4) | Fair (2) | Poor (0) |
|---|---|---|---|
| Comprehensive data strategy: source identified, size known, quality issues documented, access timeline clear. Privacy/ethical considerations addressed. | Good data plan: source and size known, basic quality check done. Access timeline reasonable. | Minimal data planning: source identified but details missing. Data quality not assessed. | No data planning. Data source unclear or unavailable. |

**Checklist:**
- [ ] Data source clearly identified
- [ ] Data size and characteristics known (n samples, m features)
- [ ] Data quality issues documented (missing values, outliers)
- [ ] Data access timeline confirmed
- [ ] Privacy/ethical considerations addressed (PII, GDPR, bias)
- [ ] Data dictionary or feature descriptions provided

---

### 1.3 Feasibility & Timeline (5 points)

| Excellent (5) | Good (4) | Fair (2) | Poor (0) |
|---|---|---|---|
| Detailed, realistic timeline with milestones and resource allocation. Risk assessment thorough with mitigation strategies. Scope appropriately sized. | Reasonable timeline with clear milestones. Basic risk assessment. Mostly realistic scope. | Vague timeline or unrealistic scope. Limited risk assessment. Timeline may be too tight. | No timeline or completely unrealistic. No risk assessment. Over-scoped. |

**Checklist:**
- [ ] Timeline broken into weekly milestones
- [ ] Realistic time estimates for each phase
- [ ] Key deliverables clearly identified
- [ ] Risk assessment completed (5+ risks identified)
- [ ] Mitigation strategies defined for each risk
- [ ] Scope clearly bounded (what's IN, what's OUT)
- [ ] Resource requirements identified

---

## Category 2: Data & Analysis (15 points)

### 2.1 Data Quality (5 points)

| Excellent (5) | Good (4) | Fair (2) | Poor (0) |
|---|---|---|---|
| Dataset is clean and well-documented. Missing values, duplicates, and outliers properly handled and justified. Data types correct. No obvious quality issues. | Dataset mostly clean. Most quality issues addressed. Minor documentation gaps. | Dataset has quality issues (missing values, wrong types). Incomplete handling. Limited documentation. | Dataset not cleaned. Multiple quality issues unaddressed. No documentation. |

**Checklist:**
- [ ] Missing values assessed and handled appropriately
- [ ] Duplicates identified and removed
- [ ] Outliers identified and decision made (keep/remove/flag)
- [ ] Data types correct (numerical vs categorical)
- [ ] Value ranges reasonable and validated
- [ ] Data quality report created
- [ ] All decisions documented

---

### 2.2 EDA & Insights (5 points)

| Excellent (5) | Good (4) | Fair (2) | Poor (0) |
|---|---|---|---|
| Comprehensive EDA with multiple perspectives (univariate, bivariate, multivariate). Clear insights extracted. Visualizations are informative. Hypotheses for modeling generated. | Good EDA covering main variables. Decent visualizations. Some insights identified. | Basic EDA (distributions only). Limited insights. Few/poor visualizations. | Minimal or missing EDA. No insights. No visualizations. |

**Checklist:**
- [ ] Univariate analysis (distributions, statistics)
- [ ] Bivariate analysis (correlations, target relationship)
- [ ] Multivariate analysis (feature interactions, clustering)
- [ ] Class distribution analyzed (if classification)
- [ ] Top 5+ insights documented
- [ ] Visualizations clear and well-labeled
- [ ] Insights directly inform modeling decisions

---

### 2.3 Feature Engineering (5 points)

| Excellent (5) | Good (4) | Fair (2) | Poor (0) |
|---|---|---|---|
| 5+ domain-informed features created with clear rationale. Feature interactions explored. Impact of new features validated. Dimensionality reduction considered. | 3-4 thoughtful features created. Impact somewhat validated. Reasonable approach. | 1-2 basic features. Limited justification. No validation of impact. | No new features created or only trivial features. |

**Checklist:**
- [ ] Domain knowledge applied in feature creation
- [ ] At least 3 new features created
- [ ] Rationale documented for each feature
- [ ] Impact of features on target validated
- [ ] Highly correlated features identified
- [ ] Scaling/normalization strategy decided
- [ ] Categorical encoding strategy chosen

---

## Category 3: Model Development (25 points)

### 3.1 Approach & Algorithm Selection (8 points)

| Excellent (8) | Good (6) | Fair (4) | Poor (0) |
|---|---|---|---|
| 4+ diverse algorithms tested systematically. Clear justification for algorithm choice. Baseline established and compared. Advanced techniques applied appropriately. | 3 algorithms tested. Reasonable algorithm selection. Baseline present. Some justification. | 2 algorithms tried. Limited justification. Weak baseline. | Only 1 model or no clear selection criteria. |

**Checklist:**
- [ ] Baseline model implemented first (simple algorithm)
- [ ] 3+ advanced models trained and compared
- [ ] Algorithm selection justified (tree-based, linear, ensemble, etc.)
- [ ] Domain-appropriate algorithms chosen
- [ ] Model complexity vs performance trade-off considered
- [ ] Comparison table created with metrics
- [ ] Best model selected with clear reasoning

---

### 3.2 Validation Strategy (9 points)

| Excellent (9) | Good (7) | Fair (5) | Poor (0) |
|---|---|---|---|
| Proper train/val/test split with stratification (if needed). K-fold CV performed (5+). No data leakage. Validation strategy appropriate for data type (time series split if needed). Results stable across folds. | Good train/val/test split. K-fold CV done (usually 5). No obvious leakage. | Basic train/test split (no validation set). Limited CV. Possible data leakage issues. | Train/test contamination. Single split only. Potential leakage. |

**Checklist:**
- [ ] Train/validation/test split (70/15/15 or similar)
- [ ] Stratified splitting for imbalanced data
- [ ] K-fold cross-validation (5-10 folds)
- [ ] No data leakage (scaling, preprocessing on train only)
- [ ] Proper handling of time series (temporal split if applicable)
- [ ] Validation metrics consistent across folds
- [ ] Final evaluation only on held-out test set

---

### 3.3 Hyperparameter Tuning (8 points)

| Excellent (8) | Good (6) | Fair (4) | Poor (0) |
|---|---|---|---|
| Systematic tuning (GridSearch/RandomSearch). Multiple hyperparameters optimized. Tuning done on validation set, not test set. Results show clear improvement. | Good tuning approach. 3-4 hyperparameters tuned. Validation set used. Some improvement shown. | Limited tuning. 1-2 parameters adjusted. Unclear if validation set used. Minimal improvement. | No tuning or tuning on test set. Random hyperparameter selection. |

**Checklist:**
- [ ] Hyperparameter grid defined with reasonable ranges
- [ ] GridSearchCV or RandomizedSearchCV used
- [ ] Tuning done on validation set, not test set
- [ ] 3-4 key hyperparameters optimized
- [ ] Cross-validation used during tuning
- [ ] Best parameters documented
- [ ] Improvement quantified vs baseline

---

## Category 4: Evaluation & Results (20 points)

### 4.1 Metrics Selection (5 points)

| Excellent (5) | Good (4) | Fair (2) | Poor (0) |
|---|---|---|---|
| Metrics carefully selected to match problem type and business goals. Multiple metrics reported (not just accuracy). Metrics well-justified. | Good metric selection. 3-4 metrics reported. Reasonable justification. | Limited metrics (1-2). Weak justification for metric choice. | Inappropriate metrics or only single metric (accuracy). |

**Checklist:**
- [ ] Primary metric aligned with business goal
- [ ] 3-4 secondary metrics reported
- [ ] Metrics appropriate for problem type
- [ ] Metrics defined and explained (what they mean)
- [ ] Baseline comparison provided
- [ ] Trade-offs between metrics discussed
- [ ] Business impact of metrics explained

---

### 4.2 Results & Analysis (8 points)

| Excellent (8) | Good (6) | Fair (4) | Poor (0) |
|---|---|---|---|
| Clear improvement over baseline (10%+ improvement). Thorough error analysis. Diagnostic plots included. Results interpreted in business context. Honest assessment of limitations. | Good results with reasonable improvement. Some error analysis. Basic diagnostics. | Acceptable results but minimal analysis. Limited error discussion. | Poor results or no analysis. Results not explained. |

**Checklist:**
- [ ] Results meet or exceed success metrics
- [ ] Clear improvement documented (quantified % improvement over baseline)
- [ ] Confusion matrix created and explained
- [ ] ROC/PR curves plotted (for classification)
- [ ] Error analysis performed (false positives/negatives analyzed)
- [ ] Failure cases identified
- [ ] Business impact of results explained
- [ ] Honest discussion of limitations

---

### 4.3 Reproducibility (7 points)

| Excellent (7) | Good (5) | Fair (3) | Poor (0) |
|---|---|---|---|
| Complete reproducibility: random seeds set, data splits documented, all preprocessing shown, code runs end-to-end. Results consistent across runs. | Good reproducibility. Seeds set. Most preprocessing documented. Minimal issues. | Partial reproducibility. Missing some details. Some uncertainty in replication. | Poor reproducibility. Missing key details. Results not verifiable. |

**Checklist:**
- [ ] Random seeds set (numpy, random, tensorflow if used)
- [ ] Train/val/test splits reproducible
- [ ] Preprocessing pipeline fully documented and scriptable
- [ ] Model training code complete and functional
- [ ] Results exactly reproducible with provided code
- [ ] requirements.txt with pinned versions
- [ ] All random processes controlled

---

## Category 5: Documentation & Code Quality (15 points)

### 5.1 Code Quality (5 points)

| Excellent (5) | Good (4) | Fair (2) | Poor (0) |
|---|---|---|---|
| Clean, well-structured code. Proper naming conventions. Docstrings for functions. Meaningful comments. No code smell. Follows PEP 8. | Generally clean code. Reasonable structure. Some comments and docstrings. Minor style issues. | Code works but messy. Limited comments. Inconsistent style. Some code smell. | Very messy code. No documentation. Poor structure. Difficult to follow. |

**Checklist:**
- [ ] Variable names are descriptive
- [ ] Functions have docstrings (parameters, returns, purpose)
- [ ] Comments explain WHY not WHAT
- [ ] No dead code or unnecessary complexity
- [ ] Code follows PEP 8 style guide (mostly)
- [ ] Error handling where appropriate
- [ ] No hardcoded paths or credentials

---

### 5.2 Documentation (5 points)

| Excellent (5) | Good (4) | Fair (2) | Poor (0) |
|---|---|---|---|
| Comprehensive documentation: README, Model Card, Technical Report all complete. Clear explanations. Professional writing. All decisions documented. | Good documentation. Most elements complete. Clear but could be more detailed. | Minimal documentation. Missing key sections. Some clarity issues. | Poor or missing documentation. Hard to understand project. |

**Checklist:**
- [ ] README.md complete with quick start
- [ ] Model Card filled out with all sections
- [ ] Technical Report 15-25 pages with all sections
- [ ] Data dictionary documenting features
- [ ] EDA Report with insights
- [ ] Professional writing quality
- [ ] All design decisions documented

---

### 5.3 Repository Organization (5 points)

| Excellent (5) | Good (4) | Fair (2) | Poor (0) |
|---|---|---|---|
| Well-organized directory structure. Clean git history. README at root. All artifacts included. .gitignore configured. | Good organization. Mostly clean git history. Main files present. | Somewhat disorganized. Git history messy. Missing some files. | Poorly organized. No git history or structure. |

**Checklist:**
- [ ] Clear directory structure (data/, notebooks/, src/, models/, etc.)
- [ ] Clean git commit history with meaningful messages
- [ ] .gitignore configured (excludes large files, cache)
- [ ] README.md at repository root
- [ ] All code and artifacts included
- [ ] No large data files committed
- [ ] No credentials or sensitive info in repo

---

## Category 6: Presentation (10 points)

### 6.1 Clarity & Storytelling (5 points)

| Excellent (5) | Good (4) | Fair (2) | Poor (0) |
|---|---|---|---|
| Clear narrative arc. Problem, solution, results flow logically. Appropriate for audience (technical and non-technical elements). Visualizations support story. Engaging. | Good story flow. Mostly clear. Some good visuals. Decent pacing. | Somewhat disjointed. Could be clearer. Limited visuals. | Confusing narrative. Poor organization. No clear story. |

**Checklist:**
- [ ] Starts with compelling problem statement
- [ ] Clear explanation of approach
- [ ] Results presented with supporting visuals
- [ ] Key findings highlighted
- [ ] Limitations honestly discussed
- [ ] Appropriate technical depth for audience
- [ ] Visuals are clear and well-labeled

---

### 6.2 Delivery & Q&A (5 points)

| Excellent (5) | Good (4) | Fair (2) | Poor (0) |
|---|---|---|---|
| Confident, well-paced delivery. Good eye contact. Handles questions expertly. Demonstrates deep understanding. Demo works smoothly. | Good presentation skills. Mostly confident. Handles questions adequately. Some demo issues. | Nervous or rushed. Struggles with some questions. Demo has issues. | Very nervous/rushed. Can't answer questions. Failed demo. |

**Checklist:**
- [ ] Well-practiced (clearly rehearsed multiple times)
- [ ] Good pacing (not too fast, not too slow)
- [ ] Clear voice and good projection
- [ ] Eye contact with audience
- [ ] Answers questions directly and honestly
- [ ] Demonstrates knowledge of code and decisions
- [ ] Demo works (or has backup screenshot)

---

## Bonus Points (Optional)

- **Production-Ready Code:** +3 points
  - Full unit tests implemented
  - Logging and error handling comprehensive
  - CI/CD pipeline configured

- **Advanced ML Techniques:** +3 points
  - Transfer learning (for CV)
  - Ensemble methods beyond basic voting
  - SHAP/LIME interpretability analysis

- **Deployment Excellence:** +3 points
  - Kubernetes deployment configuration
  - Monitoring dashboard implemented
  - Auto-scaling configuration

- **Outstanding Presentation:** +2 points
  - Exceptional clarity and engagement
  - Professional-quality slides
  - Impressive live demo

**Maximum with bonus: 110 points**

---

## Grade Conversion

```
90-100   A   Excellent - Professional quality project
80-89    B   Good - Meets expectations with minor issues
70-79    C   Acceptable - Functional but needs improvement
60-69    D   Poor - Significant gaps in execution
<60      F   Fail - Does not meet minimum standards
```

---

## Detailed Feedback Form

Use this form to provide detailed feedback on each category:

### Category Scores Summary

| Category | Points | Score | Weight | Weighted |
|----------|--------|-------|--------|----------|
| 1. Problem Definition & Planning | 15 | [ ] | 15% | [ ] |
| 2. Data & Analysis | 15 | [ ] | 15% | [ ] |
| 3. Model Development | 25 | [ ] | 25% | [ ] |
| 4. Evaluation & Results | 20 | [ ] | 20% | [ ] |
| 5. Documentation & Code Quality | 15 | [ ] | 15% | [ ] |
| 6. Presentation | 10 | [ ] | 10% | [ ] |
| **TOTAL** | **100** | **[ ]** | **100%** | **[ ]** |
| **Bonus** | **+10** | **[ ]** | - | - |
| **FINAL GRADE** | - | **[ ]** | - | - |

### Strengths (What was done well):
1. ____________________________________________________________
2. ____________________________________________________________
3. ____________________________________________________________

### Areas for Improvement:
1. ____________________________________________________________
2. ____________________________________________________________
3. ____________________________________________________________

### Specific Feedback:
[Space for detailed comments]

### Recommendations for Next Steps:
[Space for suggestions on how to improve further]

---

## Grading Instructions for Instructors

1. **Score each criterion** according to the rubric (Excellent/Good/Fair/Poor)
2. **Assign points** based on criteria scores
3. **Check checklist items** - missing items should lower the score
4. **Consider evidence** from code, documentation, and presentation
5. **Award bonus points** if applicable
6. **Fill out feedback form** with strengths, areas for improvement, specific comments
7. **Provide constructive feedback** that helps student improve

### Common Issues to Watch For:

- **Scope creep:** Project grew beyond initial proposal
- **Data leakage:** Model uses information it shouldn't have access to
- **Test set tuning:** Hyperparameters optimized on test data
- **Overfitting:** Train/test gap >15%
- **Single metric:** Only reporting accuracy, not other important metrics
- **Poor documentation:** Hard to understand or reproduce
- **Incomplete deployment:** API or Docker not functional
- **Last-minute presentation:** Clearly not practiced enough

---

*This rubric emphasizes both technical quality and professional practices suitable for industry work.*
