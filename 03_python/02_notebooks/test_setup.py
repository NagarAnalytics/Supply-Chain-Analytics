# Test all imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly
from sklearn.ensemble import RandomForestClassifier
import pyodbc
import sqlalchemy

print("✅ pandas:", pd.__version__)
print("✅ numpy:", np.__version__)
print("✅ matplotlib:", plt.matplotlib.__version__)
print("✅ seaborn:", sns.__version__)
print("✅ plotly:", plotly.__version__)
print("✅ scikit-learn:", RandomForestClassifier.__module__)
print("✅ pyodbc:", pyodbc.version)
print("✅ sqlalchemy:", sqlalchemy.__version__)
print("\n🎉 All libraries installed successfully!")