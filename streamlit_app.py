"""
Streamlit app for AKI Mortality Prediction
Research-use only mortality risk predictor
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / 'src'))
from config import MODELS_DIR, RANDOM_STATE

# Page configuration
st.set_page_config(
    page_title="AKI Mortality Risk Predictor",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { max-width: 1200px; }
    .header { text-align: center; padding: 20px 0; }
    .warning-box { background-color: #0066cc; padding: 15px; border-radius: 5px; border-left: 4px solid #003d99; color: white; }
    .result-box { padding: 15px; border-radius: 5px; }
    .high-risk { background-color: #dc3545; border-left: 4px solid #8b0000; color: white; }
    .moderate-risk { background-color: #ff8c00; border-left: 4px solid #cc6600; color: white; }
    .low-risk { background-color: #28a745; border-left: 4px solid #1a6d2f; color: white; }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model_and_preprocessors():
    """Load best model and preprocessing objects"""
    try:
        # Load Logistic Regression model for web page
        model_path = MODELS_DIR / "logistic_regression.pkl"
        if not model_path.exists():
            # Fall back to best available model
            available_models = list(MODELS_DIR.glob("*.pkl"))
            if not available_models:
                return None, None, None, None
            model_path = available_models[0]
        
        model = joblib.load(model_path)
        
        # Fix sklearn version compatibility (1.8.0 removed multi_class, 1.6.1 needs it)
        if hasattr(model, '__class__') and model.__class__.__name__ == 'LogisticRegression':
            if not hasattr(model, 'multi_class'):
                model.multi_class = 'auto'
        
        # Load scaler
        scaler = None
        scaler_path = MODELS_DIR / "scaler.pkl"
        if scaler_path.exists():
            scaler = joblib.load(scaler_path)
        
        # Load imputer
        imputer = None
        imputer_path = MODELS_DIR / "imputer.pkl"
        if imputer_path.exists():
            imputer = joblib.load(imputer_path)
        
        # Load feature names from metrics
        feature_names = None
        metrics_path = MODELS_DIR.parent / "tables" / "model_metrics.csv"
        
        return model, scaler, imputer, feature_names
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None, None, None, None

@st.cache_data
def load_top_features():
    """Load top 5 LR features for web page"""
    # Top 5 Logistic Regression features (excluding kreatininlastvalue)
    return ['kreatinin', 'wbc', 'plt', 'totalbilirubin', 'age']

def get_feature_input_info():
    """
    Get information about available features - TOP 5 FOR WEB PAGE
    Returns a template with reasonable ranges based on typical AKI data
    """
    # Top 5 Logistic Regression features only
    features_info = {
        'kreatinin': {'type': 'number', 'min': 0.1, 'max': 15.0, 'step': 0.1, 'default': 1.0, 'description': 'Serum Creatinine (mg/dL)', 'label': 'Creatinine'},
        'wbc': {'type': 'number', 'min': 0.0, 'max': 50.0, 'step': 0.1, 'default': 10.0, 'description': 'White Blood Cells (10³/µL)', 'label': 'WBC'},
        'plt': {'type': 'number', 'min': 10, 'max': 500, 'step': 1, 'default': 200, 'description': 'Platelets (10³/µL)', 'label': 'PLT'},
        'totalbilirubin': {'type': 'number', 'min': 0.0, 'max': 20.0, 'step': 0.1, 'default': 0.8, 'description': 'Total Bilirubin (mg/dL)', 'label': 'Total Bilirubin'},
        'age': {'type': 'number', 'min': 18, 'max': 120, 'step': 1, 'default': 65, 'description': 'Patient Age (years)', 'label': 'Age'},
    }
    return features_info

def main():
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='header'><h1>AKI Mortality Risk Predictor</h1></div>", unsafe_allow_html=True)
    
    # Load model
    model, scaler, imputer, _ = load_model_and_preprocessors()
    
    if model is None:
        st.error("❌ Model files not found. Please run the training pipeline first.")
        st.info("Run `python src/app.py` from the project root to train the model.")
        return
    
    # Load top features
    top_features = load_top_features()
    
    # Sidebar - Model info
    with st.sidebar:
        st.markdown("### Model Information")
        st.info(f"""
        - **Model Type**: Logistic Regression
        - **Target**: AKI Mortality
        - **Training Data**: DEU Hospital AKI Dataset
        - **Model Status**: Production-Ready
        """)
    
    # Main interface
    st.markdown("### Patient Data Input - Top 5 Predictors")
    
    # Get feature info template
    features_info = get_feature_input_info()
    
    # Create input fields
    input_data = {}
    
    # Organize inputs in columns
    if top_features:
        st.markdown(f"**Top 5 Predictive Features** (recommended inputs):")
        
        # Create multiple columns for organized layout
        cols = st.columns(3)
        col_idx = 0
        
        for feature in top_features:
            # Normalize feature name for matching
            feature_lower = feature.lower().strip()
            
            # Find matching info
            feature_config = features_info.get(feature_lower, {
                'type': 'number',
                'min': 0,
                'max': 1000,
                'step': 1,
                'default': 0,
                'description': feature
            })
            
            with cols[col_idx % 3]:
                if feature_config['type'] == 'number':
                    display_label = feature_config.get('label', feature)
                    input_data[feature_lower] = st.number_input(
                        display_label,
                        min_value=feature_config['min'],
                        max_value=feature_config['max'],
                        value=feature_config['default'],
                        step=feature_config['step'],
                        help=feature_config['description']
                    )
            
            col_idx += 1
    else:
        st.markdown("**Enter Patient Features**:")
        
        common_features = ['age', 'hr', 'sbp', 'dbp', 'rr', 'spo2', 'temp', 'glucose', 'wbc', 'hgb', 'plt', 'cr']
        
        cols = st.columns(3)
        col_idx = 0
        
        for feature in common_features:
            feature_config = features_info[feature]
            
            with cols[col_idx % 3]:
                input_data[feature] = st.number_input(
                    feature.upper(),
                    min_value=feature_config['min'],
                    max_value=feature_config['max'],
                    value=feature_config['default'],
                    step=feature_config['step'],
                    help=feature_config['description']
                )
            
            col_idx += 1
    
    # Prediction button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        predict_button = st.button("🔮 Predict Mortality Risk", use_container_width=True, type="primary")
    
    # Prediction logic
    if predict_button:
        try:
            # Top 5 features for Logistic Regression - Direct mapping (database names match)
            feature_mapping = {
                'kreatinin': 'kreatinin',
                'wbc': 'wbc',
                'plt': 'plt',
                'totalbilirubin': 'totalbilirubin',
                'age': 'age',
            }
            
            # Create mapping dict with actual database column names
            mapped_data = {}
            for user_field, db_column in feature_mapping.items():
                if user_field in input_data:
                    mapped_data[db_column] = input_data[user_field]
            
            # Convert to DataFrame and ensure proper columns
            input_df = pd.DataFrame([mapped_data])
            
            # Get the expected columns from the model (if available through scaler)
            if scaler is not None and hasattr(scaler, 'feature_names_in_'):
                expected_cols = list(scaler.feature_names_in_)
                # Fill missing features with training mean so they scale to 0 (neutral)
                fill_values = dict(zip(expected_cols, scaler.mean_))
                input_df = input_df.reindex(columns=expected_cols)
                for col in expected_cols:
                    if col not in mapped_data:
                        input_df[col] = fill_values[col]
            
            # Apply scaling if available
            if scaler is not None:
                try:
                    input_scaled = scaler.transform(input_df)
                    X_input = pd.DataFrame(input_scaled, columns=input_df.columns)
                except Exception as scale_err:
                    st.warning(f"Scaling issue: {scale_err}. Using unscaled data.")
                    X_input = input_df
            else:
                X_input = input_df
            
            # Get prediction
            y_pred_proba = model.predict_proba(X_input)[0]
            y_pred = model.predict(X_input)[0]
            
            mortality_prob = y_pred_proba[1]
            
            # Display results
            st.markdown("---")
            st.markdown("### Prediction Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Mortality Probability",
                    f"{mortality_prob*100:.1f}%",
                    delta=None
                )
            
            with col2:
                predicted_class = "HIGH RISK" if mortality_prob >= 0.5 else "LOW RISK"
                risk_color = "#dc3545" if mortality_prob >= 0.5 else "#28a745"
                st.metric("Predicted Class", predicted_class)
            
            with col3:
                st.metric(
                    "Survival Probability",
                    f"{(1-mortality_prob)*100:.1f}%",
                    delta=None
                )
            
            # Detailed result box
            if mortality_prob >= 0.7:
                risk_level = "HIGH"
                css_class = "high-risk"
                icon = "🔴"
            elif mortality_prob >= 0.4:
                risk_level = "MODERATE"
                css_class = "moderate-risk"
                icon = "🟡"
            else:
                risk_level = "LOW"
                css_class = "low-risk"
                icon = "🟢"
            
            st.markdown(f"""
            <div class='result-box {css_class}'>
                <h4>{icon} Risk Level: {risk_level}</h4>
                <p><strong>Mortality Risk:</strong> {mortality_prob*100:.1f}%</p>
                <p><strong>Interpretation:</strong> This patient has a {risk_level.lower()} estimated risk of AKI mortality 
                based on the predictive model trained on the DEU hospital dataset.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Additional info
            with st.expander("ℹ️ Model Information & Disclaimers"):
                st.markdown("""
                **Model Details:**
                - Algorithm: Logistic Regression (Simplified for Web)
                - Top 5 Features: Creatinine, WBC, Platelets, Bilirubin, Age
                - Training Dataset: DEU Hospital AKI Retrospective Data (2,230 patients)
                - Performance: AUC = 0.857, Accuracy = 81.2%
                - Validation: Stratified train-test split with proper cross-validation
                
                **Important Notes:**
                1. This model is for research purposes only
                2. Predictions should NOT replace clinical judgment
                3. Model performance may vary in different populations
                4. Always verify predictions with clinical experts
                5. Ensure all input values are accurate before interpretation
                
                **Limitations:**
                - Model trained on specific hospital population (DEU Hospital)
                - May not generalize to all patient populations
                - Uses only 5 most important features (simplified version)
                - Missing important contextual clinical information
                - Should be used as supplementary tool only
                """)
            
        except Exception as e:
            st.error(f"❌ Prediction error: {str(e)}")
            st.info("Please ensure all input values are valid and within expected ranges.")

if __name__ == "__main__":
    main()
