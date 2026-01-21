# Synthetic Leads Dataset - Documentation

## Overview
This dataset contains 500 synthetic lead records designed to simulate a realistic CRM database for a B2B SaaS company selling CRM solutions. The data includes company information, contact details, engagement metrics, inquiry text, and conversion outcomes.

## Dataset Statistics
- **Total Records**: 500 leads
- **Date Range**: Last 6 months
- **Conversion Rate**: ~29%
- **Features**: 23 columns
- **File Format**: CSV

## Data Dictionary

### Identification Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `lead_id` | String | Unique identifier for each lead | LEAD-1000 |
| `created_date` | Date | Date when lead entered the system | 2025-09-15 |

### Contact Information

| Field | Type | Description | Example | Notes |
|-------|------|-------------|---------|-------|
| `first_name` | String | Lead's first name | John | - |
| `last_name` | String | Lead's last name | Smith | - |
| `email` | String | Lead's email address | john.smith@acmecorp.com | Auto-generated format |
| `phone` | String | Lead's phone number | +1-555-0123 | Various international formats |
| `job_title` | String | Lead's position | VP of Sales | 12 different titles |

### Company Information

| Field | Type | Description | Possible Values | Notes |
|-------|------|-------------|----------------|-------|
| `company_name` | String | Name of lead's company | Acme Corporation | - |
| `company_size` | String | Number of employees | 1-10, 11-50, 51-200, 201-500, 501-1000, 1000+ | Categorical |
| `industry` | String | Company's industry sector | Technology, Healthcare, Finance, etc. | 15 industries |
| `country` | String | Company's primary location | USA, UK, Canada, Germany, etc. | 10 countries |

### Lead Source & Timing

| Field | Type | Description | Possible Values | Notes |
|-------|------|-------------|----------------|-------|
| `lead_source` | String | How lead found the company | Website, LinkedIn, Referral, Cold Email, Conference, Webinar, Advertisement, Partner | 8 sources |

### Engagement Metrics

| Field | Type | Description | Range | Notes |
|-------|------|-------------|-------|-------|
| `website_visits` | Integer | Number of website visits | 0-20+ | Poisson distribution (λ=5) |
| `email_opens` | Integer | Number of marketing emails opened | 0-15+ | Poisson distribution (λ=3) |
| `email_clicks` | Integer | Number of email links clicked | 0-email_opens | Always ≤ email_opens |
| `form_submissions` | Integer | Number of forms filled | 0-1 | Binary in this dataset |
| `content_downloads` | Integer | Number of resources downloaded | 0-5+ | Poisson distribution (λ=0.5) |

### Inquiry & Intent

| Field | Type | Description | Possible Values | Notes |
|-------|------|-------------|----------------|-------|
| `inquiry_text` | Text | Lead's initial message/inquiry | Free text | 150-300 characters |
| `intent` | String | Categorized intent | demo_request, pricing, technical, support, partnership | Ground truth label |
| `budget_range` | String | Mentioned or inferred budget | < $10K, $10K-$50K, $50K-$100K, $100K+, Not specified | Often "Not specified" |

### Response & Conversion

| Field | Type | Description | Range | Notes |
|-------|------|-------------|-------|-------|
| `response_time_hours` | Float | Hours until first response | 0.5-72.0 | Null for ~20% of leads |
| `converted` | Integer | Whether lead converted | 0 or 1 | Binary outcome |
| `days_to_conversion` | Float | Days from lead to conversion | 7-90 | Null if not converted |

## Intent Categories

### 1. Demo Request (35% of leads)
**Characteristics:**
- Highest conversion rate (~40%)
- Looking to see product in action
- Often mentions team size or current pain points

**Example Inquiries:**
- "Hi, I'd like to schedule a demo of your CRM platform."
- "Can we book a demo? Our team of 25 sales reps needs a better solution."
- "Interested in seeing your product in action."

### 2. Pricing (25% of leads)
**Characteristics:**
- Moderate conversion rate (~30%)
- Budget-conscious
- Needs cost justification

**Example Inquiries:**
- "What are your pricing plans? We have about 50 users."
- "Can you share pricing information?"
- "Need a quote for 10 users."

### 3. Technical (15% of leads)
**Characteristics:**
- Lower conversion rate (~20%)
- Focused on integration and capabilities
- Longer sales cycle

**Example Inquiries:**
- "Does your CRM integrate with Salesforce?"
- "What APIs do you provide?"
- "Can your platform handle 100K contacts?"

### 4. Support (15% of leads)
**Characteristics:**
- Lowest conversion rate (~15%)
- Often existing customers or evaluating migration
- Issue-driven

**Example Inquiries:**
- "We're having issues with lead scoring."
- "What migration support do you offer?"
- "Need help understanding your automation features."

### 5. Partnership (10% of leads)
**Characteristics:**
- Variable conversion rate (~25%)
- Not traditional customers
- Reseller or integration partners

**Example Inquiries:**
- "Interested in exploring partnership opportunities."
- "Would like to discuss becoming a reseller partner."
- "Exploring white-label solutions."

## Conversion Factors

### Positive Indicators (Increase Conversion Probability)
1. **Intent**: demo_request (+30 points), pricing (+20 points)
2. **Company Size**: Larger companies convert better (1000+ employees: +25 points)
3. **Engagement**: 
   - High website visits (>5): +10 points
   - High email opens (>3): +10 points
   - Form submissions: +15 points
4. **Lead Source**: Referral or Partner (+20 points)
5. **Quick Response**: Response time < 2 hours (+10 points)

