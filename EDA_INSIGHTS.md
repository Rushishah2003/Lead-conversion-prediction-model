# Exploratory Data Analysis & Decision Log

> **Purpose**: This dataset analysis justifies the engineering decisions made in the pipeline.

## 1. Class Imbalance Check
- **Total Leads**: 500
- **Conversion Rate**: 29.2%
- **Converted (1)**: 146
- **Not Converted (0)**: 354

**Decision**: The dataset is imbalanced (~29/71). We MUST use **Stratified Splitting** to ensure training and test sets possess the same ratio.

## 2. Missing Value Strategy
| Column | Missing Count | Percentage | Decision |
|--------|---------------|------------|----------|
| `response_time_hours` | 100 | 20.0% | **Impute Median**. Mean (35.7h) > Median (34.8h) indicates right-skew (outliers). |
| `days_to_conversion` | 354 | 70.8% | **DROP**. LEAKAGE. This field only exists after conversion. |

## 3. Why 'Company Tier'? (Ordinal vs Categorical)
We checked Conversion Rate by Company Size to see if there is a linear trend.

| Company Size | Conversion Rate |
|--------------|------------------|
| 1-10       | 12.1% ▓▓ |
| 11-50      | 12.9% ▓▓ |
| 51-200     | 14.5% ▓▓ |
| 201-500    | 29.9% ▓▓▓▓▓ |
| 501-1000   | 53.0% ▓▓▓▓▓▓▓▓▓▓ |
| 1000+      | 49.0% ▓▓▓▓▓▓▓▓▓ |

**Insight**: Conversion rate generally increases with company size. Mapping this to a 1-6 scale (`Company Tier`) captures this linear relationship better than One-Hot Encoding.

## 4. Engagement Signals
Do higher interactions actually lead to conversion?

| Metric | Avg (Converted) | Avg (Not Converted) | Uplift |
|--------|-----------------|---------------------|--------|
| `website_visits` | 4.19 | 3.28 | **+27.8%** |
| `email_opens` | 1.88 | 1.63 | **+15.4%** |
| `form_submissions` | 0.38 | 0.21 | **+80.2%** |

**Decision**: All interaction metrics show positive uplift for converted users. Creating a weighted `Engagement Score` sums up this directional signal into a strong predictive feature.
