#%%

import pandas as pd
import plotly.graph_objects as go
from collections import Counter
import re
from plotly.subplots import make_subplots

# Load data
data = pd.read_excel('data.xlsx')

# Clean the RepairerNotes column
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

data['CleanedNotes'] = data['RepairerNotes'].astype(str).apply(clean_text)

# Identify faults
def extract_faults(text):
    patterns = [
        r'\bcompressor\b', r'\bfan\b', r'\bcontroller\b', r'\bdoor handle\b', r'\bgasket\b', 
        r'\bthermostat\b', r'\belectrical\b', r'\bcooling\b', r'\bleaking\b', r'\bfrost\b',
        r'\bnoise\b', r'\boverheating\b', r'\bfailure\b', r'\bpower\b', r'\bsensor\b',
        r'\binstallation\b', r'\bdefrost\b', r'\bdisplay\b', r'\bmotor\b', r'\bcircuit\b'
    ]
    fault_dict = {}
    for pattern in patterns:
        if re.search(pattern, text):
            fault = re.search(pattern, text).group()
            fault_dict[fault] = fault_dict.get(fault, 0) + 1
    return fault_dict

all_faults = Counter()
data['FaultsFound'] = data['CleanedNotes'].apply(extract_faults)
for faults in data['FaultsFound']:
    all_faults.update(faults)

# Extract data for the bar chart
bar_data = pd.DataFrame(all_faults.most_common(), columns=['Issue', 'Occurrences']).sort_values(by='Occurrences', ascending=False)

# Function to count occurrences of each fault by date for the line chart
def count_faults_by_date(df, issue):
    filtered_data = df[df['CleanedNotes'].str.contains(issue)]
    return filtered_data.groupby(filtered_data['ActualStartedOn'].dt.date).size()

# Extract time series data for plotting
top_issues = bar_data['Issue'][:10]
time_series_data = {issue: count_faults_by_date(data, issue) for issue in top_issues}

# Create subplots
fig = make_subplots(rows=1, cols=2, subplot_titles=("Total Fault Occurrences", "Cumulative Faults Over Time"),
                    specs=[[{"type": "bar"}, {"type": "scatter"}]])

# Adding bar chart for total occurrences
fig.add_trace(go.Bar(x=bar_data['Issue'], y=bar_data['Occurrences'], name='Total Occurrences'), row=1, col=1)

# Adding cumulative counts to the second subplot
for issue, counts in time_series_data.items():
    cumulative_counts = counts.cumsum()
    fig.add_trace(go.Scatter(x=cumulative_counts.index, y=cumulative_counts.values, mode='lines+markers', name=f'{issue} (Cumulative)', visible='legendonly'), row=1, col=2)

fig.update_layout(
    title='ACF Top Issues',
    showlegend=True
)

fig.update_xaxes(title_text="Issue", row=1, col=1)
fig.update_yaxes(title_text="Occurrences", row=1, col=1)
fig.update_xaxes(title_text="Date", row=1, col=2)
fig.update_yaxes(title_text="Cumulative Counts", row=1, col=2)

# Use the browser renderer to open the plot in a web browser
fig.show(renderer="browser")

