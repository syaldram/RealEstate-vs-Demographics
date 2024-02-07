import pandas as pd
#import boto3
#import os
#from io import StringIO
import plotly.express as px
import plotly.graph_objs as go

#s3 = boto3.client("s3")

#bucket_name = os.environ["s3BucketName"]

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

def clean_headers(val):
    if isinstance(val, str):
        val = val.split("!!")[0]
        return val
    else:
        return val
    
#obj = s3.get_object(Bucket=bucket_name, Key='data/SexByAge2022.csv')
#data_pop = pd.read_csv(StringIO(obj['Body'].read().decode('utf-8')), index_col=0)
    
data_pop = pd.read_csv('./data/SexByAge2022.csv', index_col=0)
data_pop = data_pop.rename(columns=clean_headers)

male_data = data_pop.iloc[[2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]]
female_data = data_pop.iloc[[26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48]]

male_data.reset_index()
female_data.reset_index()

def cleanup_dataframe(df, gender: str):

    dict_data = df.to_dict()

    #Clean up label column for white spaces and convert population size to integers
    cleaned_dict = {state: {key.strip(): int(float(value.replace(',',''))) for key, value in data.items()} for state, data in dict_data.items()}

    final_dict = {'State': [], 'Age Group': [], gender: []}

    #Clean up age_group labels
    age_groups = ['0 - 4','5 - 9','10 - 14','15 - 19' ,'20 - 24','25 - 29','30 - 34', '35 - 39','40 - 44', '45 - 49','50 - 54','55 - 59','60 - 64','65 - 69','70 - 74','75 - 79', '80 - 84', '85 +']

    for state, data in cleaned_dict.items():
        gender_data = [data['Under 5 years'], data['5 to 9 years'], 
                data['10 to 14 years'],(data['15 to 17 years'] + data['18 and 19 years']),
                (data['20 years'] + data['21 years'] + data['22 to 24 years']), data['25 to 29 years'],
                data['30 to 34 years'],data['35 to 39 years'],
                data['40 to 44 years'], data['45 to 49 years'],
                data['50 to 54 years'], data['55 to 59 years'],
                (data['60 and 61 years'] + data['62 to 64 years']),(data['65 and 66 years'] + data['67 to 69 years']),
                data['70 to 74 years'],data['75 to 79 years'],
                data['80 to 84 years'],data['85 years and over']]
        
        for age_group, g in zip(age_groups, gender_data):
            final_dict['State'].append(state)
            final_dict['Age Group'].append(age_group)
            final_dict[gender].append(g)

    df = pd.DataFrame(final_dict)

    return df


def graph_pyramid(state: str, data_year: str):

    df_male = cleanup_dataframe(male_data,'Males')
    df_female = cleanup_dataframe(male_data,'Females')

    df = pd.merge(df_male, df_female)
    #Add State Code
    df['Code'] = df['State'].map(state_abbreviations)

    target_state = df.loc[df['State']==state]
    
    y = target_state['Age Group']
    x1 = target_state['Males']
    x2 = target_state['Females'] * -1
    state = target_state['State'].iloc[0]
    state_code = target_state['Code'].iloc[0]

    #Create instance for chart figure
    fig = go.Figure()

    #Add Trace to Figure
    fig.add_trace(go.Bar(
        y = y,
        x = x1,
        name = 'Males',
        orientation='h'
    ))

    #Add Trace to figure
    fig.add_trace(go.Bar(
        y = y,
        x = x2,
        name = 'Females',
        orientation='h'
    ))

    # Find the minimum and maximum values in x1 and x2
    min_val = min(min(x1), min(x2))
    max_val = max(max(x1), max(x2))

    # Create a range of values for the x-axis ticks
    tickvals = list(range(min_val, max_val, int((max_val - min_val) / 5)))

    def human_format(num):
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '%.1f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

    #Update the Title_suffix
    max_val = max(max(x1), max(x2))
    if abs(max_val) >= 10**6:
        title_suffix = 'in Millions'
    elif abs(max_val) >= 10**3:
        title_suffix = 'in Thousands'
    else:
        title_suffix = ''

    #Update Figure Layout
    fig.update_layout(
        template = 'plotly_white',
        title = f'Age Pyramid {state} {data_year}',
        title_font_size = 24,
        barmode = 'relative',
        bargap =0.0,
        bargroupgap =0,
        #height = 700,
        #width = 1400,
        xaxis= dict(
            tickvals=tickvals,
            ticktext=[human_format(abs(i)) for i in tickvals],
            title = 'Populations ' + title_suffix,
            title_font_size=14
        ),
        plot_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
        paper_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
        font=dict(
        color='#FFFFFF'  # change 'color_of_your_choice' to your desired color
        )
    )

    #Plot Figure
    pop_pyramid = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return pop_pyramid

