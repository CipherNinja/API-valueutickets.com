# Hotel Booking API

## Overview
The Hotel Booking API is designed to allow frontend applications to interact with the backend for managing hotel bookings. It supports creating bookings and includes validations to ensure data integrity.

---

## Access URL
```
https://crm.valueutickets.com/api/v4/
```

---

## Endpoints

### 1. Create a Hotel Booking
**POST** `/hotel-booking/`

This endpoint allows you to create a new hotel booking by sending the necessary booking details in the request body.

#### Request Body
Send a JSON object with the following fields:

| Field            | Type     | Required | Description                                  |
|------------------|----------|----------|----------------------------------------------|
| `phone_number`   | string   | Yes      | International phone number with country code (e.g., +919876543210). |
| `email`          | string   | Yes      | Customer's email address.                   |
| `checkin_datetime` | string | Yes      | Check-in date and time in ISO 8601 format (`YYYY-MM-DDTHH:MM:SS`). |
| `checkout_datetime`| string | Yes     | Check-out date and time in ISO 8601 format (`YYYY-MM-DDTHH:MM:SS`). |
| `adults`         | integer  | Yes      | Number of adult guests (minimum: 1).         |
| `children`       | integer  | No       | Number of children (default: 0).             |
| `infants`        | integer  | No       | Number of infants (default: 0).              |
| `destination`    | string   | Yes      | Destination name or address.                 |

#### Example Request
```json
{
    "phone_number": "+919876543210",
    "email": "customer@example.com",
    "checkin_datetime": "2025-03-15T14:00:00",
    "checkout_datetime": "2025-03-20T11:00:00",
    "adults": 2,
    "children": 1,
    "infants": 0,
    "destination": "Goa"
}
```

#### Response

| Field         | Type    | Description                                  |
|---------------|---------|----------------------------------------------|
| `Booking_ID`  | string  | The unique identifier for the booking.       |
| `Message`     | string  | Confirmation message for successful booking. |

#### Success Response
**Status Code**: `201 Created`
```json
{
    "Booking_ID": "HTL2029001",
    "Message": "Successfully Created"
}
```

#### Error Response
**Status Code**: `406 Not Acceptable`
```json
{
    "Error": {
        "field_name": [
            "error message"
        ]
    }
}
```

---

## Validations
1. **Phone Number**: Must be in a valid international format with the country code (e.g., `+919876543210`).
2. **Dates**: 
   - `checkin_datetime` cannot be in the past.
   - `checkout_datetime` must be later than `checkin_datetime`.
3. **Adults**: Minimum of 1 adult is required.
4. **Children and Infants**: Defaults to 0 if not provided.

---

## Email Notifications
Upon successful booking creation, the API will automatically send a confirmation email to the customer. The email includes:
- Booking ID
- Check-in and Check-out dates
- Number of guests
- Destination details

---

## Developer Notes
- Ensure the request header contains `Content-Type: application/json`.
- Test the API endpoints using tools like Postman or cURL before integration.
- Handle error responses gracefully by displaying appropriate feedback to users.

---

```
