import pandas as pd
import plotly.express as px
import plotly.graph_objs as go 

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
    
data_pop = pd.read_csv('../Data/SexByAge2022.csv', index_col=0)
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
        height = 700,
        width = 1400,
        xaxis= dict(
            tickvals=tickvals,
            ticktext=[human_format(abs(i)) for i in tickvals],
            title = 'Populations ' + title_suffix,
            title_font_size=14
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
    
mortgage_data = pd.read_csv('../Data/Financial_Mortgate_Data_2022.csv', index_col=0)
mortgage_data = mortgage_data.rename(columns=clean_mortgage_headers)

home_value = mortgage_data.iloc[[2,3,4,5,6,7,8,9]]

def convert_value(value):
    if '%' in value:
        return float(value.replace('%', '')) / 100  # Convert percentage to a decimal
    else:
        return int(value.replace(',', ''))  # Remove commas and convert to integer

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
    home_value_graph = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return home_value_graph

"""Get Mortgage status by state"""
mortgage_status = mortgage_data.iloc[[12,13,14,15,16]]


def graph_pie(state:str,data_year: str):
    df, df_median = dataframe_sanitize(mortgage_status)
    target_state = df[df['State']==state]
    # Create the bar chart
    fig = px.pie(target_state, values='Units', names='Value', title=f'{data_year} Number of Houses by Mortgage Type in {state}')
    mort_stat = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return mort_stat