"""Number of Housing Units by Cost - Accessing Mortgage data"""
def clean_mortgage_headers(val):
    if isinstance(val, str):
        if 'Percent' in val:
            val = val.split("!!")[0]
            val = val + " Percent"
        else:
            val = val.split("!!")[0]
        return val
    else:
        return val
    
#mort_obj = s3.get_object(Bucket=bucket_name, Key='data/Financial_Mortgate_Data_2022.csv')
#mortgage_data = pd.read_csv(StringIO(mort_obj['Body'].read().decode('utf-8')), index_col=0)
    
mortgage_data = pd.read_csv('./data/Financial_Mortgate_Data_2022.csv', index_col=0)
mortgage_data = mortgage_data.rename(columns=clean_mortgage_headers)

#mort_obj19 = s3.get_object(Bucket=bucket_name, Key='data/Financial_Mortgate_Data_2019.csv')
#mortgage_data19 = pd.read_csv(StringIO(mort_obj19['Body'].read().decode('utf-8')), index_col=0)

mortgage_data19 = pd.read_csv('./data/Financial_Mortgate_Data_2019.csv', index_col=0)
mortgage_data19 = mortgage_data19 .rename(columns=clean_mortgage_headers)

home_value = mortgage_data.iloc[[2,3,4,5,6,7,8,9]]
home_value19 = mortgage_data19.iloc[[2,3,4,5,6,7,8,9]]

def convert_value(value):
    try:
        if '%' in value:
            return float(value.replace('%', '')) / 100  # Convert percentage to a decimal
        else:
            return int(value.replace(',', ''))  # Remove commas and convert to integer
    except TypeError:
        return value  # If the value is already a float, return it as it is

def dataframe_sanitize(df):
    dict_mortgage = df.to_dict()
    cleaned_dict = {state: {key.strip(): convert_value(value) for key, value in data.items()} for state, data in dict_mortgage.items()}

    # Clean up dataframe columns
    final_list = []
    median_dict = {}  # Dictionary to store 'Median (dollars)' for each state
    for state, data in cleaned_dict.items():
        if 'Percent' not in state:
            state_percent = cleaned_dict.get(state + ' Percent', {})
            for value, unit in data.items():
                if value != 'Median (dollars)':
                    final_dict = {}
                    final_dict['State'] = state
                    final_dict['Value'] = value
                    final_dict['Units'] = unit
                    final_dict['unit_percent'] = state_percent.get(value)
                    final_list.append(final_dict)
                else:
                    median_dict[state] = unit  # Store 'Median (dollars)' in median_dict

    df = pd.DataFrame(final_list)
    df['Code'] = df['State'].map(state_abbreviations)

    # Create a separate DataFrame for 'Median'
    median_df = pd.DataFrame(list(median_dict.items()), columns=['State', 'Median'])
    median_df['Code'] = median_df['State'].map(state_abbreviations)

    return df, median_df


def graph_bar(state: str, data_year: str):

    df, df_median = dataframe_sanitize(home_value)
    target_state = df[df['State']==state]
    # Create the bar chart
    fig = px.bar(target_state, x='Value', y='Units', color='Value', title=f'{data_year} Number of Housing Units by Cost in {state}')
    fig.update_xaxes(title_text='Home Value')
    fig.update_yaxes(title_text='Number of Houses')
    fig.update_layout(
    plot_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    paper_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    font=dict(
        color='#FFFFFF'  # change 'color_of_your_choice' to your desired color
    )
    )
    home_value_graph = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return home_value_graph

