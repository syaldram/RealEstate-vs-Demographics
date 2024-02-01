from flask import Flask, render_template, request
from jinja2 import Environment, FileSystemLoader
from graph_generator import graph_pyramid, graph_bar, graph_pie, chart_income, graph_bar_median_price, chart_income_median, graph_bar_pmt, graph_bar_pmt_median, graph_pie_tax, chart_units, chart_home_aff, chart_tax_burden, chart_home_aff_19
from graphs import make_map, home_pie, bedroom_size, chart_births, chart_state_births

app = Flask(__name__)

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


jinja2_env = Environment(loader=FileSystemLoader('./templates'), autoescape=True)
template = jinja2_env.get_template("index.html")

@app.route("/")
def home():
    state = "California"
    return template.render(
        pop_pyramid=graph_pyramid(state, '2022'), 
        state_abbreviations=state_abbreviations, 
        state=state, 
        home_value=graph_bar(state,'2022'),
        home_median=graph_bar_median_price('2022'), 
        mort_stat=graph_pie(state,'2022'), 
        chart_income= chart_income(state, '2022')[0],
        percent_income = chart_income(state,'2022')[1],
        us_own_avg_hh_size = make_map('2022')[0], 
        us_rent_avg_hh_size = make_map('2022')[1],
        median_income = chart_income_median('2022'),
        median_mtg_pmt = graph_bar_pmt_median('2022'),
        mtg_pmt = graph_bar_pmt(state,'2022'),
        tax = graph_pie_tax(state,'2022'),
        chart_units = chart_units('2022'),
        home_aff = chart_home_aff('2022')[0],
        home_aff19 = chart_home_aff_19('2019'),
        map_home_aff = chart_home_aff('2022')[1],
        tax_burden = chart_tax_burden('2022'),
        home_pie = home_pie(state, '2022'),
        bedroom_size = bedroom_size(state,'2022'),
        total_births = chart_births(),
        state_births = chart_state_births(state))

@app.route("/state")
def state():
    state_abbr = request.args.get('state')
    # Get the full state name from the abbreviation
    state = next((key for key, value in state_abbreviations.items() if value == state_abbr), None)
    if state is None:
        return "Invalid state abbreviation"
    return template.render(
        pop_pyramid=graph_pyramid(state, '2022'), 
        state_abbreviations=state_abbreviations, 
        state=state, 
        home_value=graph_bar(state,'2022'),
        home_median=graph_bar_median_price('2022'), 
        mort_stat=graph_pie(state,'2022'), 
        scrollToAnchor='charts_tag', 
        chart_income= chart_income(state, '2022')[0],
        percent_income = chart_income(state,'2022')[1],
        us_own_avg_hh_size = make_map('2022')[0], 
        us_rent_avg_hh_size = make_map('2022')[1],
        median_income = chart_income_median('2022'),
        median_mtg_pmt = graph_bar_pmt_median('2022'),
        mtg_pmt = graph_bar_pmt(state,'2022'),
        tax = graph_pie_tax(state,'2022'),
        chart_units = chart_units('2022'),
        home_aff = chart_home_aff('2022')[0],
        home_aff19 = chart_home_aff_19('2019'),
        map_home_aff = chart_home_aff('2022')[1],
        tax_burden = chart_tax_burden('2022'),
        home_pie = home_pie(state, '2022'),
        bedroom_size = bedroom_size(state,'2022'),
        total_births = chart_births(),
        state_births = chart_state_births(state))

if __name__ == "__main__":
    app.run()