import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

from constants import STATE_ABBREVIATIONS, DARK_THEME, PLOTLY_HTML_OPTS, CHART_COLORS

# ---------------------------------------------------------------------------
# Household size data
# ---------------------------------------------------------------------------

data_2022 = pd.read_csv('./data/AverageHouseHoldSize2022.csv', index_col=0)
data_2022 = data_2022.transpose().dropna(axis=1)

data_2012 = pd.read_csv('./data/AverageHouseHoldSize2012.csv', index_col=0)
data_2012 = data_2012.transpose().dropna(axis=1)

_YEAR_TO_HH_DATA = {
    '2022': data_2022,
    '2012': data_2012,
}


def _dataframe_cleanup(df):
    dict_data = df.to_dict()
    new_dict = {'State': [], 'Owner_occupied': [], 'Renter_occupied': []}
    for k, v in dict_data.items():
        if k == 'Owner occupied':
            new_dict['State'].extend(list(v.keys()))
            new_dict['Owner_occupied'].extend(v.values())
        if k == 'Renter occupied':
            new_dict['Renter_occupied'].extend(v.values())

    df_out = pd.DataFrame(new_dict, columns=['State', 'Owner_occupied', 'Renter_occupied'])
    df_out['Code'] = df_out['State'].map(STATE_ABBREVIATIONS)
    return df_out


def make_map(data_year: str):
    raw = _YEAR_TO_HH_DATA.get(data_year, data_2022)
    df = _dataframe_cleanup(raw)

    def _choropleth(z_col, title_text):
        data = dict(
            type='choropleth',
            colorscale=[[0, '#2ec4b6'], [0.5, '#f4a261'], [1, '#e44c65']],
            locations=df['Code'],
            locationmode='USA-states',
            z=df[z_col],
            colorbar={'title': 'Average Number of People'},
        )
        layout = dict(
            title={'text': f'{data_year} {title_text}', 'x': 0.5, 'xanchor': 'center'},
            geo=dict(scope='usa'),
        )
        fig = go.Figure(data=[data], layout=layout)
        fig.update_layout(**DARK_THEME)
        return fig.to_html(**PLOTLY_HTML_OPTS)

    own_html = _choropleth('Owner_occupied', 'US Average Household Size by Home Owner')
    rent_html = _choropleth('Renter_occupied', 'US Average Household Size by Renter')
    return own_html, rent_html


# ---------------------------------------------------------------------------
# Physical housing occupancy data
# ---------------------------------------------------------------------------

def _clean_house_char_headers(val):
    if not isinstance(val, str):
        return val
    prefix = val.split("!!")[0]
    if 'Percent owner-occupied housing units' in val:
        return prefix + "_own_percent"
    if 'Percent renter-occupied' in val:
        return prefix + "_rent_percent"
    if 'Percent occupied housing units' in val:
        return prefix + "_total_percent"
    if 'Owner-occupied housing' in val:
        return prefix + "_owner"
    if 'Renter-occupied housing units' in val:
        return prefix + "_renter"
    if 'Occupied' in val:
        return prefix + "_total"
    return prefix


def _convert_value(value):
    if '%' in value:
        return float(value.replace('%', '')) / 100
    return int(value.replace(',', ''))


def _housing_data_cleanup(df):
    df_dict = df.to_dict()
    cleaned_dict = {
        state: {key.strip(): _convert_value(value) for key, value in data.items()}
        for state, data in df_dict.items()
    }

    nested = {}
    for state_attr, attr_values in cleaned_dict.items():
        if "_" not in state_attr:
            continue
        state, attribute = state_attr.split("_", 1)
        nested.setdefault(state, {}).setdefault(attribute, {}).update(attr_values)

    def _to_df(lst):
        df_out = pd.concat(
            {k: pd.DataFrame.from_dict(v, 'index') for d in lst for k, v in d.items()},
            axis=0,
        )
        df_out.reset_index(inplace=True)
        df_out.columns = ['State', 'Value', 'Count']
        df_out['Code'] = df_out['State'].map(STATE_ABBREVIATIONS)
        return df_out

    total_lst = [{k: v['total']} for k, v in nested.items() if 'total' in v]
    owner_lst = [{k: v['owner']} for k, v in nested.items() if 'owner' in v]
    renter_lst = [{k: v['renter']} for k, v in nested.items() if 'renter' in v]

    return _to_df(total_lst), _to_df(owner_lst), _to_df(renter_lst)


house_char_data = pd.read_csv('./data/Physical_Housing_Occup.csv', index_col=0)
house_char_data = house_char_data.rename(columns=_clean_house_char_headers)

units_in_struc = house_char_data.iloc[[2, 3, 4, 5, 6, 7, 8]]
bedroom = house_char_data.iloc[[24, 25, 26, 27]]

# Precompute housing occupancy dataframes
_units_df_total, _units_df_owner, _units_df_renter = _housing_data_cleanup(units_in_struc)
_bed_df_total, _bed_df_owner, _bed_df_renter = _housing_data_cleanup(bedroom)