def graph_bar_median_price(data_year: str):

    df = dataframe_sanitize(home_value)[1]
    df = df.sort_values('Median')
    # Create the bar chart
    fig = px.bar(df, x='State', y='Median', color='State', title=f'{data_year} Median Price of Homes in US')
    fig.update_xaxes(title_text='State')
    fig.update_yaxes(title_text='Median Price')
    fig.update_layout(
    plot_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    paper_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    font=dict(
        color='#FFFFFF'  # change 'color_of_your_choice' to your desired color
    )
    )
    home_median_graph = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return home_median_graph

"""Get Mortgage status by state"""
mortgage_status = mortgage_data.iloc[[12,13,14,15,16]]


def graph_pie(state:str,data_year: str):
    df, df_median = dataframe_sanitize(mortgage_status)
    target_state = df[df['State']==state]
    # Create the bar chart
    fig = px.pie(target_state, values='Units', names='Value', title=f'{data_year} Number of Houses by Mortgage Type in {state}')
    fig.update_layout(
    plot_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    paper_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    font=dict(
        color='#FFFFFF'  # change 'color_of_your_choice' to your desired color
    )
    )
    mort_stat = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return mort_stat

"""Household income status"""
household_income = mortgage_data.iloc[[18,19,20,21,22,23,24,25,26]]
household_income19 = mortgage_data19.iloc[[18,19,20,21,22,23,24,25,26]]

def dataframe_sanitize_income(df):
    
    dict_mortgage = df.to_dict()
    cleaned_dict = {state: {key.strip(): convert_value(value) for key, value in data.items()} for state, data in dict_mortgage.items()}

    #Clean up dataframe columns
    final_list = []
    median_dict = {}  # Dictionary to store 'Median household income (dollars)' for each state
    for state, data in cleaned_dict.items():
        if 'Percent' not in state:
            state_percent = cleaned_dict.get(state + ' Percent', {})
            for value, owners in data.items():
                if value != 'Median household income (dollars)':
                    final_dict = {}
                    final_dict['State'] = state
                    final_dict['Value'] = value
                    final_dict['Owners'] = owners
                    final_dict['Owner_percent'] = state_percent.get(value)
                    final_list.append(final_dict)
                else:
                    median_dict[state] = owners  # Store 'Median household income (dollars)' in median_dict
    
    df = pd.DataFrame(final_list)
    df['Code'] = df['State'].map(state_abbreviations)

    # Create a separate DataFrame for 'Median'
    median_df = pd.DataFrame(list(median_dict.items()), columns=['State', 'Median'])
    median_df['Code'] = median_df['State'].map(state_abbreviations)
    
    return df, median_df


def chart_income(state:str,data_year:str):

    df = dataframe_sanitize_income(household_income)[0]
    target_state = df[df['State']==state]
    fig = px.bar(target_state, x="Owners", y="Value", orientation='h', title=f'{data_year} Number of Homeowners with Household Income in {state}')
    fig.update_xaxes(title_text='Number of Homeowners')
    fig.update_yaxes(title_text='Household Income')
    fig.update_layout(
    plot_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    paper_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    font=dict(
        color='#FFFFFF'  # change 'color_of_your_choice' to your desired color
    )
    )
    num_house_income = fig.to_html(full_html=False, include_plotlyjs='cdn')

    fig = px.pie(target_state, values='Owners', names='Value', title=f'{data_year} Percent of Homeowners by Household Income in {state}')
    fig.update_layout(
    plot_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    paper_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    font=dict(
        color='#FFFFFF'  # change 'color_of_your_choice' to your desired color
    )
    )
    house_income = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return num_house_income, house_income

def chart_income_median(data_year:str):
    df = dataframe_sanitize_income(household_income)[1]
    df_sorted = df.sort_values('Median')
    fig = px.bar(df_sorted, x="State", y="Median", color='State', title=f'{data_year} Median Household Income by Homeowners in US')
    fig.update_xaxes(title_text='State')
    fig.update_yaxes(title_text='Median Household Income')
    fig.update_layout(
    plot_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    paper_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    font=dict(
        color='#FFFFFF'  # change 'color_of_your_choice' to your desired color
    )
    )
    median_income = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return median_income

"""Mortgage payment data"""
monthly_mortgage = mortgage_data.iloc[[34,35,36,37,38,39,40,41,42,43,44]]

