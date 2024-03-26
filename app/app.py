from flask import Flask, render_template, request
import logging
from graph_generator import graph_pyramid, graph_bar, graph_pie, chart_income, graph_bar_median_price, chart_income_median, graph_bar_pmt, graph_bar_pmt_median, graph_pie_tax, chart_units, chart_home_aff, chart_tax_burden, chart_home_aff_19
from graphs import make_map, home_pie, bedroom_size, chart_births, chart_state_births
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

foot_year = datetime.now().year

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
'Wyoming': 'WY'
}

predictions = [
    {'Alabama': 211079.27}, {'Alaska': 339052.03}, {'Arizona': 306941.34}, {'Arkansas': 194682.4}, {'California': 477853.56}, {'Colorado': 392629.2}, {'Connecticut': 353654.62}, {'Delaware': 292033.72}, {'District of Columbia': 536802.25}, {'Florida': 267907.0}, {'Georgia': 270794.62}, {'Hawaii': 558202.3}, {'Idaho': 306502.75}, {'Illinois': 261655.5}, {'Indiana': 204480.97}, {'Iowa': 213915.58}, {'Kansas': 240106.77}, {'Kentucky': 206727.23}, {'Louisiana': 229143.12}, {'Maine': 253239.69}, {'Maryland': 365915.56}, {'Massachusetts': 438043.97}, {'Michigan': 217066.14}, {'Minnesota': 295210.78}, {'Mississippi': 190834.75}, {'Missouri': 216126.39}, {'Montana': 288817.44}, {'Nebraska': 251140.03}, {'Nevada': 327448.84}, {'New Hampshire': 362251.78}, {'New Jersey': 416136.8}, {'New Mexico': 231550.6}, {'New York': 359355.4}, {'North Carolina': 240967.6}, {'North Dakota': 259075.05}, {'Ohio': 204287.16}, {'Oklahoma': 217383.16}, {'Oregon': 354209.8}, {'Pennsylvania': 240789.97}, {'Rhode Island': 340761.12}, {'South Carolina': 231672.92}, {'South Dakota': 250030.98}, {'Tennessee': 245226.92}, {'Texas': 269651.03}, {'Utah': 383908.1}, {'Vermont': 276144.6}, {'Virginia': 330968.97}, {'Washington': 422838.25}, {'West Virginia': 182807.48}, {'Wisconsin': 240014.98}, {'Wyoming': 263141.5}]

@app.route("/")
def home():
    state = "California"
    year = '2022'
    chart_income_data = chart_income(state, year)
    make_map_data = make_map(year)
    chart_home_aff_data = chart_home_aff(year)

    for states in predictions:
        if state in states:
            value = states[state]

    
    return render_template("index.html",
        footer_year = foot_year,
        value = value,
        pop_pyramid=graph_pyramid(state, year), 
        state_abbreviations=state_abbreviations, 
        state=state, 
        home_value=graph_bar(state, year),
        home_median=graph_bar_median_price(year), 
        mort_stat=graph_pie(state, year), 
        chart_income= chart_income_data[0],
        percent_income = chart_income_data[1],
        us_own_avg_hh_size = make_map_data[0], 
        us_rent_avg_hh_size = make_map_data[1],
        median_income = chart_income_median(year),
        median_mtg_pmt = graph_bar_pmt_median(year),
        mtg_pmt = graph_bar_pmt(state, year),
        tax = graph_pie_tax(state, year),
        chart_units = chart_units(year),
        home_aff = chart_home_aff_data[0],
        home_aff19 = chart_home_aff_19('2019'),
        map_home_aff = chart_home_aff_data[1],
        tax_burden = chart_tax_burden(year),
        home_pie = home_pie(state, year),
        bedroom_size = bedroom_size(state, year),
        total_births = chart_births(),
        state_births = chart_state_births(state))

@app.route("/state")
def state():
    state_abbr = request.args.get('state')
    state = next((key for key, value in state_abbreviations.items() if value == state_abbr), None)
    if state is None:
        return "Invalid state abbreviation"
    
    for data in predictions:
        if state in data:
            value = data[state]
    
    year = '2022'
    chart_income_data = chart_income(state, year)
    make_map_data = make_map(year)
    chart_home_aff_data = chart_home_aff(year)
    
    return render_template("index.html",
        footer_year = foot_year,
        value = value,
        pop_pyramid=graph_pyramid(state, year), 
        state_abbreviations=state_abbreviations, 
        state=state, 
        home_value=graph_bar(state, year),
        home_median=graph_bar_median_price(year), 
        mort_stat=graph_pie(state, year), 
        scrollToAnchor='charts_tag', 
        chart_income= chart_income_data[0],
        percent_income = chart_income_data[1],
        us_own_avg_hh_size = make_map_data[0], 
        us_rent_avg_hh_size = make_map_data[1],
        median_income = chart_income_median(year),
        median_mtg_pmt = graph_bar_pmt_median(year),
        mtg_pmt = graph_bar_pmt(state, year),
        tax = graph_pie_tax(state, year),
        chart_units = chart_units(year),
        home_aff = chart_home_aff_data[0],
        home_aff19 = chart_home_aff_19('2019'),
        map_home_aff = chart_home_aff_data[1],
        tax_burden = chart_tax_burden(year),
        home_pie = home_pie(state, year),
        bedroom_size = bedroom_size(state, year),
        total_births = chart_births(),
        state_births = chart_state_births(state))

@app.route('/predictions')
def predictions():
    return render_template('predictions.html',footer_year = foot_year)

if __name__ == "__main__":
    app.run()