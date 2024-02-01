import pandas as pd
import boto3
from io import StringIO
import plotly.express as px
import plotly.graph_objs as go

s3 = boto3.client("s3")

data_2022 = pd.read_csv('./data/AverageHouseHoldSize2022.csv', index_col=0)
data_2022= data_2022.transpose()
data_2022 = data_2022.dropna(axis=1)

data_2012 = pd.read_csv('./data/AverageHouseHoldSize2012.csv', index_col=0)
data_2012= data_2012.transpose()
data_2012 = data_2012.dropna(axis=1)

state_abbreviations = {
'Alabama': 'AL',
'Alaska': 'AK',
'Arizona': 'AZ',
'Arkansas': 'AR',
'California': 'CA',
'Colorado': 'CO',
'Connecticut': 'CT',
'Delaware': 'DE',
'District of Columbia': 'DC',
'Florida': 'FL',
'Georgia': 'GA',
'Hawaii': 'HI',
'Idaho': 'ID',
'Illinois': 'IL',
'Indiana': 'IN',
'Iowa': 'IA',
'Kansas': 'KS',
'Kentucky': 'KY',
'Louisiana': 'LA',
'Maine': 'ME',
'Maryland': 'MD',
'Massachusetts': 'MA',
'Michigan': 'MI',
'Minnesota': 'MN',
'Mississippi': 'MS',
'Missouri': 'MO',
'Montana': 'MT',
'Nebraska': 'NE',
'Nevada': 'NV',
'New Hampshire': 'NH',
'New Jersey': 'NJ',
'New Mexico': 'NM',
'New York': 'NY',
'North Carolina': 'NC',
'North Dakota': 'ND',
'Ohio': 'OH',
'Oklahoma': 'OK',
'Oregon': 'OR',
'Pennsylvania': 'PA',
'Rhode Island': 'RI',
'South Carolina': 'SC',
'South Dakota': 'SD',
'Tennessee': 'TN',
'Texas': 'TX',
'Utah': 'UT',
'Vermont': 'VT',
'Virginia': 'VA',
'Washington': 'WA',
'West Virginia': 'WV',
'Wisconsin': 'WI',
'Wyoming': 'WY',
'Puerto Rico': 'PR'
}

def dataframe_cleanup(df):
    
    #Clean up dataframe columns
    dict_data = df.to_dict()

    new_dict = {'State': [], 'Owner_occupied': [], 'Renter_occupied': []}
    for k, v in dict_data.items():
        if k=='Owner occupied':
            new_dict['State'].extend(list(v.keys())),
            new_dict['Owner_occupied'].extend(v.values())

        if k=='Renter occupied':
            new_dict['Renter_occupied'].extend(v.values())


    #Add state abbreviations to the dataframe column
    df = pd.DataFrame(new_dict, columns=['State', 'Owner_occupied','Renter_occupied'])
    df['Code'] = df['State'].map(state_abbreviations)
            
    return df

def make_map(data_year: str):

    df = dataframe_cleanup(data_2022)

    data = dict(type = 'choropleth',
                colorscale = 'Portland',
                locations = df['Code'],
                locationmode = 'USA-states',
                z=df['Owner_occupied'],
                colorbar = {'title':'Average Number of People'})

    layout = dict(
        title = {'text': f'{data_year} US Average Household Size by Home Owner', 'x':0.5, 'xanchor': 'center'},
        geo = dict(scope = 'usa')
    )

    choromap_own = go.Figure(data = [data],layout = layout)
    choromap_own.update_layout(
    plot_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    paper_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    font=dict(
        color='#FFFFFF'  # change 'color_of_your_choice' to your desired color
    )
    )

    data_rent = dict(type = 'choropleth',
                colorscale = 'Portland',
                locations = df['Code'],
                locationmode = 'USA-states',
                z=df['Renter_occupied'],
                colorbar = {'title':'Average Number of People'})

    layout = dict(
        title = {'text': f'{data_year} US Average Household Size by Renter', 'x':0.5, 'xanchor': 'center'},
        geo = dict(scope = 'usa'),
    )

    choromap = go.Figure(data = [data_rent],layout = layout)
    choromap.update_layout(
    plot_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    paper_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    font=dict(
        color='#FFFFFF'  # change 'color_of_your_choice' to your desired color
    )
    )

    choromap_own_html = choromap_own.to_html(full_html=False, include_plotlyjs='cdn')
    choromap_html = choromap.to_html(full_html=False, include_plotlyjs='cdn')

    return choromap_own_html, choromap_html

"""Physical housing occupancy data"""

def convert_value(value):
    if '%' in value:
        return float(value.replace('%', '')) / 100  # Convert percentage to a decimal
    else:
        return int(value.replace(',', ''))  # Remove commas and convert to integer
    
