
# **Flight Booking API Documentation**

## Overview

This API endpoint allows frontend developers to send a **single POST request** to create a **flight booking**. The request should contain data about the customer, passengers, and payment details, and the response will provide confirmation along with the IDs of the created records.


## **API Endpoint**

**POST** `/api/v2/flight/booking/`

This endpoint handles the creation of a flight booking with all related data (customer, passengers, payment).

---

## **Request Body**

You will need to send a **JSON object** with the following structure:

### **Input Data for Onewaytrips**

```json
{
    "phone_number": "+1234567890",
    "email": "example@email.com",
    "date": "2025-02-06T14:30:00Z",
    "flight_name": "Airway Express 123",
    "departure_iata": "JFK",
    "arrival_iata": "LAX",
    "departure_date": "2025-02-10T08:00:00Z",
    "arrival_date": "2025-02-10T11:00:00Z",
    "passengers": [
        {
            "first_name": "John",
            "middle_name": "A",
            "last_name": "Doe",
            "dob": "1990-01-01",
            "gender": "Male"
        },
        {
            "first_name": "Jane",
            "middle_name": "",
            "last_name": "Smith",
            "dob": "1995-05-10",
            "gender": "Female"
        }
    ],
    "payment": {
        "address_line1": "123 Main St",
        "address_line2": "Apt 4B",
        "country": "USA",
        "state": "NY",
        "city": "New York",
        "postal_code": "10001",
        "card_number": "4111111111111111",
        "card_expiry_month": 12,
        "card_expiry_year": 2026,
        "cvv": 123,
        "cardholder_name": "John Doe"
    },
    "flight_cancellation_protection": true,
    "sms_support": false,
    "baggage_protection": true,
    "premium_support": false,
    "total_refund_protection": true,
    "payble_amount": 850.00
}
```

### **Input Data for Roundtrips**

**Status Code:** `200 OK`

**Body:**
```json
{
    "flight_name": "Flight ABC123",
    "departure_iata": "JFK",
    "arrival_iata": "LHR",
    "departure_date": "2025-03-15T10:00:00Z",
    "arrival_date": "2025-03-15T18:00:00Z",
    "return_departure_iata": "LHR",
    "return_arrival_iata": "JFK",
    "return_departure_date": "2025-03-20T06:00:00Z",
    "return_arrival_date": "2025-03-20T11:00:00Z",
    "passenger": [
        {
            "name": "John A. Doe",
            "dob": "1990-01-01",
            "gender": "Male",
            "age": 35
        }
    ],
    "contact_billings": {
        "Email": "user@example.com",
        "phone_number": "1234567890",
        "cardholder_name": "John Doe",
        "card_number": "1234"
    },
    "orderings": {
        "payble_amount": 500.0,
        "flight_cancellation_protection": 15,
        "sms_support": 2,
        "baggage_protection": 15,
        "premium_support": 5,
        "total_refund_protection": 100,
        "total_amount": 637.0
    }
}
```


### **Field Descriptions**

- **phone_number**: A string representing the customer's phone number (e.g., `"+1234567890"`).
- **email**: A string representing the customer's email address (e.g., `"customer@example.com"`).
- **date**: A string representing the booking date and time in ISO 8601 format (e.g., `"2025-02-04T12:00:00Z"`).
- **passengers**: A list of passenger objects, where each object contains:
  - `first_name`: First name of the passenger (e.g., `"John"`).
  - `middle_name`: Middle name of the passenger (optional).
  - `last_name`: Last name of the passenger (e.g., `"Doe"`).
  - `dob`: Date of birth (in `YYYY-MM-DD` format, e.g., `"1990-01-01"`).
  - `gender`: Gender of the passenger (e.g., `"Male"`).
