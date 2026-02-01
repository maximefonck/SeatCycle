from flask import Flask, render_template, request, jsonify
from datetime import date

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Set default values (Today and Tomorrow)
    origin = "Detroit (DTW)"
    destination = "Orlando (MCO)"
    dep_date = date.today().strftime('%Y-%m-%d')
    ret_date = date.today().strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        # Capture the text inputs
        origin = request.form.get('origin_input', origin)
        destination = request.form.get('destination_input', destination)
        
        # Capture the date inputs
        dep_date = request.form.get('dep_date_input', dep_date)
        ret_date = request.form.get('ret_date_input', ret_date)

    mock_results = [
        {
            "airline_code": "DL",
            "departure_time": "8:15 AM",
            "arrival_time": "11:00 AM",
            "duration": "2h 45m",
            "price": 420,
            "refill_options": [
                {"id": 1, "route": f"{origin} → ORD", "timing": f"Departs {dep_date}", "price": 150, "credit": 187.50}
            ]
        }
    ]
    
    return render_template('index.html', 
                           origin=origin, 
                           destination=destination,
                           dep_date=dep_date,
                           ret_date=ret_date,
                           user_credits="1,250.00",
                           results=mock_results)