import os
import requests
from datetime import datetime, date, time , timedelta
import pytz
from pytz import utc, timezone
from covid_data.models import StateAirport, StateDailyFlights, State
from covid_data.utilities import get_local_timestamp, api_request_from_str

username = os.environ['OPENSKY_USERNAME']
password = os.environ['OPENSKY_PASSWORD']   

def get_flights_by_state(state, flights_date):
    number_of_inbound_flights = 0
    number_of_outbound_flights = 0

    state_airports = StateAirport.objects.filter(state=state)

    for airport in state_airports:
        begin_timestamp, end_timestamp = get_local_timestamp(airport.timezone, flights_date)
        
        inbound_flights_request_str = "https://" + username + ":" + password + "@opensky-network.org/api/flights/arrival?airport=" + str(airport.icao_code) + "&begin=" + str(begin_timestamp) + "&end=" + str(end_timestamp)
        outbound_flights_request_str = "https://" + username + ":" + password + "@opensky-network.org/api/flights/departure?airport=" + str(airport.icao_code) + "&begin=" + str(begin_timestamp) + "&end=" + str(end_timestamp)

        inbound_flights_json = api_request_from_str(inbound_flights_request_str)
        outbound_flights_json = api_request_from_str(outbound_flights_request_str)
        
        try:
            for flight in inbound_flights_json:
                if flight:
                    number_of_inbound_flights += 1
        except:
            print("Couldn't get inbound flights for " + str(airport.airport_name) + " on " + str(flights_date))

        try:
            for flight in outbound_flights_json:
                if flight:
                    number_of_outbound_flights += 1
        except:
            print("Couldn't get outbound flights for " + str(airport.airport_name) + " on " + str(flights_date))
    
    return number_of_inbound_flights, number_of_outbound_flights

def update_state_flights(state, date_to_update):
    number_of_inbound_flights, number_of_outbound_flights = get_flights_by_state(state, date_to_update)
    new_daily_flights = StateDailyFlights.objects.create(date=date_to_update, state=state, number_of_inbound_flights = number_of_inbound_flights, number_of_outbound_flights=number_of_outbound_flights)
    new_daily_flights.save()

def update_flights_daily():
    yesterday = date.today() - timedelta(days = 1)
    print(yesterday)
    import_flights(yesterday)