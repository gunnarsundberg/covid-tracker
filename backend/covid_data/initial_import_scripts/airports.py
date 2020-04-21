import pandas as pd
from covid_data.models import State, StateAirport

# Takes in pandas dataframe and adds counties
def import_state_airports(airports):
    for index, row in airports.iterrows():
        airport_name = row['name']
        airport_icao_code = row['icao']
        airport_timezone = row['timezone_pytz']
        airport_state_name = row['state']
        airport_state_object = State.objects.get(state_name=airport_state_name)

        new_state_airport = StateAirport(airport_name=airport_name, icao_code=airport_icao_code, timezone=airport_timezone, state=airport_state_object)
        new_state_airport.save()