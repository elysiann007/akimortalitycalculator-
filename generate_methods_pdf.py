"""Generate Methods section as PDF"""
from fpdf import FPDF
from pathlib import Path

class MethodsPDF(FPDF):
    def header(self):
        pass
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

pdf = MethodsPDF()
pdf.set_auto_page_break(auto=True, margin=25)
pdf.add_page()

# Title
pdf.set_font('Helvetica', 'B', 16)
pdf.cell(0, 12, 'Methods', ln=True, align='L')
pdf.ln(4)

def section(title, body):
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 8, title, ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(0, 5.5, body)
    pdf.ln(3)

section("Study Design and Data Source",
    "This retrospective cohort study utilized data from Dokuz Eylul University (DEU) Hospital. "
    "The dataset comprised 2,230 patients admitted with acute kidney injury (AKI), stored in a PostgreSQL database. "
    "A total of 23 variables were initially available, including demographic, laboratory, and clinical parameters. "
    "The primary outcome variable was in-hospital mortality (binary: survived/deceased).")

section("Data Preprocessing",
    "Identifier columns (row_id, protocol_no) were removed prior to analysis, leaving 20 predictor variables: "
    "INR plasma, PT plasma, aPTT plasma, sodium, potassium, calcium, BUN, chloride, creatinine, creatinine last value, "
    "glucose, WBC, RDW, PLT, hemoglobin, total bilirubin, ALT, AST, eGFR (CKD-EPI), and age. "
    "One variable (PT plasma) was stored as string type and was converted to numeric (float) format. "
    "No categorical encoding was required as all predictors were continuous.")

section("Handling Missing Data",
    "Missing values were imputed using Multiple Imputation by Chained Equations (MICE) implemented via "
    "scikit-learn's IterativeImputer with BayesianRidge as the base estimator (max iterations = 5). "
    "The imputer was fitted exclusively on the training set and subsequently applied to the test set to prevent data leakage.")

section("Feature Scaling",
    "Standardization (z-score normalization) was applied using scikit-learn's StandardScaler. "
    "The scaler was fitted on the training set and applied to both training and test sets. "
    "Scaling was applied to Logistic Regression and Artificial Neural Network inputs, while tree-based models "
    "(Random Forest, Gradient Boosting) received unscaled data, as they are invariant to feature scaling.")

section("Train-Test Split",
    "The dataset was split into training (80%, n=1,784) and test (20%, n=446) sets using stratified random sampling "
    "to preserve the class distribution of the outcome variable (approximately 34.5% mortality in both sets). "
    "A fixed random seed (42) was used to ensure reproducibility.")

# ML Algorithms
pdf.set_font('Helvetica', 'B', 11)
pdf.cell(0, 8, 'Machine Learning Algorithms', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(0, 5.5, "Four supervised classification algorithms were trained and evaluated:")
pdf.ln(2)

algos = [
    ("1. Logistic Regression (LR):", " A linear classifier with L2 regularization (maximum iterations = 1,000)."),
    ("2. Random Forest (RF):", " An ensemble of 200 decision trees with maximum depth of 20 and minimum samples split of 10."),
    ("3. Gradient Boosting (GB):", " A sequential ensemble of 200 boosted trees with maximum depth of 5 and a learning rate of 0.05."),
    ("4. Artificial Neural Network (ANN):", " A multilayer perceptron with three hidden layers (128, 64, and 32 neurons), "
     "trained for up to 500 epochs with early stopping (patience = 20 iterations, validation fraction = 10%).")
]
for label, desc in algos:
    pdf.set_font('Helvetica', 'B', 10)
    pdf.write(5.5, label)
    pdf.set_font('Helvetica', '', 10)
    pdf.write(5.5, desc)
    pdf.ln(6)

pdf.ln(1)
pdf.set_font('Helvetica', '', 10)
pdf.multi_cell(0, 5.5, "All models were implemented using scikit-learn (version 1.8.0) in Python 3.14.")
pdf.ln(3)

section("Model Evaluation",
    "Model performance was assessed on the held-out test set using six metrics: "
    "Area Under the Receiver Operating Characteristic Curve (AUC), Classification Accuracy (CA), "
    "Precision, F1-Score, Recall (Sensitivity), and Matthews Correlation Coefficient (MCC). "
    "ROC curves were generated for visual comparison of discriminative performance across models.")

section("Feature Importance Analysis",
    "Feature importance was extracted from all four models: coefficient magnitudes for Logistic Regression, "
    "Gini importance for Random Forest and Gradient Boosting, and permutation importance (10 repeats) for the ANN. "
    "An aggregated ranking was computed by averaging normalized importance scores across all models "
    "to identify the top 15 predictive features.")

section("Statistical Software",
    "All analyses were performed using Python 3.14 with the following libraries: "
    "scikit-learn 1.8.0 (model training and evaluation), pandas 2.3.3 (data manipulation), "
    "NumPy 2.0.2 (numerical computation), matplotlib 3.7.2 and seaborn 0.12.2 (visualization), "
    "and IterativeImputer (missing data imputation). "
    "An interactive web-based prediction tool was developed using Streamlit 1.50.0.")

# Performance table
pdf.add_page()
pdf.set_font('Helvetica', 'B', 11)
pdf.cell(0, 8, 'Table 1. Performance Metrics of Machine Learning Models', ln=True)
pdf.ln(2)

headers = ['Model', 'AUC', 'Accuracy', 'Precision', 'F1-Score', 'Recall', 'MCC']
data = [
    ['Gradient Boosting', '0.910', '83.2%', '77.6%', '74.7%', '72.1%', '0.623'],
    ['Random Forest',     '0.900', '83.9%', '78.9%', '75.7%', '72.7%', '0.637'],
    ['ANN (MLP)',         '0.877', '79.6%', '73.3%', '68.5%', '64.3%', '0.538'],
    ['Logistic Regression','0.865','82.1%', '79.4%', '71.4%', '64.9%', '0.592'],
]

col_widths = [40, 20, 22, 22, 22, 20, 20]

# Header row
pdf.set_font('Helvetica', 'B', 9)
pdf.set_fill_color(220, 220, 220)
for i, h in enumerate(headers):
    pdf.cell(col_widths[i], 7, h, border=1, fill=True, align='C')
pdf.ln()

# Data rows
pdf.set_font('Helvetica', '', 9)
for row in data:
    for i, val in enumerate(row):
        align = 'L' if i == 0 else 'C'
        pdf.cell(col_widths[i], 7, val, border=1, align=align)
    pdf.ln()

output_path = Path("outputs/methods_section.pdf")
output_path.parent.mkdir(parents=True, exist_ok=True)
pdf.output(str(output_path))
print(f"PDF saved: {output_path.resolve()}")