### Negative Indicators (Decrease Conversion Probability)
1. Intent: support or technical queries
2. Small company size (1-10 employees)
3. Low engagement metrics
4. Long response times (>24 hours)
5. Cold email or advertisement sources

### Conversion Threshold
- Leads with composite score > 50 are marked as converted
- Random variation (±15 points) added for realism

## Data Quality Notes

### Complete Fields (100%)
- All identification and contact fields
- Company information
- Intent and inquiry text
- Conversion status

### Partial Fields
- `response_time_hours`: ~80% complete (20% null)
- `days_to_conversion`: Only present for converted leads (29%)
- `budget_range`: Often "Not specified" (~40%)

### Data Relationships
1. `email_clicks` ≤ `email_opens` (logical constraint)
2. `days_to_conversion` only exists where `converted` = 1
3. Higher engagement typically correlates with conversion
4. Larger companies + demo requests = highest conversion rate

## Use Case Scenarios

### For Assignment 1 (Lead Scoring & Classification)
**Key Features to Use:**
- All engagement metrics for scoring model
- `inquiry_text` for NLP classification
- `converted` as target variable
- Company info as categorical features

**Modeling Challenges:**
- Imbalanced classes (71% not converted)
- Text classification with limited training data
- Feature engineering from multiple signal types

### For Assignment 2 (Conversational AI & Enrichment)
**Key Features to Use:**
- `inquiry_text` as conversation starter
- Missing/partial fields for enrichment targets
- Intent to guide conversation flow
- Engagement metrics to prioritize leads

**Enrichment Opportunities:**
- Infer `company_size` from inquiry text mentions
- Extract `budget_range` from conversation
- Predict `industry` from pain points
- Estimate team size from context clues

## Sample Data Patterns

### High-Value Lead Example
```
company_size: 1000+
industry: Technology
intent: demo_request
website_visits: 12
email_opens: 7
lead_source: Referral
response_time_hours: 1.2
inquiry_text: "We're a SaaS company with 200 sales reps looking for a better CRM..."
→ converted: 1 (87% probability)
```

### Low-Value Lead Example
```
company_size: 1-10
industry: Retail
intent: support
website_visits: 1
email_opens: 0
lead_source: Cold Email
response_time_hours: 48.5
inquiry_text: "How do I reset my password?"
→ converted: 0 (12% probability)
```

### Ambiguous Lead Example
```
company_size: 51-200
industry: Healthcare
intent: technical
website_visits: 6
email_opens: 4
lead_source: Website
response_time_hours: 8.0
inquiry_text: "Does your system comply with HIPAA?"
→ converted: 0 (45% probability - could go either way)
```

## Data Generation Logic

The dataset was generated using:
- **Faker library**: For realistic names, companies, contact info
- **Numpy random**: For engagement metrics (Poisson distributions)
- **Template-based text generation**: For inquiry text matching intent
- **Rule-based scoring**: Composite score determining conversion

### Distribution Parameters
- Website visits: Poisson(λ=5), 30% zero-inflated
- Email opens: Poisson(λ=3), 40% zero-inflated
- Email clicks: ≤ opens, Poisson(λ=1)
- Content downloads: Poisson(λ=0.5), 60% zero-inflated

## Ethical Considerations

### Privacy
- All data is synthetic and randomly generated
- No real individuals or companies are represented
- Email addresses follow a fake pattern

### Bias Considerations
- Geographic distribution may not reflect real market
- Industry representation is uniform (not market-weighted)
- Conversion factors are simplified from real-world complexity
- No demographic or sensitive personal data included

## File Information

**Filename**: `leads_dataset.csv`
**Size**: ~250 KB
**Encoding**: UTF-8
**Delimiter**: Comma (,)
**Header Row**: Yes (row 1)
**Missing Value Representation**: Empty cells or "NaN"

## Loading the Data

### Python (pandas)
```python
import pandas as pd
df = pd.read_csv('leads_dataset.csv')
print(df.info())
print(df.head())
```

### Python (with type handling)
```python
import pandas as pd

df = pd.read_csv('leads_dataset.csv', 
                 parse_dates=['created_date'],
                 na_values=['', 'NaN', 'None'])
                 
# Convert data types
df['converted'] = df['converted'].astype(int)
df['lead_id'] = df['lead_id'].astype(str)
```

## Recommended Preprocessing Steps

1. **Handle Missing Values**
   - `response_time_hours`: Impute with median or create "No Response" category
   - `days_to_conversion`: Leave as-is (only relevant for converted leads)
   - `budget_range`: Consider "Not specified" as a valid category

2. **Feature Engineering**
   - Create `total_engagement_score` = weighted sum of engagement metrics
   - Extract `company_tier` from company_size
   - Create `time_features` from created_date (day of week, month)
   - Generate `email_engagement_rate` = clicks/opens (where opens > 0)

3. **Text Processing**
   - Lowercase inquiry_text
   - Remove special characters
   - Tokenization for NLP tasks
   - TF-IDF or embeddings for classification

4. **Encoding**
   - One-hot encode: industry, country, lead_source
   - Ordinal encode: company_size (natural ordering)
   - Label encode: intent (for classification target)

## Questions & Support

For questions about the dataset or assignments, consider:
1. What business problem are you solving?
2. Which features are most predictive of conversion?
3. How would this scale to 100,000 leads?
4. What real-world data would improve the model?

---

**Dataset Version**: 1.0  
**Generated**: January 2026  
**Purpose**: AI/ML Technical Assessment  
**License**: For assessment purposes only
