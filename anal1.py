# volume plot

import plotly.graph_objects as go
import pandas as pd

# Replace 'HSY1.csv' with the correct file path to your CSV file
df = pd.read_csv('HSY1.csv')

fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close*'])])


fig.show()