- **payment**: A dictionary containing payment details:
  - `address_line1`: Address line 1 (e.g., `"123 Main St"`).
  - `address_line2`: Address line 2 (optional).
  - `country`: The country of the address (e.g., `"USA"`).
  - `state`: The state of the address (e.g., `"NY"`).
  - `city`: The city of the address (e.g., `"New York"`).
  - `postal_code`: The postal code (e.g., `"10001"`).
  - `card_number`: Credit card number (e.g., `"4111111111111111"`).
  - `card_expiry_month`: Card expiration month (e.g., `12`).
  - `card_expiry_year`: Card expiration year (e.g., `2026`).
  - `cvv`: Card verification value (CVV) (e.g., `123`).
  - `cardholder_name`: Name on the credit card (e.g., `"John Doe"`).
- **flight_cancellation_protection**: A boolean indicating if flight cancellation protection is enabled (`true` or `false`).
- **sms_support**: A boolean indicating if SMS support is enabled (`true` or `false`).
- **baggage_protection**: A boolean indicating if baggage protection is enabled (`true` or `false`).
- **premium_support**: A boolean indicating if premium support is enabled (`true` or `false`).
- **total_refund_protection**: A boolean indicating if total refund protection is enabled (`true` or `false`).
- **payble_amount**: The total payable amount for the booking in USD (e.g., `850.00`).

---

## **Response**

After a successful request, the API will return a **201 Created** response with the following structure:

### **Example Output Response**

```json
{
    "message": "Booking successful!",
    "data": {
        "customer_id": 1,
        "booking_id": 2,
        "payment_id": 3,
        "passenger_ids": [4, 5]
    }
}
```

### **Response Details**
- **message**: A success message indicating that the booking was successful.
- **data**: A dictionary containing the IDs of the created records:
  - **customer_id**: The ID of the customer record (e.g., `1`).
  - **booking_id**: The ID of the flight booking record (e.g., `2`).
  - **payment_id**: The ID of the payment record (e.g., `3`).
  - **passenger_ids**: A list of passenger IDs (e.g., `[4, 5]`).

---

## **Testing the Request**

You can test this API using **Postman** or **cURL**. Here’s how to do it:

### **Using Postman**

1. **Set the HTTP method** to `POST`.
2. **URL**: Enter the URL `http://crm.valueutickets.com/api/v2/flight/booking/`.
3. **Body**: In the "Body" tab, select "raw" and set the type to `JSON`. Then, paste the **input data** in the text area.
4. **Send** the request.
5. You should receive a **201 Created** response with a success message and the IDs of the created records.

### **Using cURL**

You can also send a POST request using **cURL** from your terminal:

```bash
curl -X POST http://<your-server-url>/api/v2/flight/booking/ \
-H "Content-Type: application/json" \
-d '{
    "phone_number": "+1234567890",
    "email": "customer@example.com",
    "date": "2025-02-04T12:00:00Z",
    "passengers": [
        {
            "first_name": "John",
            "middle_name": "A",
            "last_name": "Doe",
            "dob": "1990-01-01",
            "gender": "Male"
        },
        {
            "first_name": "Jane",
            "middle_name": "",
            "last_name": "Smith",
            "dob": "1995-05-10",
            "gender": "Female"
        }
    ],
    "payment": {
        "address_line1": "123 Main St",
        "address_line2": "Apt 4B",
        "country": "USA",
        "state": "NY",
        "city": "New York",
        "postal_code": "10001",
        "card_number": "4111111111111111",
        "card_expiry_month": 12,
        "card_expiry_year": 2026,
        "cvv": 123,
        "cardholder_name": "John Doe"
    },
    "flight_cancellation_protection": true,
    "sms_support": false,
    "baggage_protection": true,
    "premium_support": false,
    "total_refund_protection": true,
    "payble_amount": 850.00
}'
```

---

## **Error Handling**

If the data sent in the request is invalid or incomplete, the server will respond with a **400 Bad Request** along with an error message detailing the issue.

### **Example Error Response**

```json
{
    "phone_number": ["This field is required."],
    "email": ["This field is required."]
}
```

This means the **phone_number** and **email** fields are required but were not provided.

---

## Conclusion

With this API, frontend developers can easily create a **flight booking** by sending a **single POST request** with all the necessary information about the customer, passengers, and payment. The API returns a confirmation message along with the IDs of the created records. 🎉✈️
