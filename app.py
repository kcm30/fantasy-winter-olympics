import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

app = dash.Dash()
#app.config['suppress_callback_exceptions']=True
server = app.server

#########################
### Data Manipulation ###
#########################
medal_count = pd.read_html('http://www.nbcolympics.com/medals')[0]
teams = pd.melt(pd.read_json("country_selections.json"))
teams.columns = ['Team', 'Country']
data = pd.merge(teams, medal_count, how='left').fillna(0)
data['Place'] = 0

player_data = (data.groupby("Team")
                   .sum()
                   .reset_index()[['Place', 'Team', 'Total', 'Gold', 'Silver', 'Bronze']]
                   .sort_values(['Total', 'Gold', 'Silver', 'Bronze'], ascending=False))
player_data['Place'] = range(1, 8)

country_data = (pd.merge(teams, medal_count, on='Country', how='outer')
				  .fillna(0))
country_data.loc[country_data.Place == 0, 'Place'] = country_data.Place.max() + 1 

#########################
# Dashboard/Layout view #
#########################


def generate_table(dataframe):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(len(dataframe))],
    )



app = dash.Dash()

app.layout = html.Div([
	html.Div([
    	html.H4(children='Minkus Family Standings'),
    	generate_table(player_data)], className='six columns'),
	html.Div([
		html.H4(children="Country Standings"),
		html.Label('View Team'),
    	dcc.Dropdown(id='dropdown',
        	options=[
				{'label': 'All Countries', 'value': 'All Countries'},
            	{'label': 'Dan', 'value': 'Dan'},
            	{'label': 'Derek', 'value': 'Derek'},
            	{'label': 'Gail', 'value': 'Gail'},
				{'label': 'Jeff', 'value': 'Jeff'},
				{'label': 'Kevin', 'value': 'Kevin'},
				{'label': 'Laura', 'value': 'Laura'},
				{'label': 'Sarah', 'value': 'Sarah'}
        	],
        	value='All Countries'
    	), 
		html.Div(id='output-table')
		], className='six columns')
])

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

#########################
### Control elements ####
#########################

@app.callback(
    Output(component_id='output-table', component_property='children'),
    [Input(component_id='dropdown', component_property='value')]
)
def generate_responsive_table(value):
	dataframe = country_data
	if value != 'All Countries':
		dataframe = (dataframe[dataframe.Team == value].drop('Team', axis=1)
                                                       .sort_values(['Total', 'Gold', 'Silver', 'Bronze'], ascending=False))
	else:
		dataframe = (dataframe.drop('Team', axis=1)
                              .drop_duplicates()
                              .sort_values(['Total', 'Gold', 'Silver', 'Bronze'], ascending=False))
	return generate_table(dataframe)


if __name__ == '__main__':
    app.run_server(debug=True)
