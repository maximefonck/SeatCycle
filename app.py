from flask import Flask, render_template, request, jsonify
from datetime import date, datetime, timedelta
import random
import os
import google.generativeai as genai

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-flash-lite-latest')

class RefillData:
    def __init__(self, refill_id, route, timing, price, credit):
        self.id = refill_id
        self.route = route
        self.timing = timing
        self.price = price      
        self.credit = credit    
    
    def to_dict(self):
        return self.__dict__

class FlightData:
    def __init__(self, airline, dep_time, arr_time, duration, price, refills):
        self.airline_code = airline
        self.departure_time = dep_time
        self.arrival_time = arr_time
        self.duration = duration
        self.price = price     
        self.refill_options = refills 
    
    def to_dict(self):
        return {
            "airline_code": self.airline_code,
            "departure_time": self.departure_time,
            "arrival_time": self.arrival_time,
            "duration": self.duration,
            "price": self.price,
            "refill_options": [r.to_dict() for r in self.refill_options]
        }

def generate_mock_flights(origin, destination, dep_date):
    airlines = ["DL", "AA", "UA", "B6", "NK"]
    flights = []
    
    for i in range(5):
        # Generate random times
        h1 = random.randint(6, 20)
        m1 = random.choice([0, 15, 30, 45])
        departure_time = f"{h1}:{m1:02d} AM" if h1 < 12 else f"{h1-12 if h1 > 12 else h1}:{m1:02d} PM"
        
        # Random duration between 2 and 5 hours
        duration_hrs = random.randint(2, 5)
        duration_mins = random.choice([0, 15, 30, 45])
        
        arrival_h = (h1 + duration_hrs) % 24
        arrival_m = (m1 + duration_mins) % 60
        arrival_time = f"{arrival_h}:{arrival_m:02d} AM" if arrival_h < 12 else f"{arrival_h-12 if arrival_h > 12 else arrival_h}:{arrival_m:02d} PM"

        main_flight_price = random.randint(300, 950)
        
        refills = []
        for j in range(2):
            d_price = random.randint(20, 150)
            new_refill = RefillData(
                refill_id = i * 10 + j,
                route = f"{origin} → {random.choice(['ORD', 'ATL', 'DFW'])}",
                timing = "Additional Savings",
                price = d_price,
                credit = round(d_price * 1.25, 2)
            )
            refills.append(new_refill)

        new_flight = FlightData(
            airline = random.choice(airlines),
            dep_time = departure_time,
            arr_time = arrival_time,
            duration = f"{duration_hrs}h {duration_mins}m",
            price = main_flight_price,
            refills = refills
        )
        
        flights.append(new_flight)
        
    return flights


def get_gemini_analysis(flights, origin, destination, dep_date, ret_date):
    """
    Analyzes flights using Gemini and returns recommendation text.
    Returns None if analysis fails.
    """
    try:
        prompt = f"""You are a flight booking analyst for SeatCycle, a service that helps travelers find the best flight deals based on credit opportunities.

Analyze these flights from {origin} to {destination} (departing {dep_date}, returning {ret_date}):

"""

        for idx, flight in enumerate(flights, 1):
            flight_dict = flight.to_dict()
            prompt += f"\n**Flight {idx}** ({flight_dict['airline_code']})\n"
            prompt += f"- Departure: {flight_dict['departure_time']}, Arrival: {flight_dict['arrival_time']}\n"
            prompt += f"- Duration: {flight_dict['duration']}\n"
            prompt += f"- Price: ${flight_dict['price']}\n"
            prompt += f"- Refill Options:\n"
            
            for refill in flight_dict['refill_options']:
                prompt += f"{refill['route']}: ${refill['price']} (${refill['credit']} credit)\n"
        
        prompt += """\n\nBased on this data, provide a brief recommendation (2-3 sentences) on which flight offers the best value when considering:
1. Total cost (flight price + refill price)
2. Credit earned from refill options
3. Travel time and convenience
4. Net cost after credits

Be specific about which flight number and which refill option you recommend, and explain the financial benefit clearly."""

        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"Gemini API error: {e}")
        return None

@app.route('/flight/<int:flight_id>')
def flight_page(flight_id):
    # Get the price from the URL (?price=123), default to 150 if not found
    price_from_url = request.args.get('price', 150)
    
    return render_template('flight.html', 
                           rows=range(1, 11), 
                           cols=['A', 'B', 'C', 'D'], 
                           seat_price=price_from_url)
@app.route('/ask_ai', methods=['POST'])
def ask_ai():
    data = request.json
    seat = data.get('seat')
    cost = data.get('cost')
    
    # Optional: Use Gemini to analyze the specific seat value
    try:
        prompt = f"The user is looking at seat {seat} which costs ${cost}. Give a 1-sentence witty travel tip about this seat choice."
        response = model.generate_content(prompt)
        answer = response.text
    except:
        answer = f"Seat {seat} confirmed. This choice earns you ${(float(cost)*1.25):.2f} in future flight credits."
        
    return jsonify({"answer": answer})

@app.route('/', methods=['GET', 'POST'])
def index():
    origin = "Detroit (DTW)"
    destination = "Orlando (MCO)"
    dep_date = date.today().strftime('%Y-%m-%d')
    ret_date = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
    results = []
    ai_recommendation = None
    
    if request.method == 'POST':
        origin = request.form.get('origin_input', origin)
        destination = request.form.get('destination_input', destination)
        dep_date = request.form.get('dep_date_input', dep_date)
        ret_date = request.form.get('ret_date_input', ret_date)

        results = generate_mock_flights(origin, destination, dep_date)
        
    if results:
        print("Calling Gemini...") 
        ai_recommendation = get_gemini_analysis(results, origin, destination, dep_date, ret_date)
        print(f"Gemini returned: {ai_recommendation}")  
    
    return render_template('index.html', 
                           origin=origin, 
                           destination=destination,
                           dep_date=dep_date,
                           ret_date=ret_date,
                           results=results,
                           ai_recommendation=ai_recommendation)


if __name__ == '__main__':
    app.run(debug=True)