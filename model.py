import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load the dataset
df = pd.read_csv('phishing.csv')

# 1. Remove the 'Index' column (it's just a row ID, not a feature)
df = df.drop('Index', axis=1)

# 2. Split into Features (X) and Target (y)
# Now we use 'class' as the column name
X = df.drop('class', axis=1)
y = df['class']

# 3. Train the model
print("Training the Safe-Surf AI... please wait.")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# 4. Save the model
with open('classifier.pkl', 'wb') as f:
    pickle.dump(model, f)

print("✅ Success! 'classifier.pkl' created using the 'class' column.")