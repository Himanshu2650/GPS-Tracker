# from flask import Flask, render_template, request, jsonify
# from datetime import datetime
# import os
# import csv
# from utils.pdf_generator import generate_pdf
# from utils.email_sender import send_email

# app = Flask(__name__)
# CSV_FILE = 'temp/data.csv'

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/start', methods=['POST'])
# def start_walk():
#     try:
#         os.makedirs('temp', exist_ok=True)
#         start_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

#         with open(CSV_FILE, 'w', newline='') as file:
#             writer = csv.writer(file)
#             # Write Start Time in the first row with headers
#             writer.writerow(['Start Time'])
#             # Add the actual start time in the second row
#             writer.writerow([start_time])

#         print("Start time saved:", start_time)
#         return jsonify({'status': 'started', 'start_time': start_time})
#     except Exception as e:
#         print("Error in /start:", e)
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# @app.route('/scan', methods=['POST'])
# def scan_qr():
#     data = request.json
#     scan_time = data.get('scan_time')
#     gps = data.get('gps')
#     address = data.get('address')
#     qr_text = data.get('qr_text')

#     try:
#         # Append the scan data to the CSV file
#         with open(CSV_FILE, 'a', newline='') as f:
#             writer = csv.writer(f)
#             # Write the scan data in the next row
#             writer.writerow([scan_time, address])
#         return jsonify({'status': 'success'})
#     except Exception as e:
#         print("Error in /scan:", e)
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# @app.route('/submit', methods=['POST'])
# def submit_walk():
#     try:
#         os.makedirs('temp', exist_ok=True)
#         Submit_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

#         with open(CSV_FILE, 'a', newline='') as file:
#             writer = csv.writer(file)
#             # Write Start Time in the first row with headers
#             writer.writerow(['Submit Time'])
#             # Add the actual start time in the second row
#             writer.writerow([Submit_time])

#         print("Start time saved:", Submit_time)
#         pdf_path = generate_pdf(CSV_FILE)
#         send_email(pdf_path)
#         os.remove(CSV_FILE)
#         os.remove(pdf_path)
#         return jsonify({'status': 'submitted', 'Submit_time': Submit_time})
#     except Exception as e:
#         print("Error in /submit:", e)
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)

#GOOGLE_MAPS_API_KEY = 'YYAIzaSyDcnruTEV42C6rCNisqJ9NtbuG6CUGQ6sI'

from flask import Flask, render_template, request, jsonify
import csv
import os
import folium
from datetime import datetime
from utils.pdf_generator import generate_walk_pdf
from utils.email_sender import send_email_with_map

app = Flask(__name__)

DATA_FILE = 'temp/data.csv'
MAP_IMAGE = 'static/walk_map.png'
MAP_HTML = 'temp/map.html'
PDF_REPORT = 'temp/walk_report.pdf'

os.makedirs('temp', exist_ok=True)
os.makedirs('static', exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_walk', methods=['POST'])
def start_walk():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Timestamp', 'Latitude', 'Longitude'])
        writer.writerow([timestamp, lat, lon])

    return {"message": "✅ Walk started and first GPS point saved."}


@app.route('/save_position', methods=['POST'])
def save_position():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if lat is None or lon is None:
        return jsonify({'error': 'Missing GPS data'}), 400

    with open(DATA_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([timestamp, lat, lon])

    return jsonify({'message': '✅ Position saved'})

@app.route('/submit_walk', methods=['POST'])
def submit_walk():
    if not os.path.exists(DATA_FILE):
        return "❌ No data file found."

    lats, lons, timestamps = [], [], []

    with open(DATA_FILE, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                if not row['Latitude'] or not row['Longitude']:
                    continue
                lats.append(float(row['Latitude']))
                lons.append(float(row['Longitude']))
                timestamps.append(row['Timestamp'])
            except (ValueError, KeyError):
                continue

    if not lats or not lons:
        return "❌ No GPS points captured."

    walk_map = folium.Map(location=[lats[0], lons[0]], zoom_start=17)
    coordinates = list(zip(lats, lons))
    folium.PolyLine(coordinates, color='blue', weight=5).add_to(walk_map)
    folium.Marker(coordinates[0], tooltip='Start', icon=folium.Icon(color='green')).add_to(walk_map)
    folium.Marker(coordinates[-1], tooltip='End', icon=folium.Icon(color='red')).add_to(walk_map)

    walk_map.save(MAP_HTML)

    # Convert to PNG using selenium
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.headless = True
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(800, 600)
    driver.get(f'file://{os.path.abspath(MAP_HTML)}')
    driver.save_screenshot(MAP_IMAGE)
    driver.quit()

    generate_walk_pdf(timestamps[0], timestamps[-1], MAP_IMAGE, PDF_REPORT)

    try:
        send_email_with_map(PDF_REPORT)
    except Exception as e:
        return f"✅ Map created, ❌ Email failed: {str(e)}"

    # Clean up
    open(DATA_FILE, 'w').close()
    if os.path.exists(MAP_IMAGE): os.remove(MAP_IMAGE)

    return "✅ Walk map created, emailed, and data cleared!"

if __name__ == '__main__':
    app.run(debug=True)
