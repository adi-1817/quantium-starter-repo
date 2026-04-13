import pandas as pd 
import dash 
from dash import dcc, html 
import plotly.express as px 

#Loading Data
df = pd.read_csv("../data/processed_data.csv")

#Convert Date
df["date"] = pd.to_datetime(df["date"])

#Aggregate Sales by Date
df = df.groupby("date")["sales"].sum().reset_index()

#Sort by Date
df = df.sort_values("date")

#Create Line Chart
fig = px.line(df, x="date", y="sales", title="Sales Over Time")

#Add Vertical Line for Jan 15, 2021
fig.add_vline(x="2021-01-15", line_dash="dash", line_color="red")

#Initialize the app
app = dash.Dash(__name__)

#Layout
app.layout = html.Div([
    html.H1('Sales Trend Analysis'),
    dcc.Graph(figure=fig)
])

#Run server
if __name__ == "__main__":
    app.run(debug=True)
