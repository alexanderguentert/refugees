# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

# load data
filename='UNdata_refugees.csv'
refugees = pd.read_csv(filename,sep=';')

# define data for filtering
all_categories = ['Refugees*','Refugees assisted by UNHCR','Total refugees and people in refugee-like situations**','Total refugees and people in refugee-like situations assisted by UNHCR']
filter_years = pd.Series(refugees['Year'].unique()).dropna(how='any').sort_values(ascending=False).reset_index(drop=True)
dropdown_list= pd.Series(refugees['Country or territory of origin'].unique()).dropna(how='any').sort_values().reset_index(drop=True)
footnotes = '''**Footnotes**:

*Persons recognized as refugees under the 1951 UN Convention/1967 Protocol, the 1969 OAU Convention, in accordance with the UNHCR Statute, persons granted a complementary form of protection and those granted temporary protection. In the absence of Government estimates, UNHCR has estimated the refugee population in 24 industrialized countries based on 10 years of individual refugee recognition.

**The category of people in refugee-like situations is descriptive in nature and includes groups of persons who are outside their country or territory of origin and who face protection risks similar to those of refugees, but for whom refugee status has, for practical or other reasons, not been ascertained.

**Source**: [http://data.un.org/Data.aspx?d=UNHCR&f=indID%3aType-Ref](http://data.un.org/Data.aspx?d=UNHCR&f=indID%3aType-Ref)

Created by Alexander Güntert. See also: [https://plot.ly/~alexander.guentert](https://plot.ly/~alexander.guentert)
'''



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Refugee Movements'),
	
    html.Div(children='''
        See where refugees come frome and where they end up, based on data from the United Nations (http://data.un.org).
    '''),
    html.Label('Select a country of origin:'),
    dcc.Dropdown(
		id='country-origin',
        options=[{'label': i, 'value': i} for i in dropdown_list],
        value=dropdown_list[0]
    ),
	html.Label('Select a year:'),
    dcc.Dropdown(
        id='years',
        options=[{'label': i, 'value': i} for i in filter_years],
        value=filter_years[0]
    ),
    html.Label('Category:'),
    dcc.RadioItems(
		id='category',
        options=[{'label': i, 'value': i} for i in all_categories],
        value=all_categories[0],
        #labelStyle={'display': 'inline-block'}
    ),
    html.Div([dcc.Graph(id='pie-chart'),], style={'width': '55%', 'display': 'inline-block'}),
	html.Div([dcc.Graph(id='map'),],style={'width': '45%', 'display': 'inline-block'}),
	
	dcc.Graph(id='sankey-graph'),
    #dcc.Graph(id='sankey-graph', figure={...data...})
    html.Div([
    dcc.Markdown(children=footnotes)
])
])

@app.callback(
	dash.dependencies.Output('pie-chart', 'figure'),
	[dash.dependencies.Input('country-origin', 'value'),
	dash.dependencies.Input('years', 'value'),
	dash.dependencies.Input('category', 'value'),
	]
	)
def update_graph_pie(country_origin,years,category):#,refugees,filter_year,filter_country,filter_category):
	filter_country=country_origin
	filter_category=category
	filter_year=years
	r2016 = refugees.loc[(refugees['Year']==filter_year) & (refugees[filter_category].notnull()),]
	Verteilung=r2016[['Country or territory of origin',filter_category]].groupby('Country or territory of origin').sum()
	# liste mit Nullen für Pull
	PullList = [0 for x in range(len(Verteilung.index))]
	# ersetze einen Wert zum Pullen
	PullList[Verteilung.index.get_loc(filter_country)]=0.3
	trace = go.Pie(labels=Verteilung.index, values=Verteilung[filter_category], pull=PullList,textposition='inside')
	layout = dict(title = 'Country of Origin in comparison',)
	fig = dict(data=[trace], layout=layout)
	return fig
	#py.iplot(fig)					


#map
@app.callback(
	dash.dependencies.Output('map', 'figure'),
	[dash.dependencies.Input('country-origin', 'value'),
	dash.dependencies.Input('years', 'value'),
	dash.dependencies.Input('category', 'value'),
	]
	)
def update_map(country_origin,years,category):#,refugees,filter_year,filter_country,filter_category):
	filter_country=country_origin
	filter_category=category
	filter_year=years
	r2016 = refugees.loc[(refugees['Year']==filter_year) & (refugees[filter_category].notnull()) & (refugees[filter_category]>0) & (refugees['Country or territory of origin']==filter_country),]
	data=[]
	for C in r2016['Country or territory of asylum or residence'].unique():
		data.append(
			dict(
				type = 'scattergeo',
				locationmode = 'country names',
				locations = [filter_country,C],
				mode = 'lines',
				line = dict(width = 2,color = 'blue',),
			)
		)
	layout = dict(
		title = 'Origin and destination countries',
		showlegend=False,
		geo = dict(showframe = False,
				   showcoastlines = True, 
				   showland = True,
				   showcountries=True,
				   landcolor = 'rgb(229, 229, 229)',
				   countrycolor = 'rgb(255, 255, 255)',
				   coastlinecolor = "rgb(255, 255, 255)",		   
		)
	)
	fig = dict( data=data, layout=layout )
	return fig

# sankey
@app.callback(
	dash.dependencies.Output('sankey-graph', 'figure'),
	[dash.dependencies.Input('country-origin', 'value'),
	dash.dependencies.Input('years', 'value'),
	dash.dependencies.Input('category', 'value'),
	]
	)

def update_graph_sankey(country_origin,years,category):#,refugees,filter_year,filter_country,filter_category):
	filter_country=country_origin
	filter_category=category
	filter_year=years
	#r2016 = refugees.loc[refugees['Year']==filter_year,]
	r2016 = refugees.loc[(refugees['Year']==filter_year) & (refugees[filter_category].notnull()),]
	r2016f = r2016[r2016['Country or territory of origin']==filter_country]#.dropna(how='any')
	#Erstelle Liste mit den Ländern im Filtern
	countrylistf = r2016f['Country or territory of asylum or residence'].append(r2016f['Country or territory of origin'])
	countrylistf = pd.Series(countrylistf.unique())
	#Codiere Ländernamen mit Nummern aus Länderliste
	r2016c = r2016f[['Country or territory of origin','Country or territory of asylum or residence',filter_category]]
	r2016c = r2016c.replace(countrylistf.values,countrylistf.index.values)
	return {
	        'data': [
			{
			  "domain": {
				"x": [0, 1], 
				"y": [0, 1]
			  }, 
			  "link": { 
				"source": r2016c['Country or territory of origin'], 
				"target": r2016c['Country or territory of asylum or residence'], 
				"value":  r2016c[filter_category]
			  }, 
			  "node": { 
				"label": countrylistf, 
				"line": {
				  "color": "black", 
				  "width": 0
				}, 
				"pad": 10, 
				"thickness": 30
			  }, 
			  "orientation": "h", 
			  "type": "sankey", 
			  "valueformat": ".0f"
			}
        ],
			'layout': {
				'title' : filter_category+"<br>Country of Origin: "+filter_country+" ("+str(filter_year)+")",
				'autosize' : False,
				'width' :1200,
				#height=1200,
				'height' : 800+countrylistf.shape[0]*5,
			}
	}

if __name__ == '__main__':
    app.run_server(debug=True)