def clean_house_char_headers(val):
    if isinstance(val, str):
        if 'Occupied' in val:
            val = val.split("!!")[0]
            val = val + "_total"
        elif 'Percent occupied housing units' in val:
            val = val.split("!!")[0]
            val = val + "_total_percent"
        elif 'Owner-occupied housing'in val:
            val = val.split("!!")[0]
            val = val + "_owner"
        elif 'Percent owner-occupied housing units' in val:
            val = val.split("!!")[0]
            val = val + "_own_percent"
        elif 'Renter-occupied housing units' in val:
            val = val.split("!!")[0]
            val = val + "_renter"
        elif 'Percent renter-occupied' in val:
            val = val.split("!!")[0]
            val = val + "_rent_percent"
        else:
            val = val.split("!!")[0]
        return val
    else:
        return val

def data_cleanup(df):

    df_dict = df.to_dict()
    cleaned_dict = {state: {key.strip(): convert_value(value) for key, value in data.items()} for state, data in df_dict.items()}

    # Create nested dictionary for each state to combine data by state
    new_dict = {}
    for state_attr, attr_values in cleaned_dict.items():
        state, attribute = state_attr.split("_", 1)
        if state not in new_dict:
            new_dict[state] = {}
        if attribute not in new_dict[state]:
            new_dict[state][attribute] = {}
        for attr, value in attr_values.items():
            new_dict[state][attribute][attr] = value

    # Create category by total units in state, homeowner units and renter units
    total_unit_lst = [{k: v.get('total')} for k, v in new_dict.items() if v.get('total') is not None]
    owner_unit_lst = [{k: v.get('owner')} for k, v in new_dict.items() if v.get('owner') is not None]
    renter_unit_lst = [{k: v.get('renter')} for k, v in new_dict.items() if v.get('renter') is not None]

    # Function to convert list of dictionaries into a DataFrame
    def create_df(lst):
        df = pd.concat({k: pd.DataFrame.from_dict(v, 'index') for d in lst for k, v in d.items()}, axis=0)
        df.reset_index(inplace=True)
        df.columns = ['State', 'Value', 'Count']
        df['Code'] = df['State'].map(state_abbreviations)
        return df

    # Convert the list of nested dictionaries into a DataFrame
    df_total = create_df(total_unit_lst)
    df_owner = create_df(owner_unit_lst)
    df_renter = create_df(renter_unit_lst)

    return df_total, df_owner, df_renter

house_char_data = pd.read_csv('./data/Physical_Housing_Occup.csv', index_col=0)
house_char_data = house_char_data.rename(columns=clean_house_char_headers)

units_in_struc = house_char_data.iloc[[2,3,4,5,6,7,8]]
year_struc = house_char_data.iloc[[10,11,12,13,14,15,16]]
#rooms = house_char_data.iloc[[18,19,20,21,22]]
bedroom = house_char_data.iloc[[24,25,26,27]]
#vehicles = house_char_data.iloc[[32,33,34,35]]
#house_heat_fuel = house_char_data.iloc[[39,40,41,42,43,44,45]]


def home_pie(state:str,data_year: str):
    df = data_cleanup(units_in_struc)[0]
    target_state = df[df['State']==state]
    # Create the bar chart
    fig = px.pie(target_state, values='Count', names='Value', title=f'{data_year} Typical house type in {state}')
    fig.update_layout(
    plot_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    paper_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    font=dict(
        color='#FFFFFF'  # change 'color_of_your_choice' to your desired color
    )
    )
    html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return html

def bedroom_size(state:str, data_year:str):
    df_bed_total, df_bed_owner, df_bed_renter = data_cleanup(bedroom)
    target_state_own = df_bed_owner[df_bed_owner['State']==state]
    target_state_rent = df_bed_renter[df_bed_renter['State']==state]
    target_state_own['Type'] = 'Homeowners'
    target_state_rent['Type'] = 'Renters'

    # Concatenate the dataframes
    df = pd.concat([target_state_own, target_state_rent])

    # Create the bar graph
    fig = px.bar(df, x='Value', y='Count', color='Type', barmode='group', 
                facet_row='State', labels={'Count':'Number of Units', 'Value':'Number of Bedrooms'}, 
                title=f'{data_year} Number of Bedrooms in Homes for Homeowners vs Renters')
    fig.update_layout(
    plot_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    paper_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    font=dict(
        color='#FFFFFF'  # change 'color_of_your_choice' to your desired color
    )
    )
    html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return html

""""Fertility Rates"""

def clean_headers(val):
    if isinstance(val, str):
        if 'Total' in val:
            val = val.split("!!")[0]
            val = val + "_total"
        elif 'Women with births in the past 12 months!!Number!!Estimate' in val:
            val = val.split("!!")[0]
            val = val + "_births"
        elif 'Women with births in the past 12 months!!Rate per 1,000 women!!Estimate' in val:
            val = val.split("!!")[0]
            val = val + "_thou"
        else:
            val = val.split("!!")[0]
        return val
    else:
        return val
    
