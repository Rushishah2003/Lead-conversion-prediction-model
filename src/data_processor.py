import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from sklearn.feature_extraction.text import TfidfVectorizer

class CRMDataProcessor:
    """
    Handles data loading, cleaning, and feature engineering for the Lead Scoring model.
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self.df = None
        self.X_train = None
        self.X_val = None
        self.X_test = None
        self.y_train = None
        self.y_val = None
        self.y_test = None
        self.label_encoders = {} 
        self.tfidf_vectorizer = None # Saving this to vectorizer unseen data later

    def load_data(self):
        """Loads data and performs initial type conversions."""
        print(f"Loading data from {self.filepath}...")
        self.df = pd.read_csv(self.filepath)
        
        # Convert created_date to datetime immediately
        if 'created_date' in self.df.columns:
            self.df['created_date'] = pd.to_datetime(self.df['created_date'])
            
        print(f"Data Loaded. Shape: {self.df.shape}")
        return self.df

    def perform_eda(self):
        """
        Prints key statistics for initial analysis.
        """
        print("\n--- Data Exploration (EDA) ---")
        print("Missing Values per Column:")
        print(self.df.isnull().sum()[self.df.isnull().sum() > 0])
        
        conversion_rate = self.df['converted'].mean()
        print(f"\nConversion Rate: {conversion_rate:.1%}")
        if conversion_rate < 0.2:
            print("NOTE: Dataset is imbalanced. Stratified splitting recommended.")

        print("\nDistribution of Key Categorical Fields:")
        print(self.df['intent'].value_counts())
        print("-------------------------------")

    def clean_and_feature_engineer(self):
        """
        Main pipeline for cleaning and feature engineering.
        """
        df = self.df.copy()

        # 1. Remove Leakage & Noise
        # 'days_to_conversion' is future information (leakage).
        # 'lead_id' is a unique identifier (noise).
        drop_cols = ['days_to_conversion', 'lead_id']
        df = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')

        # 2. PII Removal
        # Drop personally identifiable information not needed for scoring.
        pii_cols = ['first_name', 'last_name', 'phone', 'email']
        df = df.drop(columns=[col for col in pii_cols if col in df.columns], errors='ignore')

        # 3. Missing Value Handling
        # Impute response_time_hours with median to handle outliers.
        if 'response_time_hours' in df.columns:
            median_resp = df['response_time_hours'].median()
            df['response_time_hours'] = df['response_time_hours'].fillna(median_resp)
        
        # Treat missing budget as its own category.
        if 'budget_range' in df.columns:
            df['budget_range'] = df['budget_range'].fillna('Unknown')

        # 4. Feature Engineering
        
        # Engagement Score: Weighted sum based on "Intent Hierarchy"
        # Logic: High-friction actions (Form) >> Low-friction (Visit).
        # These weights act as a heuristic baseline for the model to refine.
        weights = {
            'visit': 1,
            'open': 2,
            'click': 3,
            'download': 5,
            'form': 10
        }
        
        df['engagement_score'] = (
            (df['website_visits'] * weights['visit']) + 
            (df['email_opens'] * weights['open']) + 
            (df['email_clicks'] * weights['click']) + 
            (df['form_submissions'] * weights['form']) +
            (df['content_downloads'] * weights['download'])
        )

        # Company Tier: Map company_size to ordinal 1-6 scale.
        size_map = {
            '1-10': 1, '11-50': 2, '51-200': 3, 
            '201-500': 4, '501-1000': 5, '1000+': 6
        }
        df['company_tier'] = df['company_size'].map(size_map).fillna(0)

        # Engagement Rate: Clicks / Opens
        df['email_engagement_rate'] = df['email_clicks'] / (df['email_opens'] + 0.0001)

        # 5. Store inquiry_text for later (TF-IDF after split to avoid leakage)
        self._inquiry_text = df['inquiry_text'].fillna('').values if 'inquiry_text' in df.columns else None
            
        # 6. Encoding
        # Use Label Encoding for tree-based models. 
        # Keep dimensionality low by dropping high-cardinality columns.
        df = df.drop(columns=['company_name', 'inquiry_text'], errors='ignore')
        
        cat_encode_cols = ['industry', 'lead_source', 'intent', 'budget_range', 'country', 'job_title']
        
        for col in cat_encode_cols:
            if col in df.columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le

        # Cleanup original columns
        df = df.drop(columns=['company_size', 'created_date'], errors='ignore')

        print(f"Feature Engineering Complete. Final Shape: {df.shape}")
        self.df = df
        return df

    def split_data(self):
        """
        Splits data into Train (70%), Validation (15%), Test (15%).
        """
        # Separate Target
        X = self.df.drop(columns=['converted'])
        y = self.df['converted']

        # First Split: Train (70%) vs Temp (30%)
        self.X_train, X_temp, self.y_train, y_temp = train_test_split(
            X, y, test_size=0.30, stratify=y, random_state=42
        )

        # Second Split: Validation (15%) vs Test (15%)
        self.X_val, self.X_test, self.y_val, self.y_test = train_test_split(
            X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=42
        )

        # Now do TF-IDF properly: fit on train, transform all
        if self._inquiry_text is not None:
            print("Processing NLP features (TF-IDF)...")
            train_idx = self.X_train.index
            val_idx = self.X_val.index
            test_idx = self.X_test.index
            
            tfidf = TfidfVectorizer(max_features=50, stop_words='english')
            
            # Fit only on training text
            train_text = self._inquiry_text[train_idx]
            tfidf.fit(train_text)
            self.tfidf_vectorizer = tfidf
            
            # Transform each set
            for X_set, idx in [(self.X_train, train_idx), (self.X_val, val_idx), (self.X_test, test_idx)]:
                text_feats = tfidf.transform(self._inquiry_text[idx]).toarray()
                text_df = pd.DataFrame(
                    text_feats,
                    columns=[f"txt_{f}" for f in tfidf.get_feature_names_out()],
                    index=X_set.index
                )
                for col in text_df.columns:
                    X_set[col] = text_df[col].values

        print(f"Split Sizes - Train: {self.X_train.shape[0]}, Val: {self.X_val.shape[0]}, Test: {self.X_test.shape[0]}")
        return self.X_train, self.X_val, self.X_test, self.y_train, self.y_val, self.y_test

if __name__ == "__main__":
    # Quick sanity check step when running this file directly
    processor = CRMDataProcessor("leads_dataset.csv")
    processor.load_data()
    processor.perform_eda()
    processor.clean_and_feature_engineer()
    processor.split_data()