def graph_bar_pmt(state: str, data_year: str):
    df  = dataframe_sanitize(monthly_mortgage)[0]
    target_state = df[df['State']==state]
    # Create the bar chart
    fig = px.bar(target_state, x='Value', y='Units', color='Value', title=f'{data_year} Number of Homes by Monthly Mortgage Payments in {state}')
    fig.update_xaxes(title_text='Monthly Mortgage')
    fig.update_yaxes(title_text='Number of Houses')
    fig.update_layout(
    plot_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    paper_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    font=dict(
        color='#FFFFFF'  # change 'color_of_your_choice' to your desired color
    )
    )
    mtg_pmt = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return mtg_pmt

def graph_bar_pmt_median(data_year: str):
    df  = dataframe_sanitize(monthly_mortgage)[1]
    df = df.sort_values('Median')
    # Create the bar chart
    fig = px.bar(df, x='State', y='Median', color='State', title=f'{data_year} Median Monthly Mortgage Payments in US')
    fig.update_xaxes(title_text='State')
    fig.update_yaxes(title_text='Median Monthly Payment')
    fig.update_layout(
    plot_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    paper_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    font=dict(
        color='#FFFFFF'  # change 'color_of_your_choice' to your desired color
    )
    )
    median_mtg_pmt = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return median_mtg_pmt

"""Real Estate Taxes"""
real_estate_tax = mortgage_data.iloc[[68,69,70,71,72]]

def dataframe_sanitize_re(df):
    
    dict_mortgage = df.to_dict()
    cleaned_dict = {state: {key.strip(): convert_value(value) for key, value in data.items()} for state, data in dict_mortgage.items()}

    #Clean up dataframe columns
    final_list = []
    median_dict = {}  # Dictionary to store 'Median (dollars)' for each state
    for state, data in cleaned_dict.items():
        if 'Percent' not in state:
            state_percent = cleaned_dict.get(state + ' Percent', {})
            for value, unit in data.items():
                if value != 'Median (dollars)':
                    final_dict = {}
                    final_dict['State'] = state
                    final_dict['Tax'] = value
                    final_dict['Units'] = unit
                    final_dict['unit_percent'] = state_percent.get(value)
                    final_list.append(final_dict)
                else:
                    median_dict[state] = unit  # Store 'Median (dollars)' in median_dict
    
    df = pd.DataFrame(final_list)
    df['Code'] = df['State'].map(state_abbreviations)

    # Create a separate DataFrame for 'Median'
    median_df = pd.DataFrame(list(median_dict.items()), columns=['State', 'Median'])
    median_df['Code'] = median_df['State'].map(state_abbreviations)

    return df, median_df

def graph_pie_tax(state:str,data_year: str):
    df = dataframe_sanitize_re(real_estate_tax)[0]
    target_state = df[df['State']==state]
    # Create the bar chart
    fig = px.pie(target_state, values='Units', names='Tax', title=f'{data_year} Real Estate Taxes Paid by Household in {state}')
    fig.update_layout(
    plot_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    paper_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    font=dict(
        color='#FFFFFF'  # change 'color_of_your_choice' to your desired color
    )
    )
    tax = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return tax

"""Housing units"""
housing_units = mortgage_data.iloc[0]

def clean_units_df(df):
    dict_units = df.to_dict()
    final_list = []
    for state, data in dict_units.items():
        if 'Percent' not in state:
            final_dict = {}
            final_dict['State'] = state
            final_dict['Units'] = convert_value(data)
            final_list.append(final_dict)
    df = pd.DataFrame(final_list)
    df['Code'] = df['State'].map(state_abbreviations)
    
    return df

def chart_units(data_year:str):
    df = clean_units_df(housing_units)
    fig = px.bar(df, x="State", y="Units", title=f'{data_year} Number of Housing Units With A Mortgage')
    fig.update_xaxes(title_text='State')
    fig.update_yaxes(title_text='Number of Housing Units')
    fig.update_layout(
    plot_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    paper_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    font=dict(
        color='#FFFFFF'  # change 'color_of_your_choice' to your desired color
    )
    )
    html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return html

"""Calculate home affordability"""

