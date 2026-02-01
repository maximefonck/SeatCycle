from flask import Flask, render_template, request
from datetime import date, datetime, timedelta
import random

app = Flask(__name__)



def generate_mock_flights(origin, destination, dep_date):
    airlines = ["DL", "AA", "UA", "B6", "NK"]
    flights = []
    
    for i in range(5):
        # Generate random times
        h1 = random.randint(6, 20)
        m1 = random.choice([0, 15, 30, 45])
        departure_time = f"{h1}:{m1:02d} AM" if h1 < 12 else f"{h1-12}:{m1:02d} PM"
        
        # Random duration between 2 and 5 hours
        duration_hrs = random.randint(2, 5)
        duration_mins = random.choice([0, 15, 30, 45])
        
        arrival_h = (h1 + duration_hrs) % 24
        arrival_time = f"{arrival_h}:{m1:02d} AM" if arrival_h < 12 else f"{arrival_h-12}:{m1:02d} PM"

        main_flight_price = random.randint(300, 950)
        
        # Create the nested refill options
        refill_options = []
        for j in range(2):
            # This is the "Discounter Price" you want to show
            d_price = random.randint(20, 150) 
            
            refill_options.append({
                "id": i * 10 + j,
                "route": f"{origin} → {random.choice(['ORD', 'ATL', 'DFW'])}",
                "timing": f"Alternative for {dep_date}",
                "price": d_price,  # Set this to the discounter price
                "credit": round(d_price * 1.25, 2) # 1.25x calculation
            })

        flights.append({
            "airline_code": random.choice(airlines),
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "duration": f"{duration_hrs}h {duration_mins}m",
            "price": main_flight_price,
            "refill_options": refill_options
        })
    return flights


@app.route('/', methods=['GET', 'POST'])
def index():
    origin = "Detroit (DTW)"
    destination = "Orlando (MCO)"
    dep_date = date.today().strftime('%Y-%m-%d')
    ret_date = date.today().strftime('%Y-%m-%d')
    results = []
    
    if request.method == 'POST':
        origin = request.form.get('origin_input', origin)
        destination = request.form.get('destination_input', destination)
        dep_date = request.form.get('dep_date_input', dep_date)
        ret_date = request.form.get('ret_date_input', ret_date)

        # Local generation instead of Gemini API
        results = generate_mock_flights(origin, destination, dep_date)
    
    return render_template('index.html', 
                           origin=origin, 
                           destination=destination,
                           dep_date=dep_date,
                           ret_date=ret_date,
                           results=results)

if __name__ == '__main__':
    app.run(debug=True)