def home_pie(state: str, data_year: str):
    target_state = _units_df_total[_units_df_total['State'] == state]
    fig = px.pie(target_state, values='Count', names='Value',
                 title=f'{data_year} Typical house type in {state}',
                 color_discrete_sequence=CHART_COLORS)
    fig.update_layout(**DARK_THEME)
    return fig.to_html(**PLOTLY_HTML_OPTS)


def bedroom_size(state: str, data_year: str):
    own = _bed_df_owner[_bed_df_owner['State'] == state].copy()
    rent = _bed_df_renter[_bed_df_renter['State'] == state].copy()
    own['Type'] = 'Homeowners'
    rent['Type'] = 'Renters'
    df = pd.concat([own, rent])

    fig = px.bar(
        df, x='Value', y='Count', color='Type', barmode='group',
        facet_row='State',
        labels={'Count': 'Number of Units', 'Value': 'Number of Bedrooms'},
        title=f'{data_year} Number of Bedrooms in Homes for Homeowners vs Renters',
        color_discrete_map={'Homeowners': '#3d5a80', 'Renters': '#e44c65'},
    )
    fig.update_layout(**DARK_THEME)
    return fig.to_html(**PLOTLY_HTML_OPTS)


# ---------------------------------------------------------------------------
# Fertility / birth rate data
# ---------------------------------------------------------------------------

def _clean_fert_headers(val):
    if not isinstance(val, str):
        return val
    prefix = val.split("!!")[0]
    if 'Total' in val:
        return prefix + "_total"
    if 'Women with births in the past 12 months!!Number!!Estimate' in val:
        return prefix + "_births"
    if 'Women with births in the past 12 months!!Rate per 1,000 women!!Estimate' in val:
        return prefix + "_thou"
    return prefix


fert_data = pd.read_excel('./data/fertility_data.xlsx', index_col=0)
fert_data = fert_data.rename(columns=_clean_fert_headers)

# Each survey year occupies 11 rows; row index 1 within each block is the relevant data row.
_FERT_YEAR_ROW = {
    '2022': 1, '2021': 12, '2019': 23, '2018': 34, '2017': 45,
    '2016': 56, '2015': 67, '2014': 78, '2013': 89, '2012': 100,
    '2011': 111, '2010': 122,
}
_FERT_YEARS_ORDER = [
    '2010', '2011', '2012', '2013', '2014', '2015',
    '2016', '2017', '2018', '2019', '2021', '2022',
]


def _fert_data_cleanup(df):
    df_dict = df.to_dict()
    cleaned_dict = {
        state: {key.strip(): value for key, value in data.items()}
        for state, data in df_dict.items()
    }

    nested = {}
    for state_attr, attr_values in cleaned_dict.items():
        if "_" not in state_attr:
            continue
        state, attribute = state_attr.split("_", 1)
        nested.setdefault(state, {}).setdefault(attribute, {}).update(attr_values)

    def _to_df(lst):
        df_out = pd.concat(
            {k: pd.DataFrame.from_dict(v, 'index') for d in lst for k, v in d.items()},
            axis=0,
        )
        df_out.reset_index(inplace=True)
        df_out.columns = ['State', 'Value', 'Count']
        df_out['Code'] = df_out['State'].map(STATE_ABBREVIATIONS)
        return df_out

    total_lst = [{k: v['total']} for k, v in nested.items() if 'total' in v]
    birth_lst = [{k: v['births']} for k, v in nested.items() if 'births' in v]
    thou_lst = [{k: v['thou']} for k, v in nested.items() if 'thou' in v]

    return _to_df(total_lst), _to_df(birth_lst), _to_df(thou_lst)


def _build_all_births_df():
    frames = []
    for year in _FERT_YEARS_ORDER:
        row_idx = _FERT_YEAR_ROW[year]
        _, birth_df, _ = _fert_data_cleanup(fert_data.iloc[[row_idx]])
        birth_df['Year'] = year
        frames.append(birth_df)
    return pd.concat(frames).reset_index(drop=True)


# Precompute once at startup
_all_births_df = _build_all_births_df()


def chart_births():
    df_sum = _all_births_df.groupby('Year')['Count'].sum().reset_index()
    df_sum['Year'] = pd.Categorical(df_sum['Year'], categories=_FERT_YEARS_ORDER, ordered=True)
    df_sum = df_sum.sort_values('Year')
    fig = px.line(df_sum, x='Year', y='Count',
                  title='Total Births by year in United States')
    fig.update_layout(**DARK_THEME)
    fig.update_traces(line=dict(color='#e44c65', width=6))
    return fig.to_html(**PLOTLY_HTML_OPTS)


def chart_state_births(state: str):
    target_state = _all_births_df[_all_births_df['State'] == state].copy()
    target_state['Year'] = pd.Categorical(target_state['Year'], categories=_FERT_YEARS_ORDER, ordered=True)
    target_state = target_state.sort_values('Year')
    fig = px.line(target_state, x='Year', y='Count',
                  title=f'Total Births by year in {state}')
    fig.update_layout(**DARK_THEME)
    fig.update_traces(line=dict(color='#e44c65', width=6))
    return fig.to_html(**PLOTLY_HTML_OPTS)
