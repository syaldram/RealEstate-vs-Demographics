import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

from constants import STATE_ABBREVIATIONS, DARK_THEME, PLOTLY_HTML_OPTS, CHART_COLORS, convert_value

def _clean_mortgage_headers(val):
    if isinstance(val, str):
        prefix = val.split("!!")[0]
        return prefix + " Percent" if 'Percent' in val else prefix
    return val


data_pop = pd.read_csv('./data/SexByAge2022.csv', index_col=0)
data_pop = data_pop.rename(columns=lambda val: val.split("!!")[0] if isinstance(val, str) else val)

male_data = data_pop.iloc[[2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]]
female_data = data_pop.iloc[[26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48]]

mortgage_data = pd.read_csv('./data/Financial_Mortgate_Data_2022.csv', index_col=0)
mortgage_data = mortgage_data.rename(columns=_clean_mortgage_headers)

mortgage_data19 = pd.read_csv('./data/Financial_Mortgate_Data_2019.csv', index_col=0)
mortgage_data19 = mortgage_data19.rename(columns=_clean_mortgage_headers)


def cleanup_dataframe(df, gender: str):
    dict_data = df.to_dict()
    cleaned_dict = {
        state: {key.strip(): int(float(value.replace(',', ''))) for key, value in data.items()}
        for state, data in dict_data.items()
    }

    age_groups = [
        '0 - 4', '5 - 9', '10 - 14', '15 - 19', '20 - 24', '25 - 29',
        '30 - 34', '35 - 39', '40 - 44', '45 - 49', '50 - 54', '55 - 59',
        '60 - 64', '65 - 69', '70 - 74', '75 - 79', '80 - 84', '85 +',
    ]

    final_dict = {'State': [], 'Age Group': [], gender: []}
    for state, data in cleaned_dict.items():
        gender_data = [
            data['Under 5 years'],
            data['5 to 9 years'],
            data['10 to 14 years'],
            data['15 to 17 years'] + data['18 and 19 years'],
            data['20 years'] + data['21 years'] + data['22 to 24 years'],
            data['25 to 29 years'],
            data['30 to 34 years'],
            data['35 to 39 years'],
            data['40 to 44 years'],
            data['45 to 49 years'],
            data['50 to 54 years'],
            data['55 to 59 years'],
            data['60 and 61 years'] + data['62 to 64 years'],
            data['65 and 66 years'] + data['67 to 69 years'],
            data['70 to 74 years'],
            data['75 to 79 years'],
            data['80 to 84 years'],
            data['85 years and over'],
        ]
        for age_group, g in zip(age_groups, gender_data):
            final_dict['State'].append(state)
            final_dict['Age Group'].append(age_group)
            final_dict[gender].append(g)

    return pd.DataFrame(final_dict)


# Precompute merged population pyramid dataframe once
_df_male = cleanup_dataframe(male_data, 'Males')
_df_female = cleanup_dataframe(female_data, 'Females')
_pyramid_df = pd.merge(_df_male, _df_female)
_pyramid_df['Code'] = _pyramid_df['State'].map(STATE_ABBREVIATIONS)


def graph_pyramid(state: str, data_year: str):
    target_state = _pyramid_df.loc[_pyramid_df['State'] == state]

    y = target_state['Age Group']
    x1 = target_state['Males']
    x2 = target_state['Females'] * -1
    state_name = target_state['State'].iloc[0]

    def human_format(num):
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '%.1f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

    max_val = max(max(x1), max(x2))
    min_val = min(min(x1), min(x2))
    tickvals = list(range(min_val, max_val, int((max_val - min_val) / 5)))

    if abs(max_val) >= 10**6:
        title_suffix = 'in Millions'
    elif abs(max_val) >= 10**3:
        title_suffix = 'in Thousands'
    else:
        title_suffix = ''

    fig = go.Figure()
    fig.add_trace(go.Bar(y=y, x=x1, name='Males', orientation='h', marker_color='#3d5a80'))
    fig.add_trace(go.Bar(y=y, x=x2, name='Females', orientation='h', marker_color='#e44c65'))

    fig.update_layout(
        **DARK_THEME,
        template='plotly_white',
        title=f'Age Pyramid {state_name} {data_year}',
        title_font_size=24,
        barmode='relative',
        bargap=0.0,
        bargroupgap=0,
        xaxis=dict(
            tickvals=tickvals,
            ticktext=[human_format(abs(i)) for i in tickvals],
            title='Populations ' + title_suffix,
            title_font_size=14,
        ),
    )

    return fig.to_html(**PLOTLY_HTML_OPTS)


