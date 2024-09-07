import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flask import Flask, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
import requests
import mysql.connector
# app = Flask(__name__)

# @app.route('/',methods=['GET','POST'])
def graph():
    # Load your datasets
    df = pd.read_csv(r'HSY1.csv')
    df1 = pd.read_csv(r'NVDA1.csv')
    df2 = pd.read_csv(r'RVPH1.csv')
    df3 = pd.read_csv(r'JPM1.csv')
    df4 = pd.read_csv(r'HYMTF1.csv')

    # Create a Plotly figure with subplots
    fig = make_subplots(rows=5, cols=1, shared_xaxes=True, subplot_titles=['HSY', 'NVDA', 'RVPH', 'JPM', 'HYMTF'])

    # Iterate through dataframes and add traces to subplots
    dataframes = [df, df1, df2, df3, df4]
    colors = ['red', 'blue', 'green', 'purple', 'orange']

    for i, df in enumerate(dataframes):
        # Add line chart trace
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Close*'], mode='lines', name='Line Chart', line=dict(color=colors[i])), row=i+1, col=1)

        # Add bar graph trace
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Close*'], mode='markers', name='Bar Graph', marker=dict(color=colors[i])), row=i+1, col=1)

    # Update the layout for each subplot (optional)
    for i in range(1, 6):
        fig.update_xaxes(title_text='Date', row=i, col=1)
        fig.update_yaxes(title_text='Closing Value', row=i, col=1)

    # Update the main layout (optional)
    fig.update_layout(
        title_text="Stock Trends",
        showlegend=False,  # Hide the legend
    )

    # Show the figure
    fig.show()
graph()