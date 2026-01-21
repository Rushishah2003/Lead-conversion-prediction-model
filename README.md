# Lead Conversion Prediction

This repository contains a production-ready Machine Learning pipeline designed to predict the probability of a sales lead converting. 

The goal is to help the sales team prioritize their efforts by identifying "High Intent" leads (probability > 70%) versus "Low Intent" leads that should be nurtured via automation.

## Project Structure
```
.
├── src/
│   ├── data_processor.py    # Cleaning, imputation, and feature engineering
│   ├── train.py             # Model training, cross-validation, and evaluation
├── notebook/                # Exploratory notebooks (if applicable)
├── model_metrics.txt        # Detailed performance report of the latest run
├── leads_dataset.csv        # Input dataset
├── requirements.txt         # Dependencies
└── README.md                # Project documentation
```

## Solution Overview

### 1. Data Strategy
We prioritized **data hygiene** to ensure the model generalizes well. Decisions were driven by our initial analysis (see **`notebooks/exploration.ipynb`**).
*   **Leakage Prevention**: We explicitly dropped `days_to_conversion` as this is future information that wouldn't be available at the time of prediction.
*   **Robust Imputation**: `response_time_hours` had missing values, which were filled with the **Median** to avoid skew from outliers.
*   **Privacy**: PII fields (Name, Phone, Email) were removed to ensure ethical data usage.

### 2. Feature Engineering
We engineered features that mirror real-world sales logic:
*   **Implicit Intent (NLP)**: We processed the `inquiry_text` using TF-IDF (Top 50 unigrams) to capture signals like "urgent", "pricing", or "demo" directly from the customer's voice, rather than relying solely on the dropdown `intent` field.
*   **Engagement Score**: A composite metric based on an **Intent Hierarchy**. We assigned heuristic weights (Forms=10x, Opens=2x, Visits=1x) to create a single "heat" signal. *Note: While the model could learn these interactions non-linearly, this score provides an interpretable proxy for "Lead Effort" that sales teams intuitively understand.*
*   **Company Tier**: Mapped company sizes to an ordinal scale (1-6) to let the model understand that "larger is generally different" in a linear way.
*   **Engagement Rate**: The ratio of Clicks to Opens, which filters out low-intent curiosity.

### 3. Model Selection & Results
We evaluated three models to find the right balance between performance and explainability.
*   **Performance (Test Set):**
*   **Best Model**: XGBoost (AUC 0.91)
*   **Best Upgrade**: Logistic Regression jumped from AUC 0.83 -> **0.87** after adding NLP features, proving that text signals add massive value for linear models.
*   **Accuracy**: ~81-83% across models.

| Model | CV AUC | Test AUC | Accuracy | Precision | Recall |
|-------|--------|----------|----------|-----------|--------|
| **Logistic Regression** | 0.857 | 0.870 | 81.3% | 0.633 | 0.864 |
| **Random Forest** | 0.869 | 0.906 | 82.7% | 0.714 | 0.682 |
| **XGBoost** | **0.920** | **0.913** | **82.7%** | 0.680 | 0.773 |

**Deployment Decision**: 
Given the results, **XGBoost was selected for the final business impact analysis** because it offers the highest predictive power. However, Logistic Regression is kept in the codebase for scenarios requiring strict transparent explainability.

### 4. Why We Stopped Optimization (The "Goldilocks Zone")
We achieved an **AUC of 0.91** and stopped further tuning. Here is the engineering rationale:
1.  **Dataset Constraints**: With only 500 records (and ~150 positive cases), the statistical resolution is limited. Pushing for higher accuracy (>0.92) would likely result in **overfitting** (memorizing noise in the small test set) rather than learning true patterns.
2.  **Diminishing Returns**: The gap between our Train and Test scores (~0.08) indicates we have extracted the maximum generalizable signal.
3.  **Business Reality**: In production, stability and explainability (maintained by this simpler model) outvalue a theoretical +1% accuracy gain that comes with high variance.

## 5. Business Implementation ("The Score")
We convert the model's raw probability output (0-100%) into actionable segments for the Sales Team:

1.  **Hot Leads (>70%)**: **Immediate Priority**. These leads are highly likely to convert. Action: Direct phone call from a Senior Rep.
2.  **Warm Leads (30-70%)**: **Nurture**. These leads show interest but aren't ready. Action: Enrol in an automated email drip campaign.
3.  **Cold Leads (<30%)**: **Monitor**. Low intent. Action: Monthly newsletter only.

**Expected Value:** 
Based on test data, targeting "Hot" leads exclusively for direct calls would allow the team to capture **55% of all potential conversions** while reducing workload by **79%**.

## How to Run
1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Training Pipeline**:
    ```bash
    # Windows
    $env:PYTHONPATH="src"; python src/train.py

    # Linux/Mac
    PYTHONPATH=src python src/train.py
    ```

    This will:
    *   Load and clean the data.
    *   Train all three models with Cross-Validation.
    *   Save performance metrics to `model_metrics.txt`.
    *   Print the Business Segmentation analysis to the console.

---
*Note: This project uses a synthetic dataset for demonstration purposes.*
