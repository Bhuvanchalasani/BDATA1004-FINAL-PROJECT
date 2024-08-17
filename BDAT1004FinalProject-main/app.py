from flask import Flask, render_template, jsonify, request, abort
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB connection settings
client = MongoClient("mongodb+srv://bhuvanchalasani:Bdat2024@datafianl.c1yzp.mongodb.net/?retryWrites=true&w=majority&appName=Datafianl")
db = client['Datafianl']  # Replace with your database name

# Web Application Routes
@app.route('/')
def index():
    # Fetch all records from MongoDB
    records_cursor = db['AAPLStock'].find().sort('timestamp', -1)
    records = list(records_cursor)

    # Calculate the min and max values
    open_min = min(record['open'] for record in records)
    open_max = max(record['open'] for record in records)
    close_min = min(record['close'] for record in records)
    close_max = max(record['close'] for record in records)
    high_min = min(record['high'] for record in records)
    high_max = max(record['high'] for record in records)
    low_min = min(record['low'] for record in records)
    low_max = max(record['low'] for record in records)
    volume_min = min(record['volume'] for record in records)
    volume_max = max(record['volume'] for record in records)

    # Limit records to display on the index page
    records_to_display = records[:5]

    # Convert timestamps to strings
    for record in records_to_display:
        record['timestamp'] = record['timestamp'].strftime('%Y-%m-%d')

    return render_template('index.html',
                           records=records_to_display,
                           open_min=open_min, open_max=open_max,
                           close_min=close_min, close_max=close_max,
                           high_min=high_min, high_max=high_max,
                           low_min=low_min, low_max=low_max,
                           volume_min=volume_min, volume_max=volume_max)

@app.route('/chart')
def chart():
    # Calculate the date range for the last 6 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    # Fetch records from MongoDB for the last 6 months
    records_cursor = db['AAPLStock'].find({
        'timestamp': {
            '$gte': start_date,
            '$lte': end_date
        }
    }).sort('timestamp', 1)  # Sort by timestamp ascending

    # Convert the cursor to a list of dictionaries
    records = [
        {
            'timestamp': record['timestamp'].strftime('%Y-%m-%d'),  # Format as string
            'open': record['open'],
            'close': record['close'],
            'high': record['high'],
            'low': record['low'],
            'volume': record['volume']
        }
        for record in records_cursor
    ]

    return render_template('charts.html', records=records)

@app.route('/api-info')
def api_info():
    return render_template('api_info.html')

@app.route('/api/items', methods=['GET'])
def get_all_items():
    items = list(db['AAPLStock'].find())
    for item in items:
        item['_id'] = str(item['_id'])  # Convert ObjectId to string for JSON serialization
    return jsonify(items), 200

@app.route('/api/items/range', methods=['GET'])
def get_items_range():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    if not start_date_str or not end_date_str:
        abort(400, description="Please provide both start_date and end_date query parameters.")

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        abort(400, description="Invalid date format. Use YYYY-MM-DD.")

    items = list(db['AAPLStock'].find({
        'timestamp': {
            '$gte': start_date,
            '$lte': end_date
        }
    }))

    for item in items:
        item['_id'] = str(item['_id'])  # Convert ObjectId to string for JSON serialization

    return jsonify(items), 200

@app.route('/api/items/<id>', methods=['GET'])
def get_item_by_id(id):
    try:
        item = db['AAPLStock'].find_one({'_id': ObjectId(id)})
        if not item:
            abort(404, description="Item not found.")

        item['_id'] = str(item['_id'])  # Convert ObjectId to string for JSON serialization
        return jsonify(item), 200
    except:
        abort(400, description="Invalid ID format.")

if __name__ == '__main__':
    app.run(debug=True)
