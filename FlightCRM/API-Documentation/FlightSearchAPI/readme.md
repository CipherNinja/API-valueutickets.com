```markdown
# Flight Search API

This API is used to fetch flight schedules and fares for a particular date based on the input JSON provided. It supports searching for one-way trips.

## Access Endpoint

The API can be accessed via a POST request at:

```
/api/v1/flight/search/onewaytrip/
```

## Request

### JSON Payload

The JSON payload for the POST request should follow this structure:

```json
{
    "source_iata": "JFK",
    "destination_iata": "LHR",
    "date": "2023-06-15",
    "adults": 2,
    "children": 1,
    "infants": 0,
    "ticket_class": "Economy"
}
```

### Fields Description

- `source_iata` (string, max length 3): Departure Airport IATA code.
- `destination_iata` (string, max length 3): Arrival Airport IATA code.
- `date` (string, format "YYYY-MM-DD"): Flight date.
- `adults` (integer, default 1): Number of adult passengers.
- `children` (integer, default 0): Number of children (0-12 years).
- `infants` (integer, default 0): Number of infants (0-2 years).
- `ticket_class` (string, default "Economy"): Ticket class (Economy, Premium_Economy, Business, First).

## Response

The API will return a JSON response with the flight details and fare information. Example response:

```json
{
    "flight_details": [
        {
            "flight_number": "BA178",
            "departure_time": "2023-06-15T07:30:00",
            "arrival_time": "2023-06-15T19:30:00",
            "duration": "12h",
            "fare": {
                "currency": "USD",
                "amount": 1200
            }
        }
    ]
}
```

### Response Fields

- `flight_details`: Array of flight details
  - `flight_number` (string): Flight number.
  - `departure_time` (string, format "YYYY-MM-DDTHH:MM:SS"): Departure time.
  - `arrival_time` (string, format "YYYY-MM-DDTHH:MM:SS"): Arrival time.
  - `duration` (string): Flight duration.
  - `fare` (object): Fare information.
    - `currency` (string): Currency of the fare amount.
    - `amount` (number): Fare amount.

## Example Request

```bash
curl -X POST \
  /api/v1/flight/search/onewaytrip/ \
  -H 'Content-Type: application/json' \
  -d '{
        "source_iata": "JFK",
        "destination_iata": "LHR",
        "date": "2023-06-15",
        "adults": 2,
        "children": 1,
        "infants": 0,
        "ticket_class": "Economy"
      }'
```

## Notes

- Ensure the IATA codes are valid and supported by the API.
- Date format should be strictly followed to avoid validation errors.
- The number of passengers should be within the specified range.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contributing

We welcome contributions! Please open an issue or submit a pull request.
