# Booking Catalogs API

This API allows users to log in using their customer data and flight booking data. If the user is logged in with valid credentials, the API will return details about itineraries, passengers, contact and billing information, and orderings.

## Endpoints

### Login

**Endpoint:** `POST /api/login/`

**Description:** Authenticates a user using their email and booking ID and returns detailed booking information.

#### Request

**Headers:**
Content-Type: application/json

**Body:**

```json
{
    "email": "priyesh.kumarjii@gmail.com",
    "booking_id": "VU2029001"
}
```

#### Response

**Status Code:** `200 OK`

**Body:**
```json
{
    "flight_name": "AI202",
    "departure_iata": "DEL",
    "arrival_iata": "JFK",
    "departure_date": "2023-03-15T14:30:00Z",
    "arrival_date": "2023-03-15T20:30:00Z",
    "arrival_date": "2023-03-15T20:30:00Z",
    "return_departure_iata": "JFK",
    "return_arrival_iata": "DEL",
    "return_departure_date": "2023-03-25T10:00:00Z",
    "return_arrival_date": "2023-03-25T16:00:00Z",
    "passenger": [
        {
            "first_name": "John",
            "middle_name": "A.",
            "last_name": "Doe",
            "dob": "1990-01-01",
            "gender": "Male"
        },
        {
            "first_name": "Jane",
            "middle_name": "B.",
            "last_name": "Doe",
            "dob": "1992-02-02",
            "gender": "Female"
        }
    ],
    "contact_billings": {
        "Email": "customer@example.com",
        "phone_number": "+1234567890",
        "cardholder_name": "John Doe",
        "card_number": "**** **** **** 1234"
    },
    "orderings": {
        "payble_amount": 500.00,
        "flight_cancellation_protection": 15.00,
        "sms_support": 2.00,
        "baggage_protection": 15.00,
        "premium_support": 5.00,
        "total_refund_protection": 100.00,
        "total_amount": 637.00
    }
}
```

**Status Code:** `400 Bad Request`

**Body:**
```json
{
    "error": "Please provide both email and booking ID"
}
```

**Status Code:** `404 Not Found`

**Body:**
```json
{
    "error": "Customer does not exist"
}
```
or
```json
{
    "error": "Booking does not exist"
}
```

## Integration

### Using Axios in JavaScript

**Example of Sending a Request and Parsing the Response:**

```javascript
import axios from 'axios';

const loginData = {
  email: "priyesh.kumarjii@gmail.com",
  booking_id: "VU2029001"
};

axios.post('http://crm.valueutickets.com/api/login/', loginData, {
  headers: {
    'Content-Type': 'application/json'
  }
})
.then(response => {
  const data = response.data;
  
  // Store parameters in variables
  const flightName = data.flight_name;
  const departureIata = data.departure_iata;
  const arrivalIata = data.arrival_iata;
  const departureDate = data.departure_date;
  const arrivalDate = data.arrival_date;
  const returnDepartureIata = data.return_departure_iata;
  const returnArrivalIata = data.return_arrival_iata;
  const returnDepartureDate = data.return_departure_date;
  const returnArrivalDate = data.return_arrival_date;

  const passengers = data.passenger;
  const contactBillings = data.contact_billings;
  const orderings = data.orderings;
  
  // Print stored parameters
  console.log('Flight Name:', flightName);
  console.log('Departure IATA:', departureIata);
  console.log('Arrival IATA:', arrivalIata);
  console.log('Departure Date:', departureDate);
  console.log('Arrival Date:', arrivalDate);
  
  // Print return trip details if available
  if (returnDepartureIata && returnArrivalIata && returnDepartureDate && returnArrivalDate) {
    console.log('Return Departure IATA:', returnDepartureIata);
    console.log('Return Arrival IATA:', returnArrivalIata);
    console.log('Return Departure Date:', returnDepartureDate);
    console.log('Return Arrival Date:', returnArrivalDate);
  }
  
  console.log('Passengers:');
  passengers.forEach(passenger => {
    console.log(`  Name: ${passenger.name}`);
    console.log(`  DOB: ${passenger.dob}`);
    console.log(`  Gender: ${passenger.gender}`);
    console.log(`  Age: ${passenger.age}`);
  });
  
  console.log('Contact & Billings:');
  console.log('  Email:', contactBillings.Email);
  console.log('  Phone Number:', contactBillings.phone_number);
  console.log('  Cardholder Name:', contactBillings.cardholder_name);
  console.log('  Card Number (Last 4 Digits):', contactBillings.card_number);
  
  console.log('Orderings:');
  console.log('  Payable Amount:', orderings.payble_amount);
  console.log('  Flight Cancellation Protection:', orderings.flight_cancellation_protection);
  console.log('  SMS Support:', orderings.sms_support);
  console.log('  Baggage Protection:', orderings.baggage_protection);
  console.log('  Premium Support:', orderings.premium_support);
  console.log('  Total Refund Protection:', orderings.total_refund_protection);
  console.log('  Total Amount:', orderings.total_amount);
})
.catch(error => {
  if (error.response) {
    console.error('Error:', error.response.data.error);
  } else {
    console.error('Error:', error.message);
  }
});
```
