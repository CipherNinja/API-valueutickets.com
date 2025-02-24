## FlightRoundTrip API Documentation

### API Endpoint
**URL:** `https://crm.valueutickets.com/api/v1/flight/search/roundtrip/`

**Method:** `POST`

### Request JSON Structure
```json
{
    "source_iata": "PDX",
    "destination_iata": "IAH",
    "outbound": "2025-02-26",
    "inbound": "2025-03-03",
    "adults": 1,
    "children": 0,
    "infants": 0,
    "ticket_class": "Economy"
}
```

### Request Parameters
- `source_iata` (string, required): Departure Airport IATA code (e.g., "PDX").
- `destination_iata` (string, required): Arrival Airport IATA code (e.g., "IAH").
- `outbound` (date, required): Outbound flight date in the format YYYY-MM-DD.
- `inbound` (date, required): Inbound (return) flight date in the format YYYY-MM-DD.
- `adults` (integer, required): Number of adult passengers (min: 1, max: 9).
- `children` (integer, required): Number of children passengers (0-12 years) (min: 0, max: 9).
- `infants` (integer, required): Number of infant passengers (0-2 years) (min: 0, max: 9).
- `ticket_class` (string, required): Class of the ticket. Possible values: "Economy", "Premium Economy", "Business", "First".

### Response JSON Structure
```json
[
    {
        "legs": [
            {
                "leg_type": "Outbound",
                "flight_name": "United",
                "departure": "2025-02-26T06:00:00",
                "arrival": "2025-02-26T17:00:00",
                "duration": 540,
                "stop_count": 1
            },
            {
                "leg_type": "Inbound",
                "flight_name": "United",
                "departure": "2025-03-03T16:32:00",
                "arrival": "2025-03-03T21:05:00",
                "duration": 393,
                "stop_count": 1
            }
        ],
        "total_price": 1132.41
    },
    {
        "legs": [
            {
                "leg_type": "Outbound",
                "flight_name": "United",
                "departure": "2025-02-26T09:00:00",
                "arrival": "2025-02-26T17:25:00",
                "duration": 385,
                "stop_count": 1
            },
            {
                "leg_type": "Inbound",
                "flight_name": "United",
                "departure": "2025-03-03T08:15:00",
                "arrival": "2025-03-03T13:48:00",
                "duration": 453,
                "stop_count": 1
            }
        ],
        "total_price": 1327.71
    }
]
```

### Response Parameters
- `legs` (array of objects): Contains details of each leg of the trip.
  - `leg_type` (string): Type of leg ("Outbound" or "Inbound").
  - `flight_name` (string): Name of the airline.
  - `departure` (string): Departure date and time in ISO 8601 format.
  - `arrival` (string): Arrival date and time in ISO 8601 format.
  - `duration` (integer): Duration of the flight in minutes.
  - `stop_count` (integer): Number of stops.
- `total_price` (float): Total price of the round trip.

### Example Request
```bash
curl -X POST "https://crm.valueutickets.com/api/v1/flight/search/roundtrip/" \
-H "Content-Type: application/json" \
-d '{
    "source_iata": "PDX",
    "destination_iata": "IAH",
    "outbound": "2025-02-26",
    "inbound": "2025-03-03",
    "adults": 1,
    "children": 0,
    "infants": 0,
    "ticket_class": "Economy"
}'
```

### Example Response
```json
[
    {
        "legs": [
            {
                "leg_type": "Outbound",
                "flight_name": "United",
                "departure": "2025-02-26T06:00:00",
                "arrival": "2025-02-26T17:00:00",
                "duration": 540,
                "stop_count": 1
            },
            {
                "leg_type": "Inbound",
                "flight_name": "United",
                "departure": "2025-03-03T16:32:00",
                "arrival": "2025-03-03T21:05:00",
                "duration": 393,
                "stop_count": 1
            }
        ],
        "total_price": 1132.41
    },
    {
        "legs": [
            {
                "leg_type": "Outbound",
                "flight_name": "United",
                "departure": "2025-02-26T09:00:00",
                "arrival": "2025-02-26T17:25:00",
                "duration": 385,
                "stop_count": 1
            },
            {
                "leg_type": "Inbound",
                "flight_name": "United",
                "departure": "2025-03-03T08:15:00",
                "arrival": "2025-03-03T13:48:00",
                "duration": 453,
                "stop_count": 1
            }
        ],
        "total_price": 1327.71
    }
]
```