def dataframe_sanitize(df):
    dict_mortgage = df.to_dict()
    cleaned_dict = {
        state: {key.strip(): convert_value(value) for key, value in data.items()}
        for state, data in dict_mortgage.items()
    }

    final_list = []
    median_dict = {}
    for state, data in cleaned_dict.items():
        if 'Percent' not in state:
            state_percent = cleaned_dict.get(state + ' Percent', {})
            for value, unit in data.items():
                if value != 'Median (dollars)':
                    final_list.append({
                        'State': state,
                        'Value': value,
                        'Units': unit,
                        'unit_percent': state_percent.get(value),
                    })
                else:
                    median_dict[state] = unit

    df_out = pd.DataFrame(final_list)
    df_out['Code'] = df_out['State'].map(STATE_ABBREVIATIONS)

    median_df = pd.DataFrame(list(median_dict.items()), columns=['State', 'Median'])
    median_df['Code'] = median_df['State'].map(STATE_ABBREVIATIONS)

    return df_out, median_df


def dataframe_sanitize_income(df):
    dict_mortgage = df.to_dict()
    cleaned_dict = {
        state: {key.strip(): convert_value(value) for key, value in data.items()}
        for state, data in dict_mortgage.items()
    }

    final_list = []
    median_dict = {}
    for state, data in cleaned_dict.items():
        if 'Percent' not in state:
            state_percent = cleaned_dict.get(state + ' Percent', {})
            for value, owners in data.items():
                if value != 'Median household income (dollars)':
                    final_list.append({
                        'State': state,
                        'Value': value,
                        'Owners': owners,
                        'Owner_percent': state_percent.get(value),
                    })
                else:
                    median_dict[state] = owners

    df_out = pd.DataFrame(final_list)
    df_out['Code'] = df_out['State'].map(STATE_ABBREVIATIONS)

    median_df = pd.DataFrame(list(median_dict.items()), columns=['State', 'Median'])
    median_df['Code'] = median_df['State'].map(STATE_ABBREVIATIONS)

    return df_out, median_df


def dataframe_sanitize_re(df):
    dict_mortgage = df.to_dict()
    cleaned_dict = {
        state: {key.strip(): convert_value(value) for key, value in data.items()}
        for state, data in dict_mortgage.items()
    }

    final_list = []
    median_dict = {}
    for state, data in cleaned_dict.items():
        if 'Percent' not in state:
            state_percent = cleaned_dict.get(state + ' Percent', {})
            for value, unit in data.items():
                if value != 'Median (dollars)':
                    final_list.append({
                        'State': state,
                        'Tax': value,
                        'Units': unit,
                        'unit_percent': state_percent.get(value),
                    })
                else:
                    median_dict[state] = unit

    df_out = pd.DataFrame(final_list)
    df_out['Code'] = df_out['State'].map(STATE_ABBREVIATIONS)

    median_df = pd.DataFrame(list(median_dict.items()), columns=['State', 'Median'])
    median_df['Code'] = median_df['State'].map(STATE_ABBREVIATIONS)

    return df_out, median_df


# Precomputed dataset slices
home_value = mortgage_data.iloc[[2,3,4,5,6,7,8,9]]
home_value19 = mortgage_data19.iloc[[2,3,4,5,6,7,8,9]]
mortgage_status = mortgage_data.iloc[[12,13,14,15,16]]
household_income = mortgage_data.iloc[[18,19,20,21,22,23,24,25,26]]
household_income19 = mortgage_data19.iloc[[18,19,20,21,22,23,24,25,26]]
monthly_mortgage = mortgage_data.iloc[[34,35,36,37,38,39,40,41,42,43,44]]
real_estate_tax = mortgage_data.iloc[[68,69,70,71,72]]
housing_units = mortgage_data.iloc[0]

# Cache sanitized dataframes that don't depend on state
_home_value_df, _home_value_median_df = dataframe_sanitize(home_value)
_home_value19_df, _home_value19_median_df = dataframe_sanitize(home_value19)
_mortgage_status_df, _ = dataframe_sanitize(mortgage_status)
_household_income_df, _household_income_median_df = dataframe_sanitize_income(household_income)
_household_income19_df, _household_income19_median_df = dataframe_sanitize_income(household_income19)
_monthly_mortgage_df, _monthly_mortgage_median_df = dataframe_sanitize(monthly_mortgage)
_real_estate_tax_df, _real_estate_tax_median_df = dataframe_sanitize_re(real_estate_tax)


