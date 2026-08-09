# Lab 12: Capstone Project Intensive

## Apa ini?

Lab 12 adalah **kulminasi perjalanan pembelajaran machine learning Anda** - sebuah comprehensive capstone project yang mengintegrasikan SEMUA konsep dari kursus selama satu semester.

Ini bukan lab tutorial biasa di mana Anda mengikuti step-by-step. Ini adalah **guided project framework** di mana Anda:
- Memilih problem real-world yang ingin dipecahkan
- Membuat keputusan design dan technical sendiri
- Mengikuti best practices profesional
- Membangun portfolio-quality project

## Durasi & Struktur

**Total: 8 Jam** (distributed across 2 weeks, Weeks 13-14)

```
MINGGU 13:
├─ SENIN (2 jam lab):  Bagian 1 & 2 (Planning + EDA)
├─ RABU (2 jam lab):   Bagian 3 (Model Development)
└─ JUMAT (homework):   Lanjutkan eksperimen, tuning

MINGGU 14:
├─ SENIN (2 jam lab):  Bagian 4 & 5 (Deployment + Reporting)
├─ RABU (1 jam lab):   Q&A + Finalization
└─ JUMAT:              FINAL PRESENTATION (15-20 min)
```

## Struktur Lab

### Bagian 1: Project Planning & Scoping (2 jam)
- Memilih domain: Cybersecurity / Business Intelligence / Healthcare / NLP / Computer Vision
- Problem definition dengan SMART criteria
- Timeline planning dan risk assessment
- **Deliverable: Project Proposal**

### Bagian 2: Data & EDA (2 jam)
- Data collection dan loading
- Exploratory Data Analysis
- Data preprocessing pipeline
- **Deliverable: EDA Report + Processed Dataset**

### Bagian 3: Model Development (2 jam)
- Baseline model implementation
- Systematic model experimentation
- Hyperparameter tuning
- Cross-validation dan validation
- **Deliverable: Model Comparison + Best Model**

### Bagian 4: Deployment & Production (1.5 jam)
- Model serialization (pickle, joblib)
- FastAPI REST API development
- Docker containerization
- Model monitoring & documentation
- **Deliverable: Deployable Container + API Documentation**

### Bagian 5: Presentation & Reporting (0.5 jam)
- Technical report writing
- Presentation slides preparation
- Demo script development
- **Deliverable: Technical Report + Presentation**

## Learning Outcomes (CPMK)

Setelah menyelesaikan lab ini, Anda mampu:

### CPMK-1: Fundamental ML Knowledge
- Mengaplikasikan ML concepts untuk real-world problems
- Memilih model berdasarkan karakteristik data dan business constraints

### CPMK-2: End-to-End ML Pipelines
- Membangun complete pipeline dari data collection hingga deployment
- Mengidentifikasi dan memitigasi data leakage
- Mengoptimalkan pipeline untuk production constraints

### CPMK-3: Critical Analysis & Evaluation
- Mengevaluasi model dengan multiple metrics yang appropriate
- Melakukan error analysis sistematis
- Memvalidasi dengan proper train/val/test splitting

### CPMK-4: Advanced Solutions
- Mengimplementasikan ensemble methods dan hyperparameter tuning
- Menangani imbalanced data dan edge cases
- Designing scalable system architecture

### CPMK-5: Production ML Systems
- Mendeploy model ke production
- Membuat dokumentasi profesional (Model Cards, READMEs)
- Mempresentasikan findings ke stakeholders

## 5 Pilihan Domain Proyek

### 1. Cybersecurity: Malware Detection
**Dataset:** EMBER (600K Windows PE files)
**Goal:** Classify benign vs malware dengan 90%+ accuracy
**Key Challenge:** Large dataset, feature engineering

### 2. Business Intelligence: Customer Churn Prediction
**Dataset:** Telco customer churn
**Goal:** Predict churn dalam 3 bulan dengan 80%+ recall
**Key Challenge:** Class imbalance, interpretability

