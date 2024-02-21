# RealEstate-vs-Demographics
This is a Python Flask web application that uses Gunicorn and Nginx as web servers, and is hosted on an EC2 instance with CloudFront distribution and Route 53 and AWS ACM for domain and SSL management. The application uses US census data to analyze patterns with real estate and demographics of America. This was my first attempt at data engineering where I get the data, clean it, and analyze and generate graphs for the audience to see.

## Architecture

![architecture diagram](docs/flask-app.png)

## Data
The data compiled for this application came from the United States Census Bureau. The American Community Survey (ACS) releases new data every year in the form of estimates in a variety of tables. However given the pandamic, the 2020 year data was not published by ACS and thus 2020 data is not included in part of the analysis done in this applicaiton.

[American Community Survey](https://www.census.gov/programs-surveys/acs/data.html)