def graph_bar(state: str, data_year: str):
    target_state = _home_value_df[_home_value_df['State'] == state]
    fig = px.bar(target_state, x='Value', y='Units', color='Value',
                 title=f'{data_year} Number of Housing Units by Cost in {state}',
                 color_discrete_sequence=CHART_COLORS)
    fig.update_xaxes(title_text='Home Value')
    fig.update_yaxes(title_text='Number of Houses')
    fig.update_layout(**DARK_THEME)
    return fig.to_html(**PLOTLY_HTML_OPTS)


def graph_bar_median_price(data_year: str):
    df = _home_value_median_df.sort_values('Median')
    fig = px.bar(df, x='State', y='Median', title=f'{data_year} Median Price of Homes in US')
    fig.update_xaxes(title_text='State')
    fig.update_yaxes(title_text='Median Price')
    fig.update_traces(marker_color='#2ec4b6')
    fig.update_layout(**DARK_THEME)
    return fig.to_html(**PLOTLY_HTML_OPTS)


def graph_pie(state: str, data_year: str):
    target_state = _mortgage_status_df[_mortgage_status_df['State'] == state]
    fig = px.pie(target_state, values='Units', names='Value',
                 title=f'{data_year} Number of Houses by Mortgage Type in {state}',
                 color_discrete_sequence=CHART_COLORS)
    fig.update_layout(**DARK_THEME)
    return fig.to_html(**PLOTLY_HTML_OPTS)


def chart_income(state: str, data_year: str):
    target_state = _household_income_df[_household_income_df['State'] == state]

    fig = px.bar(target_state, x='Owners', y='Value', orientation='h',
                 title=f'{data_year} Number of Homeowners with Household Income in {state}')
    fig.update_xaxes(title_text='Number of Homeowners')
    fig.update_yaxes(title_text='Household Income')
    fig.update_traces(marker_color='#3d5a80')
    fig.update_layout(**DARK_THEME)
    num_house_income = fig.to_html(**PLOTLY_HTML_OPTS)

    fig2 = px.pie(target_state, values='Owners', names='Value',
                  title=f'{data_year} Percent of Homeowners by Household Income in {state}',
                  color_discrete_sequence=CHART_COLORS)
    fig2.update_layout(**DARK_THEME)
    house_income = fig2.to_html(**PLOTLY_HTML_OPTS)

    return num_house_income, house_income


def chart_income_median(data_year: str):
    df_sorted = _household_income_median_df.sort_values('Median')
    fig = px.bar(df_sorted, x='State', y='Median',
                 title=f'{data_year} Median Household Income by Homeowners in US')
    fig.update_xaxes(title_text='State')
    fig.update_yaxes(title_text='Median Household Income')
    fig.update_traces(marker_color='#f4a261')
    fig.update_layout(**DARK_THEME)
    return fig.to_html(**PLOTLY_HTML_OPTS)


def graph_bar_pmt(state: str, data_year: str):
    target_state = _monthly_mortgage_df[_monthly_mortgage_df['State'] == state]
    fig = px.bar(target_state, x='Value', y='Units', color='Value',
                 title=f'{data_year} Number of Homes by Monthly Mortgage Payments in {state}',
                 color_discrete_sequence=CHART_COLORS)
    fig.update_xaxes(title_text='Monthly Mortgage')
    fig.update_yaxes(title_text='Number of Houses')
    fig.update_layout(**DARK_THEME)
    return fig.to_html(**PLOTLY_HTML_OPTS)


def graph_bar_pmt_median(data_year: str):
    df = _monthly_mortgage_median_df.sort_values('Median')
    fig = px.bar(df, x='State', y='Median',
                 title=f'{data_year} Median Monthly Mortgage Payments in US')
    fig.update_xaxes(title_text='State')
    fig.update_yaxes(title_text='Median Monthly Payment')
    fig.update_traces(marker_color='#e44c65')
    fig.update_layout(**DARK_THEME)
    return fig.to_html(**PLOTLY_HTML_OPTS)


def graph_pie_tax(state: str, data_year: str):
    target_state = _real_estate_tax_df[_real_estate_tax_df['State'] == state]
    fig = px.pie(target_state, values='Units', names='Tax',
                 title=f'{data_year} Real Estate Taxes Paid by Household in {state}',
                 color_discrete_sequence=CHART_COLORS)
    fig.update_layout(**DARK_THEME)
    return fig.to_html(**PLOTLY_HTML_OPTS)


