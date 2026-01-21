import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, precision_score, recall_score, accuracy_score, confusion_matrix
import sys
import os

# Handle paths for imports whether run as script or module
try:
    from data_processor import CRMDataProcessor
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), 'src'))
    from src.data_processor import CRMDataProcessor

class ModelTrainer:
    """
    Trains and evaluates Logistic Regression, Random Forest, and XGBoost models.
    """
    
    def __init__(self, X_train, X_val, X_test, y_train, y_val, y_test):
        self.X_train = X_train
        self.X_val = X_val
        self.X_test = X_test
        self.y_train = y_train
        self.y_val = y_val
        self.y_test = y_test
        self.models = {}
        self.results = []

    def train_models(self):
        print("\n--- Model Training & Cross-Validation ---")
        
        # Define base dictionary of models
        models_to_train = {
            'Logistic Regression': LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42),
            'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=5, class_weight='balanced', random_state=42), 
        }

        # Try initializing XGBoost; fallback to GradientBoosting if unavailable
        try:
            import xgboost as xgb
            scale_pos_weight = (len(self.y_train) - self.y_train.sum()) / self.y_train.sum()
            models_to_train['XGBoost'] = xgb.XGBClassifier(
                eval_metric='logloss',
                scale_pos_weight=scale_pos_weight,
                random_state=42,
                n_estimators=100,
                max_depth=3,
                learning_rate=0.05,
                min_child_weight=5,
                subsample=0.8,
                colsample_bytree=0.8,
                reg_alpha=0.1,
                reg_lambda=1.0
            )
        except ImportError:
            print("XGBoost not found. Using GradientBoostingClassifier instead.")
            models_to_train['Gradient Boosting'] = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.05,
                max_depth=3,
                min_samples_leaf=5,
                subsample=0.8,
                random_state=42
            )

        # Train and CV
        from sklearn.model_selection import cross_val_score
        
        for name, model in models_to_train.items():
            print(f"Training {name}...")
            # 1. Cross Validation check
            cv_scores = cross_val_score(model, self.X_train, self.y_train, cv=5, scoring='roc_auc')
            print(f"  > 5-Fold CV AUC: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
            
            # 2. Fit on full training set
            model.fit(self.X_train, self.y_train)
            self.models[name] = model

    def evaluate_models(self):
        print("\n--- Model Evaluation ---")
        header = f"{'Model':<25} | {'CV AUC':<8} | {'Test AUC':<8} | {'Acc':<6} | {'Prec':<6} | {'Recall':<6} | {'Gap'}"
        print(header)
        print("-" * 90)
        
        with open("model_metrics.txt", "w", encoding="utf-8") as f:
            f.write(header + "\n")
            f.write("-" * 90 + "\n")

            for name, model in self.models.items():
                train_probs = model.predict_proba(self.X_train)[:, 1]
                train_auc = roc_auc_score(self.y_train, train_probs)
                
                test_probs = model.predict_proba(self.X_test)[:, 1]
                test_preds = model.predict(self.X_test)
                test_auc = roc_auc_score(self.y_test, test_probs)
                test_acc = accuracy_score(self.y_test, test_preds)
                test_prec = precision_score(self.y_test, test_preds, zero_division=0)
                test_recall = recall_score(self.y_test, test_preds, zero_division=0)
                
                from sklearn.model_selection import cross_val_score
                cv_scores = cross_val_score(model, self.X_train, self.y_train, cv=5, scoring='roc_auc')
                cv_auc = cv_scores.mean()

                gap = train_auc - test_auc
                gap_str = f"{gap:.3f}"
                if gap > 0.10: gap_str += " (!)"

                self.results.append({
                    'Model': name, 'AUC': test_auc, 'Accuracy': test_acc, 'Precision': test_prec, 'Recall': test_recall
                })
                
                line = f"{name:<25} | {cv_auc:.3f}    | {test_auc:.3f}    | {test_acc:.3f}  | {test_prec:.3f}  | {test_recall:.3f}  | {gap_str}"
                print(line)
                f.write(line + "\n")

    def show_business_impact(self):
        """
        Translates technical metrics into business terms.
        """
        print("\n" + "="*50)
        print("   BUSINESS IMPACT: LEAD SEGMENTATION STRATEGY")
        print("="*50)
        
        best_result = max(self.results, key=lambda x: x['AUC'])
        best_model_name = best_result['Model']
        best_model = self.models[best_model_name]
        print(f"Powered by: {best_model_name} (AUC: {best_result['AUC']:.3f})\n")

        # Generate Scores
        probs = best_model.predict_proba(self.X_test)[:, 1]
        test_df = self.X_test.copy()
        test_df['actual_conversion'] = self.y_test
        test_df['lead_score'] = (probs * 100).astype(int)

        # Segment Leads: Cold (<30), Warm (30-70), Hot (>70)
        test_df['segment'] = pd.cut(
            test_df['lead_score'], 
            bins=[-1, 30, 70, 101], 
            labels=['Cold', 'Warm', 'Hot']
        )
        
        # Calculate stats
        segment_stats = test_df.groupby('segment', observed=False).agg(
            Volume=('lead_score', 'count'),
            Conversion_Rate=('actual_conversion', 'mean'),
            Total_Conversions=('actual_conversion', 'sum')
        )
        
        # Calculate 'Efficiency' (Percentage of total conversions captured)
        total_conv = segment_stats['Total_Conversions'].sum()
        segment_stats['Capture_Rate'] = segment_stats['Total_Conversions'] / total_conv
        
        # Print formatted table
        print(f"{'Segment':<10} | {'Score Range':<12} | {'Leads':<6} | {'Conv. Rate':<10} | {'Captured':<10} | {'Action Recommended'}")
        print("-" * 85)
        
        # row for Hot
        hot = segment_stats.loc['Hot']
        print(f"{'HOT':<10} | {'> 70%':<12} | {hot['Volume']:<6} | {hot['Conversion_Rate']:.1%}     | {hot['Capture_Rate']:.1%}     | {'[!!] CALL IMMEDIATELY'}")
        
        # row for Warm
        warm = segment_stats.loc['Warm']
        print(f"{'WARM':<10} | {'30% - 70%':<12} | {warm['Volume']:<6} | {warm['Conversion_Rate']:.1%}     | {warm['Capture_Rate']:.1%}     | {'[->] Email Drip Campaign'}")
        
        # row of Cold
        cold = segment_stats.loc['Cold']
        print(f"{'COLD':<10} | {'< 30%':<12} | {cold['Volume']:<6} | {cold['Conversion_Rate']:.1%}     | {cold['Capture_Rate']:.1%}     | {'[..] Monthly Newsletter'}")
        
        print("-" * 85)
        print("\nSTRATEGIC INSIGHT:")
        print(f"By calling ONLY the 'Hot' leads ({hot['Volume']} people), we can capture {hot['Capture_Rate']:.0%} of all conversions.")
        print(f"This reduces workload by {(1 - hot['Volume']/len(test_df)):.0%} while missing very few deals.")
        print("="*50 + "\n")

if __name__ == "__main__":
    # Check for dataset in current or parent directory
    dataset_path = "leads_dataset.csv"
    if not os.path.exists(dataset_path):
        if os.path.exists("../leads_dataset.csv"):
            dataset_path = "../leads_dataset.csv"
        else:
            print("Error: leads_dataset.csv not found.")
            sys.exit(1)

    # 1. Load & Process
    processor = CRMDataProcessor(dataset_path)
    processor.load_data()
    processor.perform_eda()
    processor.clean_and_feature_engineer()
    X_train, X_val, X_test, y_train, y_val, y_test = processor.split_data()

    # 2. Train & Evaluate
    trainer = ModelTrainer(X_train, X_val, X_test, y_train, y_val, y_test)
    trainer.train_models()
    trainer.evaluate_models()
    trainer.show_business_impact()
