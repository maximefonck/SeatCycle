from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    # Example data structure - You can populate this from an API or Logic
    mock_results = [
        {
            "airline_code": "DL",
            "departure_time": "8:15 AM",
            "arrival_time": "11:00 AM",
            "duration": "2h 45m",
            "price": 420,
            "refill_options": [
                {"id": 1, "route": "DTW → ORD", "timing": "Departs 4:30 PM Today", "price": 150, "credit": 187.50},
                {"id": 2, "route": "DTW → JFK", "timing": "Departs 6:15 PM Today", "price": 200, "credit": 250.00}
            ]
        }
    ]
    return render_template('index.html', 
                           origin="Detroit (DTW)", 
                           destination="Orlando (MCO)", 
                           user_credits="1,250.00",
                           results=mock_results)

@app.route('/flight/<int:flight_id>')
def flight_page(flight_id):
    return render_template('flight.html', 
                           rows=range(1, 11), 
                           cols=['A', 'B', 'C', 'D'], 
                           seat_price=150)

@app.route('/ask_ai', methods=['POST'])
def ask_ai():
    data = request.json
    # Logic for Gemini would go here
    return jsonify({"answer": f"Seat {data['seat']} provides optimal value. You are saving 25% today."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)