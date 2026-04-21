"""
Generate sample ICU mortality dataset for testing/demo purposes
Run: python generate_sample_data.py
"""

import numpy as np
import pandas as pd
from pathlib import Path

def generate_sample_data(n_samples=500, random_state=42):
    """Generate realistic ICU mortality dataset for testing"""
    
    np.random.seed(random_state)
    
    # Generate realistic ICU parameters with correlations to mortality
    data = {
        'age': np.random.randint(18, 90, n_samples),
        'hr': np.random.normal(85, 20, n_samples).clip(30, 200),
        'sbp': np.random.normal(120, 25, n_samples).clip(60, 220),
        'dbp': np.random.normal(75, 15, n_samples).clip(30, 140),
        'rr': np.random.normal(18, 8, n_samples).clip(8, 50),
        'spo2': np.random.normal(96, 4, n_samples).clip(70, 100),
        'temp': np.random.normal(37, 0.8, n_samples).clip(34, 40),
        'glucose': np.random.normal(150, 60, n_samples).clip(50, 500),
        'wbc': np.random.gamma(2, 5, n_samples).clip(1, 30),
        'hgb': np.random.normal(11, 2.5, n_samples).clip(4, 18),
        'plt': np.random.gamma(3, 60, n_samples).clip(20, 500),
        'cr': np.random.gamma(1.2, 0.8, n_samples).clip(0.1, 10),
        'bun': np.random.gamma(1.5, 15, n_samples).clip(5, 150),
        'na': np.random.normal(140, 5, n_samples).clip(110, 160),
        'k': np.random.normal(4.0, 0.8, n_samples).clip(2, 8),
        'cl': np.random.normal(105, 5, n_samples).clip(85, 125),
        'co2': np.random.normal(24, 4, n_samples).clip(10, 45),
        'alt': np.random.gamma(1.5, 25, n_samples).clip(1, 300),
        'ast': np.random.gamma(1.5, 28, n_samples).clip(1, 300),
        'bili': np.random.gamma(1.2, 0.7, n_samples).clip(0, 15),
        'ph': np.random.normal(7.35, 0.1, n_samples).clip(6.8, 7.8),
        'pao2': np.random.normal(90, 35, n_samples).clip(40, 400),
        'paco2': np.random.normal(40, 12, n_samples).clip(20, 90),
        'lac': np.random.gamma(1.5, 1, n_samples).clip(0.3, 15),
        'sofa': np.random.randint(0, 20, n_samples),
        'apache': np.random.randint(5, 50, n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Generate mortality flag with realistic correlations
    # Higher SOFA and APACHE scores increase mortality risk
    mortality_risk = (
        -2.5 +
        0.02 * df['age'] +
        0.08 * df['sofa'] +
        0.03 * df['apache'] +
        0.1 * df['cr'] +
        0.3 * (df['hr'] > 110).astype(int) +
        0.3 * (df['sbp'] < 90).astype(int) +
        0.2 * (df['spo2'] < 88).astype(int) +
        0.1 * (df['wbc'] > 15).astype(int) +
        0.1 * (df['plt'] < 100).astype(int) +
        np.random.normal(0, 0.5, n_samples)
    )
    
    mortality_prob = 1 / (1 + np.exp(-mortality_risk))
    # Sample deaths using probability (preserves correlations)
    df['deathFlag'] = np.random.binomial(1, mortality_prob)
    
    # Reorder columns: put deathFlag at end for clarity
    cols = [c for c in df.columns if c != 'deathFlag'] + ['deathFlag']
    df = df[cols]
    
    return df

def main():
    output_path = Path("data") / "deu_icu_mortality.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("Generating sample ICU mortality dataset...")
    df = generate_sample_data(n_samples=500, random_state=42)
    
    print(f"\nDataset shape: {df.shape}")
    print(f"Mortality rate: {df['deathFlag'].mean():.1%}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nFirst 5 rows:")
    print(df.head())
    print(f"\nData types:")
    print(df.dtypes)
    
    df.to_csv(output_path, index=False)
    print(f"\n✓ Sample data saved to: {output_path}")
    print(f"\nYou can now run:")
    print(f"  python src/app.py")
    print(f"or")
    print(f"  python full_pipeline.py")

if __name__ == "__main__":
    main()