def chart_home_aff(data_year: str):

    median_home_value = dataframe_sanitize(home_value)[1]
    median_home_value.rename(columns={'Median': 'Median_House_Price'}, inplace=True)

    median_hh_income = dataframe_sanitize_income(household_income)[1]
    median_hh_income.rename(columns={'Median': 'Median_Income'}, inplace=True)

    house_aff = pd.merge(median_home_value, median_hh_income, on='State')
    house_aff['Ratio'] = house_aff['Median_House_Price']/house_aff['Median_Income']

    house_aff = house_aff.sort_values('Ratio')
    house_aff['Code'] = house_aff['State'].map(state_abbreviations)

    fig = px.bar(house_aff, x="State", y="Ratio", color='State', title=f'{data_year} Home Affordability by State')
    fig.update_xaxes(title_text='State')
    fig.update_yaxes(title_text='Affordability Ratio')
    fig.update_layout(
    plot_bgcolor='#1c1d26', 
    paper_bgcolor='#1c1d26', 
    font=dict(
        color='#FFFFFF'  
    )
    )
    html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    #Make map
    data = dict(type = 'choropleth',
            colorscale = 'Portland',
            locations = house_aff['Code'],
            locationmode = 'USA-states',
            z=house_aff['Ratio'],
            colorbar = {'title':'Affordability Ratio'})

    layout = dict(
        title = {'text': f'{data_year} House Affordability by State', 'x':0.5, 'xanchor': 'center'},
        geo = dict(scope = 'usa'),
    )

    choromap = go.Figure(data = [data],layout = layout)
    choromap.update_layout(
    plot_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    paper_bgcolor='#1c1d26',  # change 'color_of_your_choice' to your desired color
    font=dict(
        color='#FFFFFF'  # change 'color_of_your_choice' to your desired color
    )
    )
    map_html = choromap.to_html(full_html=False, include_plotlyjs='cdn')

    return html, map_html

def chart_home_aff_19(data_year: str):

    median_home_value = dataframe_sanitize(home_value19)[1]
    median_home_value.rename(columns={'Median': 'Median_House_Price'}, inplace=True)

    median_hh_income = dataframe_sanitize_income(household_income19)[1]
    median_hh_income.rename(columns={'Median': 'Median_Income'}, inplace=True)

    house_aff = pd.merge(median_home_value, median_hh_income, on='State')
    house_aff['Ratio'] = house_aff['Median_House_Price']/house_aff['Median_Income']

    house_aff = house_aff.sort_values('Ratio')
    house_aff['Code'] = house_aff['State'].map(state_abbreviations)

    #Make map
    data = dict(type = 'choropleth',
            colorscale = 'Portland',
            locations = house_aff['Code'],
            locationmode = 'USA-states',
            z=house_aff['Ratio'],
            colorbar = {'title':'Affordability Ratio'})

    layout = dict(
        title = {'text': f'{data_year} House Affordability by State', 'x':0.5, 'xanchor': 'center'},
        geo = dict(scope = 'usa'),
    )

    choromap = go.Figure(data = [data],layout = layout)
    # Update the background color and text color
    choromap.update_layout(
        plot_bgcolor='#1c1d26',
        paper_bgcolor='#1c1d26', 
        font=dict(
            color='#FFFFFF'
        )
    )
    html = choromap.to_html(full_html=False, include_plotlyjs='cdn')

    return html

"""Calculate tax burden by state"""

def chart_tax_burden(data_year:str):
    tax_median = dataframe_sanitize_re(real_estate_tax)[1]
    tax_median.rename(columns={'Median': 'Median_Tax'}, inplace=True)
    median_hh_income = dataframe_sanitize_income(household_income)[1]
    median_hh_income.rename(columns={'Median': 'Median_Income'}, inplace=True)
    tax_burden = pd.merge(tax_median,median_hh_income,on='State')
    tax_burden['Ratio'] = tax_burden['Median_Tax']/tax_burden['Median_Income']
    tax_burden = tax_burden.sort_values('Ratio')
    tax_burden['Code'] = tax_burden['State'].map(state_abbreviations)

    fig = px.bar(tax_burden, x="State", y="Ratio", color='State', title=f'{data_year} Real Estate Tax Burden by State')
    fig.update_xaxes(title_text='State')
    fig.update_yaxes(title_text='Tax Burden Ratio')
    fig.update_layout(
    plot_bgcolor='#1c1d26',
    paper_bgcolor='#1c1d26',
    font=dict(
        color='#FFFFFF'
    )
    )
    html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return html