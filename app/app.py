from flask import Flask, render_template, request
from jinja2 import Environment, FileSystemLoader
from graph_generator import graph_pyramid, graph_bar, graph_pie

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

pop_pyramid = graph_pyramid('California', '2022')

jinja2_env = Environment(loader=FileSystemLoader('./templates'), autoescape=True)
template = jinja2_env.get_template("index.html")

@app.route("/")
def home():
    return template.render(pop_pyramid=pop_pyramid, state_abbreviations=state_abbreviations)

@app.route("/state")
def state():
    state_abbr = request.args.get('state')
    # Get the full state name from the abbreviation
    state = next((key for key, value in state_abbreviations.items() if value == state_abbr), None)
    if state is None:
        return "Invalid state abbreviation"
    pop_pyramid = graph_pyramid(state, '2022')
    home_value = graph_bar(state,'2022')
    mort_stat = graph_pie(state,'2022')
    return template.render(pop_pyramid=pop_pyramid, state_abbreviations=state_abbreviations, state=state, home_value=home_value, mort_stat=mort_stat)

if __name__ == "__main__":
    app.run()