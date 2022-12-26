# -*- coding: utf-8 -*-
import plotly.graph_objs as go
import pandas as pd
import streamlit as st

# load data
filename='UNdata_refugees.csv'
filename='UNdata_Export_20221216_090103463.csv'
refugees = pd.read_csv(filename,sep=';')

## colnames
COL_CTR_RESIDENCE = 'Country or territory of asylum or residence'
COL_CTR_ORIGIN = 'Country or territory of origin'
COL_YEAR = 'Year'
COLS_CATEGORIES = [
    'Refugees*',
    'Refugees assisted by UNHCR',
    'Total refugees and people in refugee-like situations**',
    'Total refugees and people in refugee-like situations assisted by UNHCR',
]

# define data for filtering
all_categories = COLS_CATEGORIES
filter_years = pd.Series(
                    refugees[COL_YEAR].unique()
                    ).dropna(how='any').sort_values(ascending=False).reset_index(drop=True).astype(int)

dropdown_list= pd.Series(
                    refugees[COL_CTR_ORIGIN].unique()
                    ).dropna(how='any').sort_values().reset_index(drop=True)

footnotes = '''**Footnotes**:

*Persons recognized as refugees under the 1951 UN Convention/1967 Protocol, the 1969 OAU Convention, in accordance with the UNHCR Statute, persons granted a complementary form of protection and those granted temporary protection. In the absence of Government estimates, UNHCR has estimated the refugee population in 24 industrialized countries based on 10 years of individual refugee recognition.

**The category of people in refugee-like situations is descriptive in nature and includes groups of persons who are outside their country or territory of origin and who face protection risks similar to those of refugees, but for whom refugee status has, for practical or other reasons, not been ascertained.

**Source**: [http://data.un.org/Data.aspx?d=UNHCR&f=indID%3aType-Ref](http://data.un.org/Data.aspx?d=UNHCR&f=indID%3aType-Ref)

Created by Alexander Güntert. See also: [https://github.com/alexanderguentert/refugees](https://github.com/alexanderguentert/refugees)
'''


def update_graph_pie(country_origin, years, category):
    """
    pie chart with all countries. country_origin is pulled out
    """
    filter_country = country_origin
    filter_category = category
    filter_year = years
    filtered_df = refugees.loc[
        (refugees[COL_YEAR]==filter_year) & 
        (refugees[filter_category].notnull()),
        ]
    grouped_df = filtered_df[[COL_CTR_ORIGIN,filter_category]].groupby(COL_CTR_ORIGIN).sum()
    # liste mit Nullen für Pull
    PullList = [0 for x in range(len(grouped_df.index))]
    # ersetze einen Wert zum Pullen
    PullList[grouped_df.index.get_loc(filter_country)]=0.3
    trace = go.Pie(
        labels=grouped_df.index, 
        values=grouped_df[filter_category], 
        pull=PullList,
        textposition='inside',
        )
    layout = dict(title='Country of Origin in comparison',)
    fig = dict(data=[trace], layout=layout)
    return fig


def update_map(country_origin, years, category):
    """
    map with lines from country_origin to destination countries
    """
    filter_country = country_origin
    filter_category = category
    filter_year = years
    filtered_df = refugees.loc[
        (refugees[COL_YEAR]==filter_year) & 
        (refugees[filter_category].notnull()) & 
        (refugees[filter_category]>0) & 
        (refugees[COL_CTR_ORIGIN]==filter_country),
        ]
    data = []
    for country in filtered_df['Country or territory of asylum or residence'].unique():
        data.append(
            dict(
                type = 'scattergeo',
                locationmode = 'country names',
                locations = [filter_country, country],
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
    fig = dict(data=data, layout=layout)
    return fig


def update_graph_sankey(country_origin, years, category):
    filter_country = country_origin
    filter_category = category
    filter_year = years
    
    filtered_df = refugees.loc[
        (refugees[COL_YEAR]==filter_year) & 
        (refugees[filter_category].notnull()) & 
        (refugees[COL_CTR_ORIGIN]==filter_country),
        ]
    
    #Erstelle Liste mit den Ländern im Filtern
    countrylistf = filtered_df[COL_CTR_RESIDENCE].append(filtered_df[COL_CTR_ORIGIN])
    countrylistf = pd.Series(countrylistf.unique())
    #Codiere Ländernamen mit Nummern aus Länderliste
    
    coded_df = filtered_df[
        [COL_CTR_ORIGIN, COL_CTR_RESIDENCE, filter_category]
        ].replace(
            countrylistf.values,
            countrylistf.index.values
            )
    
    return {
            'data': [
            {
              "domain": {
                "x": [0, 1], 
                "y": [0, 1]
              }, 
              "link": { 
                "source": coded_df[COL_CTR_ORIGIN], 
                "target": coded_df[COL_CTR_RESIDENCE], 
                "value":  coded_df[filter_category]
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
                'autosize' : True,
                #'width' :1200,
                # height=1200,
                'height' : 800+countrylistf.shape[0]*5,
            }
    }

# streamlit app
st.set_page_config('Refugee Movements')
st.title('Refugee Movements')
st.markdown("""See where refugees come frome and where they end up, based on data from the United Nations (http://data.un.org).""")
selected_country = st.sidebar.selectbox(
                            'Select a country of origin:',
                            dropdown_list,
                            )
selected_year = st.sidebar.selectbox('Select a year:', filter_years,)
selected_cat = st.sidebar.radio('Category:', all_categories,)



fig_pie = update_graph_pie(selected_country, selected_year, selected_cat)
st.plotly_chart(fig_pie)

fig_sankey = update_graph_sankey(selected_country,selected_year,selected_cat)
st.plotly_chart(fig_sankey)

fig_map = update_map(selected_country,selected_year,selected_cat)
st.plotly_chart(fig_map)

st.markdown(footnotes)

