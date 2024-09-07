import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics
import matplotlib.pyplot as plt

# Assuming your data is in a DataFrame called df with columns 'independent' and 'dependent'
# Replace 'independent' and 'dependent' with your actual column names

# Load your data
df = pd.read_excel("C:/Users/vyoms/Desktop/CRP  copy.xlsx")

# Selecting independent and dependent variables
X = df[['independent']]
y = df['Stature(in cm)']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a linear regression model
model = LinearRegression()

# Train the model
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Print coefficients and intercept
print('Coefficients:', model.coef_)
print('Intercept:', model.intercept_)

# Calculate metrics
print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_pred))
print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred))
print('Root Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred, squared=False))

# Plot the regression line
plt.scatter(X_test, y_test, color='black')
plt.plot(X_test, y_pred, color='blue', linewidth=3)
plt.xlabel('Independent Variable')
plt.ylabel('Dependent Variable')
plt.title('Linear Regression')
plt.show()