fert_data = pd.read_excel('./data/fertility_data.xlsx', index_col=0)
fert_data = fert_data.rename(columns=clean_headers)

births_data_22 = fert_data.iloc[[1]]
births_data_21 = fert_data.iloc[[12]]
births_data_19 = fert_data.iloc[[23]]
births_data_18 = fert_data.iloc[[34]]
births_data_17 = fert_data.iloc[[45]]
births_data_16 = fert_data.iloc[[56]]
births_data_15 = fert_data.iloc[[67]]
births_data_14 = fert_data.iloc[[78]]
births_data_13 = fert_data.iloc[[89]]
births_data_12 = fert_data.iloc[[100]]
births_data_11 = fert_data.iloc[[111]]
births_data_10 = fert_data.iloc[[122]]
    
def fert_data_cleanup(df, year:str):

    df_dict = df.to_dict()
    cleaned_dict = {state: {key.strip(): value for key, value in data.items()} for state, data in df_dict.items()}

    # Create nested dictionary for each state to combine data by state
    new_dict = {}
    for state_attr, attr_values in cleaned_dict.items():
        state, attribute = state_attr.split("_", 1)
        if state not in new_dict:
            new_dict[state] = {}
        if attribute not in new_dict[state]:
            new_dict[state][attribute] = {}
        for attr, value in attr_values.items():
            new_dict[state][attribute][attr] = value

    # Create category by total units in state, homeowner units and renter units
    total_lst = [{k: v.get('total')} for k, v in new_dict.items() if v.get('total') is not None]
    birth_lst = [{k: v.get('births')} for k, v in new_dict.items() if v.get('births') is not None]
    thou_lst = [{k: v.get('thou')} for k, v in new_dict.items() if v.get('thou') is not None]

    # Function to convert list of dictionaries into a DataFrame
    def create_df(lst):
        #count_column = f'Count'
        df = pd.concat({k: pd.DataFrame.from_dict(v, 'index') for d in lst for k, v in d.items()}, axis=0)
        df.reset_index(inplace=True)
        df.columns = ['State', 'Value', 'Count']
        df['Code'] = df['State'].map(state_abbreviations)
        return df

    # Convert the list of nested dictionaries into a DataFrame
    df_total = create_df(total_lst)
    df_birth = create_df(birth_lst)
    df_thou = create_df(thou_lst)

    return df_total, df_birth, df_thou

# List of data and corresponding years
data_years = [(births_data_22, '2022'), (births_data_21, '2021'), (births_data_19, '2019'), 
              (births_data_18, '2018'), (births_data_17, '2017'), (births_data_16, '2016'), 
              (births_data_15, '2015'), (births_data_14, '2014'), (births_data_13, '2013'), 
              (births_data_12, '2012'), (births_data_11, '2011'), (births_data_10, '2010')]

def consolidate_dataframe(data_years: list):

    # Initialize dictionaries to store dataframes
    fert_pop_dict = {}
    birth_dict = {}
    birth_thou_dict = {}

    # Initialize a list to store dataframes
    df_list = []

    # Loop over all data and years
    for data, year in data_years:
        fert_pop, birth, birth_thou = fert_data_cleanup(data, year)
        fert_pop_dict[year] = fert_pop
        birth_dict[year] = birth
        birth_thou_dict[year] = birth_thou

        # Add a 'Year' column to the dataframe
        birth['Year'] = year
        # Append the dataframe to df_list
        df_list.append(birth)

    # Concatenate all dataframes in df_list
    all_years_df = pd.concat(df_list)

    # Reset the index of all_years_df
    all_years_df.reset_index(drop=True, inplace=True)

    return all_years_df, fert_pop_dict, birth_dict, birth_thou_dict

def chart_births():
    df =consolidate_dataframe(data_years)[0]
    df_sum = df.groupby('Year')['Count'].sum().reset_index()
    fig = px.line(df_sum, x='Year', y='Count', title='Total Births by year in United States')
    fig.update_layout(
    plot_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    paper_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    font=dict(
        color='#FFFFFF'  # change 'color_of_your_choice' to your desired color
    )
    )
    fig.update_traces(line=dict(color='#e44c65', width=6))
    html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return html

def chart_state_births(state:str):
    df =consolidate_dataframe(data_years)[0]
    target_state = df[df['State']==state]
    fig = px.line(target_state, x='Year', y='Count', title=f'Total Births by year in {state}')
    fig.update_layout(
    plot_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    paper_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    font=dict(
        color='#FFFFFF'  # change 'color_of_your_choice' to your desired color
    )
    )
    fig.update_traces(line=dict(color='#e44c65', width=6))
    html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return html
