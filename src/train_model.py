
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import bentoml

# Load dataset
df = pd.read_csv("data/raw/admission.csv")

# Clean column names
df.columns = df.columns.str.strip()
print("Columns:", df.columns.tolist())

# Define input features and target
X = df[["GRE Score", "TOEFL Score", "University Rating", "SOP", "LOR", "CGPA", "Research"]]
y = df["Chance of Admit"]

# Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Linear Regression model
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)

# Train Random Forest model
rf_model = RandomForestRegressor(random_state=42)
rf_model.fit(X_train, y_train)

# Save both models into the BentoML Model Store
bentoml.sklearn.save_model("admissions_lr", lr_model)
bentoml.sklearn.save_model("admissions_rf", rf_model)

print("Modell trainiert und gespeichert!")