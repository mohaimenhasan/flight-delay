import argparse
import os

import pandas as pd
from prophet import Prophet


# Function to get the prediction for the closest month-end date, with additional filtering options
def get_closest_prediction_for_date(date_to_predict, origin=None, destination=None, airline=None, carriergroup=None, flight_type=None, scheduled=None, charter=None):
    """
    Predicts the number of flights for a specific date, optionally filtering by origin, destination, airline, carrier group, 
    flight type, scheduled/charter status.

    Parameters:
    - date_to_predict: datetime, The date for which you want to predict flights.
    - origin: str, US airport code to filter flights departing from (optional).
    - destination: str, Airport code to filter flights going to a specific destination (optional).
    - airline: str, Airline code to filter flights by a specific airline (optional).
    - carriergroup: str, Carrier group to filter by airline group (optional).
    - flight_type: str, Type of flight (e.g., Departures) (optional).
    - scheduled: int, Filter by scheduled flights (1 for scheduled, 0 for non-scheduled) (optional).
    - charter: int, Filter by charter flights (1 for charter, 0 for non-charter) (optional).

    Returns:
    - closest_date: datetime, The closest available date to the requested date in the forecast.
    - predicted_total: float, The predicted number of flights.
    - lower_bound: float, The lower bound of the prediction interval.
    - upper_bound: float, The upper bound of the prediction interval.
    """
    
    # Dynamically get the directory where the script is located
    script_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Construct absolute paths for the data files
    departures_path = os.path.join(script_dir, '../data/International_Report_Departures.csv')
    
    # Load the datasets
    departures = pd.read_csv(departures_path)
    
    # Convert the 'data_dte' column to a datetime format
    departures['data_dte'] = pd.to_datetime(departures['data_dte'], format='%m/%d/%Y')
    
    # Filter by origin and destination if provided
    if origin:
        departures = departures[departures['usg_apt'] == origin]
        if departures.empty:
            raise ValueError(f"No flights found departing from the specified origin airport: {origin}")
    
    if destination:
        departures = departures[departures['fg_apt'] == destination]
        if departures.empty:
            raise ValueError(f"No flights found going to the specified destination airport: {destination}")
    
    # Filter by airline if provided
    if airline:
        departures = departures[departures['carrier'] == airline]
        if departures.empty:
            raise ValueError(f"No flights found for the specified airline: {airline}")
    
    # Filter by carrier group if provided
    if carriergroup:
        departures = departures[departures['carriergroup'] == int(carriergroup)]
        if departures.empty:
            raise ValueError(f"No flights found for the specified carrier group: {carriergroup}")
    
    # Filter by flight type if provided
    if flight_type:
        departures = departures[departures['type'] == flight_type]
        if departures.empty:
            raise ValueError(f"No flights found for the specified flight type: {flight_type}")
    
    # Filter by scheduled and charter flights if specified
    if scheduled is not None:
        departures = departures[departures['Scheduled'] == int(scheduled)]
        if departures.empty:
            raise ValueError(f"No scheduled flights found with value: {scheduled}")
    
    if charter is not None:
        departures = departures[departures['Charter'] == int(charter)]
        if departures.empty:
            raise ValueError(f"No charter flights found with value: {charter}")
    
    # Get the latest date in the dataset
    latest_date_in_data = departures['data_dte'].max()
    print(f"Latest date in the dataset: {latest_date_in_data}")
    
    # Calculate the difference between the user-specified date and the latest date in the data
    difference_in_months = (date_to_predict.year - latest_date_in_data.year) * 12 + date_to_predict.month - latest_date_in_data.month

    # Ensure we forecast for at least one month if the date is within the same month
    number_of_months_to_forecast = max(difference_in_months, 1)
    print(f"Forecasting for {number_of_months_to_forecast} months.")

    # Group the data by month-end and sum the 'Total' column
    monthly_departures = departures.groupby(pd.Grouper(key='data_dte', freq='ME')).agg({
        'Total': 'sum'
    }).reset_index()

    # Prepare the data for Prophet
    df_prophet = monthly_departures.rename(columns={'data_dte': 'ds', 'Total': 'y'})

    # Initialize and fit the Prophet model
    print("Fitting the model on historical data...")
    model = Prophet()
    model.fit(df_prophet)
    print("Model fitting completed.")

    # Make future predictions
    future = model.make_future_dataframe(periods=number_of_months_to_forecast, freq='M')
    forecast = model.predict(future)

    # Convert both 'ds' in forecast and the input date to the same date format (without time)
    forecast['ds'] = pd.to_datetime(forecast['ds']).dt.date
    date_to_predict = date_to_predict.date()

    # Find the closest date in forecast['ds'] to the given date
    closest_date = min(forecast['ds'], key=lambda x: abs(x - date_to_predict))

    # Get the prediction for the closest date
    prediction = forecast[forecast['ds'] == closest_date]
    predicted_total = prediction['yhat'].values[0]
    lower_bound = prediction['yhat_lower'].values[0]
    upper_bound = prediction['yhat_upper'].values[0]

    return closest_date, predicted_total, lower_bound, upper_bound

if __name__ == '__main__':
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Predict the number of flights for a specific date with various filtering options.')
    
    # Date to predict
    parser.add_argument('--date', type=str, required=True, help='The date for which you want to predict the number of flights in YYYY-MM-DD format.')
    
    # Filter by US airport code
    parser.add_argument('--origin', type=str, help='Optional: US airport code (e.g., JFK, LAX) to predict departures from.')
    
    # Filter by destination airport code
    parser.add_argument('--destination', type=str, help='Optional: Airport code (e.g., LHR, CDG) to predict flights going to this airport.')
    
    # Filter by airline code (two-letter IATA code)
    parser.add_argument('--airline', type=str, help='Optional: Airline code (e.g., DL for Delta, AA for American Airlines).')
    
    # Filter by carrier group (e.g., legacy, low-cost)
    parser.add_argument('--carriergroup', type=str, help='Optional: Carrier group code to filter by airline group.')
    
    # Filter by type of flight (e.g., Departures, Arrivals)
    parser.add_argument('--flight_type', type=str, help='Optional: Type of flight (e.g., Departures).')
    
    # Filter by scheduled flights (1 = scheduled, 0 = not scheduled)
    parser.add_argument('--scheduled', type=int, help='Optional: Filter by scheduled flights (1 for scheduled, 0 for non-scheduled).')
    
    # Filter by charter flights (1 = charter, 0 = not charter)
    parser.add_argument('--charter', type=int, help='Optional: Filter by charter flights (1 for charter, 0 for non-charter).')
    
    args = parser.parse_args()
    
    # Convert the input date string to a pandas datetime object
    date_to_predict = pd.to_datetime(args.date)

    # Call the function to get the prediction for the closest date
    try:
        closest_date, predicted_total, lower_bound, upper_bound = get_closest_prediction_for_date(
            date_to_predict,
            origin=args.origin,
            destination=args.destination,
            airline=args.airline,
            carriergroup=args.carriergroup,
            flight_type=args.flight_type,
            scheduled=args.scheduled,
            charter=args.charter
        )

        print(f"Predicted Total Flights on closest date {closest_date}: {predicted_total:.2f}")
        print(f"Prediction Range: {lower_bound:.2f} to {upper_bound:.2f}")
    except ValueError as e:
        print(f"Error: {e}")
