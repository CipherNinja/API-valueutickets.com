class FlightRoundTrip(APIView):
    def post(self, request):
        serializer = FlightSearchRoundTrip(data=request.data)
        if serializer.is_valid():
            source = serializer.validated_data.get('source_iata')
            destination = serializer.validated_data.get('destination_iata')
            outbound = serializer.validated_data.get('outbound')
            inbound = serializer.validated_data.get('inbound')
            adults = serializer.validated_data.get('adults')
            children = serializer.validated_data.get('children')
            infants = serializer.validated_data.get('infants')
            ticket_class = serializer.validated_data.get('ticket_class')

            api_url = f"https://api.flightapi.io/roundtrip/{Flight_Key}/{source}/{destination}/{outbound}/{inbound}/{adults}/{children}/{infants}/{ticket_class}/USD"
            try:
                response = requests.get(api_url)
                response.raise_for_status()
            except requests.exceptions.HTTPError as http_err:
                return Response({"error": f"HTTP error occurred: {http_err}"}, status=response.status_code)
            except Exception as err:
                return Response({"error": f"An error occurred: {err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if response.status_code == 200:
                data = response.json()
                
                carrier_map = {carrier["id"]: carrier["name"] for carrier in data.get("carriers", [])}
                carrier_code_map = {carrier["id"]: carrier["display_code"] for carrier in data.get("carriers", [])}
                legs_map = {leg["id"]: leg for leg in data.get("legs", [])}
                segment_map = {segment["id"]: segment for segment in data.get("segments", [])}
                
                flight_details = []
                for itinerary in data.get("itineraries", []):
                    total_price = itinerary.get("pricing_options", [{}])[0].get("price", {}).get("amount", "Unknown")
                    legs = []
                    for index, leg_id in enumerate(itinerary.get("leg_ids", [])):
                        leg_details = legs_map.get(leg_id, {})
                        departure = leg_details.get("departure", "Unknown")
                        arrival = leg_details.get("arrival", "Unknown")
                        duration = leg_details.get("duration", "Unknown")
                        stop_count = leg_details.get("stop_count", "Unknown")
                        marketing_carrier_id = leg_details.get("marketing_carrier_ids", [None])[0]
                        flight_name = carrier_map.get(marketing_carrier_id, "Unknown")
                        carrier_code = carrier_code_map.get(marketing_carrier_id, "")
                        leg_type = "Outbound" if index == 0 else "Inbound"
                        
                        segment_ids = leg_details.get("segment_ids", [])
                        flight_numbers = [
                            carrier_code + segment_map[segment_id]["marketing_flight_number"]
                            for segment_id in segment_ids
                            if segment_id in segment_map
                        ]
                        
                        legs.append({
                            "leg_type": leg_type,
                            "flight_name": flight_name,
                            "departure": departure,
                            "arrival": arrival,
                            "duration": duration,
                            "stop_count": stop_count,
                            "flight_numbers": flight_numbers
                        })
                    
                    flight_details.append({
                        "legs": legs,
                        "total_price": total_price
                    })
                
                return Response(flight_details, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to fetch flight data"}, status=response.status_code)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
