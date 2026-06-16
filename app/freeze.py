"""Generate a fully static copy of the site into ../build/ using Frozen-Flask."""

from flask_frozen import Freezer

from app import app, state_url_generator

app.config['FREEZER_DESTINATION'] = '../build'
app.config['FREEZER_RELATIVE_URLS'] = True
app.config['FREEZER_REMOVE_EXTRA_FILES'] = True
app.config['FREEZER_STATIC_IGNORE'] = ['*.scss', 'sass/*']

freezer = Freezer(app)
freezer.register_generator(state_url_generator)

if __name__ == '__main__':
    freezer.freeze()
    print('Static site written to build/')