def _clean_units_df(df):
    dict_units = df.to_dict()
    final_list = [
        {'State': state, 'Units': convert_value(data)}
        for state, data in dict_units.items()
        if 'Percent' not in state
    ]
    df_out = pd.DataFrame(final_list)
    df_out['Code'] = df_out['State'].map(STATE_ABBREVIATIONS)
    return df_out


def chart_units(data_year: str):
    df = _clean_units_df(housing_units)
    fig = px.bar(df, x='State', y='Units',
                 title=f'{data_year} Number of Housing Units With A Mortgage')
    fig.update_xaxes(title_text='State')
    fig.update_yaxes(title_text='Number of Housing Units')
    fig.update_traces(marker_color='#3d5a80')
    fig.update_layout(**DARK_THEME)
    return fig.to_html(**PLOTLY_HTML_OPTS)


def _build_home_aff_chart(median_home_df, median_income_df, data_year: str):
    median_home_df = median_home_df.rename(columns={'Median': 'Median_House_Price'})
    median_income_df = median_income_df.rename(columns={'Median': 'Median_Income'})

    house_aff = pd.merge(median_home_df, median_income_df, on='State')
    house_aff['Ratio'] = house_aff['Median_House_Price'] / house_aff['Median_Income']
    house_aff = house_aff.sort_values('Ratio')
    house_aff['Code'] = house_aff['State'].map(STATE_ABBREVIATIONS)
    return house_aff


def chart_home_aff(data_year: str):
    house_aff = _build_home_aff_chart(
        _home_value_median_df.copy(), _household_income_median_df.copy(), data_year
    )

    fig = px.bar(house_aff, x='State', y='Ratio',
                 title=f'{data_year} Home Affordability by State')
    fig.update_xaxes(title_text='State')
    fig.update_yaxes(title_text='Affordability Ratio')
    fig.update_traces(marker_color='#e44c65')
    fig.update_layout(**DARK_THEME)
    html = fig.to_html(**PLOTLY_HTML_OPTS)

    choropleth_data = dict(
        type='choropleth',
        colorscale=[[0, '#2ec4b6'], [0.5, '#f4a261'], [1, '#e44c65']],
        locations=house_aff['Code'],
        locationmode='USA-states',
        z=house_aff['Ratio'],
        colorbar={'title': 'Affordability Ratio'},
    )
    layout = dict(
        title={'text': f'{data_year} House Affordability by State', 'x': 0.5, 'xanchor': 'center'},
        geo=dict(scope='usa'),
    )
    choromap = go.Figure(data=[choropleth_data], layout=layout)
    choromap.update_layout(**DARK_THEME)
    map_html = choromap.to_html(**PLOTLY_HTML_OPTS)

    return html, map_html


def chart_home_aff_19(data_year: str):
    house_aff = _build_home_aff_chart(
        _home_value19_median_df.copy(), _household_income19_median_df.copy(), data_year
    )

    choropleth_data = dict(
        type='choropleth',
        colorscale=[[0, '#2ec4b6'], [0.5, '#f4a261'], [1, '#e44c65']],
        locations=house_aff['Code'],
        locationmode='USA-states',
        z=house_aff['Ratio'],
        colorbar={'title': 'Affordability Ratio'},
    )
    layout = dict(
        title={'text': f'{data_year} House Affordability by State', 'x': 0.5, 'xanchor': 'center'},
        geo=dict(scope='usa'),
    )
    choromap = go.Figure(data=[choropleth_data], layout=layout)
    choromap.update_layout(**DARK_THEME)
    return choromap.to_html(**PLOTLY_HTML_OPTS)


def chart_tax_burden(data_year: str):
    tax_median = _real_estate_tax_median_df.rename(columns={'Median': 'Median_Tax'})
    income_median = _household_income_median_df.rename(columns={'Median': 'Median_Income'})

    tax_burden = pd.merge(tax_median, income_median, on='State')
    tax_burden['Ratio'] = tax_burden['Median_Tax'] / tax_burden['Median_Income']
    tax_burden = tax_burden.sort_values('Ratio')
    tax_burden['Code'] = tax_burden['State'].map(STATE_ABBREVIATIONS)

    fig = px.bar(tax_burden, x='State', y='Ratio',
                 title=f'{data_year} Real Estate Tax Burden by State')
    fig.update_xaxes(title_text='State')
    fig.update_yaxes(title_text='Tax Burden Ratio')
    fig.update_traces(marker_color='#6c63ff')
    fig.update_layout(**DARK_THEME)
    return fig.to_html(**PLOTLY_HTML_OPTS)