### 3. Healthcare: Disease Risk Prediction
**Dataset:** Pima Indian Diabetes
**Goal:** Predict diabetes risk dengan 85%+ sensitivity
**Key Challenge:** Clinical interpretability, small dataset

### 4. NLP: Sentiment Analysis
**Dataset:** Amazon reviews atau custom e-commerce
**Goal:** Classify sentiment (pos/neg/neutral) dengan 85%+ accuracy
**Key Challenge:** Text preprocessing, embedding selection

### 5. Computer Vision: Binary Image Classification
**Dataset:** PE file visualizations
**Goal:** Classify malware vs benign from binary images
**Key Challenge:** Limited data, transfer learning

## File-File Penting

```
lab12-capstone-project/
├── index.qmd                           # Main lab content
├── README.md                           # This file
├── PROJECT_PROPOSAL_TEMPLATE.md        # Fill this out first!
├── MODEL_CARD_TEMPLATE.md              # Model documentation
├── RUBRIC.md                           # Grading criteria
└── WORKSHEET.md                        # Planning worksheets
```

## Cara Menggunakan Lab Ini

### Week 13, Monday (2 jam):
1. **Read:** index.qmd Bagian 1 & 2
2. **Complete:** PROJECT_PROPOSAL_TEMPLATE.md
3. **Do:** Load dataset, perform EDA
4. **Output:** Project Proposal + EDA Report

### Week 13, Wednesday (2 jam):
1. **Read:** index.qmd Bagian 3
2. **Do:** Implement baseline model, train 3+ alternative models
3. **Output:** Model comparison table, best model selected

### Week 13, Friday (Homework):
1. **Do:** Hyperparameter tuning
2. **Do:** Cross-validation and validation
3. **Output:** Final model metrics, feature importance analysis

### Week 14, Monday (2 jam):
1. **Read:** index.qmd Bagian 4 & 5
2. **Do:** Save model, build FastAPI API, create Docker container
3. **Output:** Working API, Dockerfile, model card

### Week 14, Wednesday (1 jam):
1. **Do:** Fix any issues, finalize code
2. **Do:** Complete technical report
3. **Do:** Prepare presentation slides
4. **Output:** All documentation complete

### Week 14, Friday (Presentation):
1. **Do:** Present project (15-20 minutes)
2. **Do:** Demo working system
3. **Do:** Answer questions from instructors
4. **Output:** Presentation delivered

## Template Files

### PROJECT_PROPOSAL_TEMPLATE.md
**Mulai di sini!** Fill out problem definition, data, success metrics, timeline.

### MODEL_CARD_TEMPLATE.md
**After model training:** Document model details, performance, limitations, deployment considerations.

### WORKSHEET.md
**Planning documents:** Risk assessment, feature engineering ideas, experiment tracking.

### RUBRIC.md
**Grading criteria:** 6 categories, 100 points total. Review this to understand expectations.

## Critical Success Factors

1. **Start with clear problem definition** - don't code first!
2. **Establish baseline early** - gives context for improvements
3. **Document experiments** - systematic tracking is crucial
4. **Validate properly** - use cross-validation, not just train/test split
5. **Test deployment** - API and Docker must work before submission
6. **Practice presentation** - minimum 3 times before Friday
7. **Complete documentation** - README, Model Card, Technical Report must be professional

## Common Pitfalls to Avoid

- **Scope Creep:** Lock your scope week 1, don't keep adding features
- **Data Leakage:** Scale/encode training data separately from test data
- **Test Set Tuning:** Use validation set for hyperparameter selection, not test set
- **Overfitting:** Check train/test gap regularly (should be <15%)
- **Single Metric:** Always use multiple metrics (accuracy + precision + recall)
- **Last-Minute Demo:** Test your API/Docker a week before presentation
- **Poor Documentation:** Write as you code, don't leave it for the end

## Grading Rubric Summary

