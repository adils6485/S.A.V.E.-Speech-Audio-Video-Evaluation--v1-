import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
import wordcloud
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from tqdm import tqdm
import pickle
import warnings
warnings.filterwarnings('ignore')
# Load dataset
df = pd.read_csv("./Suicide_Detection.csv")  

data=df.copy()
# Display basic info
print(data.info())
print(data.head())

# Check for missing values
print("Missing values per column:\n", data.isnull().sum())
# Drop rows with missing text data
data.dropna(subset=['text'], inplace=True)
plt.figure(figsize=(6,4))
sns.countplot(x="class", data=data, palette="coolwarm")
plt.title("Distribution of Suicide-Related Posts")
plt.show()
plt.figure(figsize=(12,10))
plt.pie(data['class'].value_counts(),startangle=90,colors=['#00ccca','#00ac82'],
        autopct='%0.2f%%',labels=['Suicide','Not Suicide'])
plt.title('SUICIDE OR NOT ?',fontdict={'size':20})
plt.show()
suicide=data[data['class']=='suicide']['text']
xsuicide=data[data['class']=='non-suicide']['text']

def display_cloud(data):
    plt.subplots(figsize=(10,10))
    wc = wordcloud.WordCloud(
                   background_color="black",
                   colormap='viridis',
                   max_words=1000,
                   random_state=24)
    plt.imshow(wc.generate(' '.join(data)))
    plt.axis('off')
    plt.show()

display_cloud(suicide)
# Convert target labels into numeric format
label_encoder = LabelEncoder()
data['class'] = label_encoder.fit_transform(data['class'])  # Encode "suicide" (1) and "non-suicide" (0)
# Text Processing using TF-IDF
vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
X_text = vectorizer.fit_transform(data['text'])

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_text, data['class'], test_size=0.2, random_state=42)
# Standardize feature set
scaler = StandardScaler(with_mean=False)
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
lr_model = LogisticRegression()
lr_model.fit(X_train, y_train)
lr_preds = lr_model.predict(X_test)
print("\nLogistic Regression Model Performance:")
print(classification_report(y_test, lr_preds))