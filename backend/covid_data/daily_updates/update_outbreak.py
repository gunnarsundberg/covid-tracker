import os
import io
import math
import requests
from datetime import datetime
from datetime import date
import pandas as pd
from covid_data.models import State, County, Outbreak, OutbreakCumulative
from covid_data.utilities import get_datetime_from_str, api_request_from_str

# Some functions only work for specific region types (state, county etc) because the data sources used differ

# Gets all state outbreak data and returns it as json object
def get_outbreak_data_by_state(outbreak_state):
    outbreak_str = "https://covidtracking.com/api/states/daily?state=" + outbreak_state.code
    print(outbreak_str)
    return api_request_from_str(outbreak_str)

# Gets all outbreak data for a specific state on a specified date and returns it as a json object
def get_outbreak_data_by_state_and_date(outbreak_state, outbreak_date):
    outbreak_str = "https://covidtracking.com/api/states/daily?state=" + outbreak_state.code + "&date=" + str(outbreak_date).replace("-","")
    return api_request_from_str(outbreak_str)

def update_state_outbreak(outbreak_data):
    for index, row in outbreak_data.iterrows():
        # If state is not a region we track, move to next iteration
        try:
            record_state = State.objects.get(code=row['state'])
        except:
            continue
        
        record_date = get_datetime_from_str(str(row['date']))
        
        # If no outbreak record exists in given state and date, create new outbreak record
        if not Outbreak.objects.filter(region=record_state, date=record_date).exists() and row['positive'] > 99: 
            daily_cases = row['positiveIncrease']
            
            daily_total_tested = row['totalTestResultsIncrease']
            daily_deaths = row['deathIncrease']

            if not math.isnan(row['negativeIncrease']):
                daily_negative_tests = row['negativeIncrease']
            else:
                daily_negative_tests = None

            if not math.isnan(row['hospitalizedIncrease']):
                daily_admitted_to_hospital = row['hospitalizedIncrease']
            else:
                daily_admitted_to_hospital = None
            
            if not math.isnan(row['hospitalizedCurrently']):
                daily_hospitalized = row['hospitalizedCurrently']
            else:
                daily_hospitalized = None
            
            if not math.isnan(row['inIcuCurrently']):
                daily_in_icu = row['inIcuCurrently']  
            else:
                daily_in_icu = None

            state_outbreak = Outbreak.objects.create(region=record_state, date=record_date, cases=daily_cases, negative_tests=daily_negative_tests, total_tested=daily_total_tested, deaths=daily_deaths, admitted_to_hospital=daily_admitted_to_hospital, hospitalized=daily_hospitalized, in_icu=daily_in_icu)
            state_outbreak.save()

            cumulative_cases = row['positive']
            cumulative_total_tested = row['totalTestResults']
            
            if not math.isnan(row['negative']):
                cumulative_negative_tests = row['negative']
            else:
                cumulative_negative_tests = None
            
            if not math.isnan(row['death']):
                cumulative_deaths = row['death']
            else:
                cumulative_deaths = None
            
            if not math.isnan(row['hospitalizedCumulative']):
                cumulative_hospitalized = row['hospitalizedCumulative']
            else:
                cumulative_hospitalized = None
            
            if not math.isnan(row['inIcuCumulative']):
                cumulative_in_icu = row['inIcuCumulative']
            else:
                cumulative_in_icu = None
            
            state_outbreak_cumulative = OutbreakCumulative.objects.create(region=record_state, date=record_date, cases=cumulative_cases, negative_tests=cumulative_negative_tests, total_tested=cumulative_total_tested, deaths=cumulative_deaths, hospitalized=cumulative_hospitalized, in_icu=cumulative_in_icu)
            state_outbreak_cumulative.save()  

def update_all_state_outbreaks(date_to_update):
    states = State.objects.all()
    for state in states:
        outbreak_json = get_outbreak_data_by_state_and_date(state, date_to_update)
        update_state_outbreak(outbreak_json)
    
# Future release
def update_county_outbreak(county_to_update, date_to_update):
    url = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv"
    county_data = requests.get(url).content
    county_data_dataframe =pd.read_csv(io.StringIO(county_data.decode('utf-8')))