```
Problem Definition & Planning      15 points
├─ Problem statement               5 pts
├─ Data planning                   5 pts
└─ Feasibility & timeline          5 pts

Data & Analysis                    15 points
├─ Data quality                    5 pts
├─ EDA & insights                  5 pts
└─ Feature engineering             5 pts

Model Development                  25 points
├─ Approach & algorithms           8 pts
├─ Validation strategy             9 pts
└─ Hyperparameter tuning          8 pts

Evaluation & Results               20 points
├─ Metrics selection               5 pts
├─ Results & analysis              8 pts
└─ Reproducibility                 7 pts

Documentation & Code Quality       15 points
├─ Code quality                    5 pts
├─ Documentation                   5 pts
└─ Repository organization         5 pts

Presentation                       10 points
├─ Clarity & storytelling          5 pts
└─ Delivery & handling questions   5 pts
────────────────────────────────────
TOTAL                            100 points
```

**See RUBRIC.md for detailed grading criteria**

## Resources

**Documentation:**
- index.qmd: Complete lab guide
- PROJECT_PROPOSAL_TEMPLATE.md: Problem definition template
- MODEL_CARD_TEMPLATE.md: Model documentation
- RUBRIC.md: Grading criteria
- WORKSHEET.md: Planning worksheets

**Related Materials:**
- Chapter 14: Capstone Project Guide & Best Practices
- Lab 11: Model Deployment
- Lab 10: Model Evaluation

**External Resources:**
- Kaggle Datasets: https://kaggle.com/datasets
- UCI ML Repository: https://archive.ics.uci.edu/ml
- scikit-learn docs: https://scikit-learn.org
- FastAPI docs: https://fastapi.tiangolo.com
- Docker docs: https://docs.docker.com

## Submission Checklist

Before submitting, make sure you have:

- [ ] **Code**
  - [ ] Jupyter notebook dengan complete pipeline
  - [ ] All code runs without errors
  - [ ] requirements.txt dengan pinned versions
  - [ ] No hardcoded paths or credentials
  - [ ] Proper comments and docstrings

- [ ] **Models**
  - [ ] Best model saved (pickle/joblib)
  - [ ] Preprocessor saved
  - [ ] Model metadata documented

- [ ] **API**
  - [ ] FastAPI endpoints working
  - [ ] Health check implemented
  - [ ] API documentation complete

- [ ] **Deployment**
  - [ ] Dockerfile working
  - [ ] Docker image builds successfully
  - [ ] Container runs without errors

- [ ] **Documentation**
  - [ ] Project Proposal complete
  - [ ] README.md comprehensive
  - [ ] Model Card filled out
  - [ ] Technical Report finished
  - [ ] EDA Report with insights

- [ ] **Presentation**
  - [ ] Slides prepared (14-16)
  - [ ] Presentation practiced 3+ times
  - [ ] Demo working
  - [ ] Q&A answers prepared

- [ ] **Git**
  - [ ] All files committed
  - [ ] Clean commit history
  - [ ] .gitignore configured

## Tips untuk Sukses

1. **Start early** - jangan tunggu last minute
2. **Plan first** - spend time on problem definition before coding
3. **Document as you go** - jangan leave documentation until the end
4. **Test everything** - API, Docker, model accuracy, presentation
5. **Get feedback** - ask mentors/classmates for review
6. **Practice presentation** - at least 3 times
7. **Quality over quantity** - better to finish well than start many things
8. **Reproducibility** - someone else should be able to run your code

## Kontak & Questions

Jika ada pertanyaan atau issues:
1. Review index.qmd dan RUBRIC.md
2. Check WORKSHEET.md untuk planning guidance
3. Lihat example project specifications di index.qmd Part 1
4. Ask instructor during office hours

---

**Remember:** Capstone bukan tentang sempurna, tapi tentang demonstrating your learning dan ability to work on real projects professionally.

**You've got this!** 🚀
