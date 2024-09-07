import pandas as pd
import plotly.graph_objects as go

# List of dataframes
dataframes = [
    pd.read_csv(r'D:\UNI_Files\Sem-5\Adv_Py\Project\HSY1.csv'),
    pd.read_csv(r'D:\UNI_Files\Sem-5\Adv_Py\Project\NVDA1.csv'),
    pd.read_csv(r'D:\UNI_Files\Sem-5\Adv_Py\Project\RVPH1.csv'),
    pd.read_csv(r'D:\UNI_Files\Sem-5\Adv_Py\Project\JPM1.csv'),
    pd.read_csv(r'D:\UNI_Files\Sem-5\Adv_Py\Project\HYMTF1.csv')
]

# Iterate through dataframes and create individual plots
for i, df in enumerate(dataframes):
    # Create a Plotly figure
    fig = go.Figure()

    # Add a line chart trace
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close*'], mode='lines', name='Line Chart', line=dict(color='red')))

    # Add a bar graph trace
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close*'], mode='markers', name='Bar Graph', marker=dict(color='blue')))

    # Update the layout (optional)
    fig.update_layout(
        title=f'Trendline for DataFrame {i}',
        xaxis_title='Date',
        yaxis_title='Closing Value',
    )

    # Show the figure
    fig.show()
