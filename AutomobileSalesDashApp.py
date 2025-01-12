# Dependencies
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px


# Loading the dataset
dataset = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN' \
'-SkillsNetwork/Data%20Files/historical_automobile_sales.csv'
df = pd.read_csv(dataset)


# Initializing the Dash app
app = dash.Dash()


# Setting the title of the dashboard
app.title = 'Automobile Statistics Dashboard'


# Creating the dropdown menu options
dropdown_options = [
    {'label': 'Global statistics', 'value': 'Global Statistics'},
    {'label': 'Recession Statistics', 'value': 'Recession Statistics'}
]


# Formatting column names and listing all unique observations (year)
df.columns = [i.replace('_', ' ').title() for i in df.columns]
annual_observations_list = list(set(df.Year))


# Layout of dashboard
app.layout = html.Div([
    # Adding a title to the dashboard
    html.H1('Automobile Sales Statistics Dashboard', style={'textAlign': 'center', 'font-size': 30}),
    html.P("Select Statistics 📊🚙:"),
    # Adding two dropdown menus
    html.Div([
        dcc.Dropdown(
            id = 'dropdown-statistics', 
            options = dropdown_options,
            placeholder = 'Select a report type',
            style={'textAlign': 'center'})
        
    ]),
    html.Div(dcc.Dropdown(
        id = 'select-year',
        options = [{'label': i, 'value': i} for i in annual_observations_list],
        value = annual_observations_list[0],
        placeholder = 'Select a year'
    )),
    html.Div([# Adding a division for output display
        html.Div(id = 'output-container', className = 'chart-grid', style = {'width': '100%'}),
    ])
],
    style = {'width': '80%','margin': '0 auto'}
    )


# Callback for disabling the years dropdown
@app.callback(
    Output(component_id = 'select-year', component_property = 'disabled'),
    Input(component_id = 'dropdown-statistics', component_property = 'value')
)
def update_input_container(selected_statistics):
    return selected_statistics is None


# Callback for returning statistics based on selected years and type
@app.callback(
    Output(component_id = 'output-container', component_property = 'children'),
    [Input(component_id = 'select-year', component_property = 'value'),
     Input(component_id = 'dropdown-statistics', component_property = 'value')]
)

def update_output_container(input_year, selected_statistics):
    
    # Conditions for ploting Recession Statistics
    if selected_statistics == 'Recession Statistics':        
        recession_data = df[(df.Recession == 1) & (df.Year == input_year)]        
        if len(recession_data) < 2:
            return html.P(f'🚨 Attention! There is no relevant data to display for {input_year}. 😞',
                          style = {'color': 'red', 'fontSize': '18px'})
        else:    
            # Plot 1: Automobile sales fluctuation over recession periods
            recession_avg_sales_period = recession_data.groupby('Month')['Automobile Sales'].mean().reset_index()
            rec_chart1 = dcc.Graph(
                figure = px.line(
                    recession_avg_sales_period, x = 'Month', y = 'Automobile Sales',
                               title = f'Average Automobile Sales Fluctuation for Recession Periods ({input_year})'
                )
            )    
            # Plot 2: Report the average number of vehicles sold by vehicle type
            recession_avg_sales_type = recession_data.groupby('Vehicle Type')['Automobile Sales'].mean().reset_index()
            rec_chart2 = dcc.Graph(
                figure = px.bar(
                    recession_avg_sales_type, x = 'Vehicle Type', y = 'Automobile Sales',
                    title = f'Average Vehicle Sales by Type in Recession of {input_year}'
                )
            )    
            # Plot 3: Pie chart for total expenditure share by vehicle type during recessions
            recession_exp = recession_data.groupby('Vehicle Type')['Advertising Expenditure'].sum().reset_index()
            rec_chart3 = dcc.Graph(
                figure = px.pie(
                    recession_exp, values = 'Advertising Expenditure', names = 'Vehicle Type',
                    title = f'Total Expenditure by Vehicle Type During the Recession of {input_year}'
                )
            )    
            # Plot 4: Bar chart for the effect of unemployment rate on vehicle type and sales
            unemployment_rec = recession_data.groupby(['Unemployment Rate', 'Vehicle Type'])['Automobile Sales'].sum().reset_index()
            rec_chart4 = dcc.Graph(
                figure = px.bar(
                    unemployment_rec, x = 'Unemployment Rate', y = 'Automobile Sales', color = 'Vehicle Type',
                    title = f'Effect of Unemployment Rate on Vehicle Type and Sales in Recession of {input_year}'
                ).update_layout(
                    bargap = .02, bargroupgap = .1
                )
            )
    
            return [
                html.Div(className = 'chart-item', children = [html.Div(children = rec_chart1), html.Div(children = rec_chart2)]),
                html.Div(className = 'chart-item', children = [html.Div(children = rec_chart3), html.Div(children = rec_chart4)])
            ]
            
    # Plots for annual statistics
    elif selected_statistics == 'Yearly Statistics':
               
        # Plot 1: Line plot for displaying the annual sales trend
        total_sales_year = df.groupby('Year')['Automobile Sales'].mean().reset_index()
        glb_chart1 = dcc.Graph(
            figure = px.line(
                total_sales_year, x = 'Year', y = 'Automobile Sales',
                title = f'Annual Sales Trend by Vehicle Type ({df.Year.min()} - {df.Year.max()})'
                            )
        )
        # Plot 2: Line plot for reporting the monthly sales fluctuation
        total_sales_month = df.groupby('Month')['Automobile Sales'].mean().reset_index()
        glb_chart2 = dcc.Graph(
            figure = px.line(total_sales_month, x = 'Month', y = 'Automobile Sales',
                           title = f'Monthly Sales Fluctuation in {input_year}')
        )
        # Plot 3: Bar chart for displaying the average number of vehicles sold in a given year
        avg_sales_type = df.groupby('Vehicle Type')['Automobile Sales'].mean().reset_index()
        glb_chart3 = dcc.Graph(
            figure=px.bar(
                avg_sales_type, x = 'Vehicle Type', y = 'Automobile Sales',
                          title = 'Average Sales by Vehicle Type in {input_year}'
                         )
        )
        # Plot 4: Total Advertisement Expenditure for each vehicle using pie chart
        total_exp_type = df.groupby('Vehicle Type')['Advertising Expenditure'].sum().reset_index()
        glb_chart4 = dcc.Graph(
            figure = px.pie(total_exp_type, values = 'Advertising Expenditure', names = 'Vehicle Type',
                          title = f'Total Expenditure by Vehicle Type ({df.Year.min()} - {df.Year.max()})')
        )

        return [
            html.Div(className = 'chart-item', children = [html.Div(children = glb_chart1), html.Div(children = glb_chart2)]),
            html.Div(className = 'chart-item', children = [html.Div(children = glb_chart3), html.Div(children = glb_chart4)])
        ]

    else:
        return None


# Running the Dash app
if __name__ == '__main__':
    app.run()