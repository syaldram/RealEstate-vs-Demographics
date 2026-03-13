STATE_ABBREVIATIONS = {
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
    'Puerto Rico': 'PR',
}

DARK_THEME = dict(
    plot_bgcolor='#1c1d26',
    paper_bgcolor='#1c1d26',
    font=dict(color='#FFFFFF'),
)

CHART_COLORS = [
    '#e44c65',  # warm red (primary accent)
    '#2ec4b6',  # teal
    '#3d5a80',  # navy
    '#f4a261',  # warm gold
    '#6c63ff',  # soft purple
    '#43aa8b',  # sage green
    '#e76f51',  # burnt orange
    '#84a9c0',  # steel blue
    '#d4a373',  # tan
    '#577590',  # slate
    '#f28482',  # light coral
    '#90be6d',  # olive green
]

DEFAULT_YEAR = '2022'

PLOTLY_HTML_OPTS = dict(
    full_html=False,
    include_plotlyjs='cdn',
    config={'responsive': True},
)


def convert_value(value):
    try:
        if '%' in value:
            return float(value.replace('%', '')) / 100
        else:
            return int(value.replace(',', ''))
    except TypeError:
        return value
