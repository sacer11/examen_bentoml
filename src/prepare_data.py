#src/prepare_data.py
import pandas as pd
from sklearn.model_selection import train_test_split
import os

df = pd.read_csv("data/raw/admission.csv")
X = df.drop(columns=["Chance of Admit ", "Serial No."])
y = df["Chance of Admit "]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

os.makedirs("data/processed", exist_ok=True)
X_train.to_csv("data/processed/X_train.csv", index=False)
X_test.to_csv("data/processed/X_test.csv", index=False)
y_train.to_csv("data/processed/y_train.csv", index=False)
y_test.to_csv("data/processed/y_test.csv", index=False)
