import json

# Load JSON data from file
with open('roundtrip.json') as f:
    data = json.load(f)

# Function to format the flight details
def format_flight_details(flight_type, flight_name, departure, arrival, stops):
    return f"({flight_type}) {flight_name} - {departure.split('T')[0]} - {arrival.split('T')[0]} - {stops}"

# Extract Flight Name from carriers
carriers = {carrier['id']: carrier['name'] for carrier in data['carriers']}

# Extracting details for all itineraries
for itinerary in data['itineraries']:
    # Extracting collective pricing information
    price = itinerary['pricing_options'][0]['price']['amount']
    
    # Extracting leg details
    for index, leg_id in enumerate(itinerary['leg_ids']):
        for leg in data['legs']:
            if leg['id'] == leg_id:
                departure_date = leg['departure']
                arrival_date = leg['arrival']
                number_of_stops = leg['stop_count']
                carrier_id = leg['marketing_carrier_ids'][0]
                flight_name = carriers[carrier_id]
                leg_type = "Outbound" if index == 0 else "Inbound"
                
                # Print the flight details in the specified format
                print(format_flight_details(leg_type, flight_name, departure_date, arrival_date, number_of_stops))
    
    # Print the collective price once
    print(f"Total Price: ${price:.2f}\n")

