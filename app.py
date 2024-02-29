# app.py
from flask import Flask, request, jsonify
from flask import render_template
import subprocess
import json

app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template("index.html") # This should be the name of your HTML file

@app.route('/execute', methods=['POST'])
def execute_algo():
    # Get the JSON data from the request
    json_data = request.get_json()

    # Write the JSON data to a file for algo.py to use as input
    with open('input.json', 'w') as input_file:
        json.dump(json_data, input_file)

    # Execute algo.py and capture its output
    result = subprocess.run(['python', 'algo.py'], capture_output=True)
    
    # Assuming that algo.py writes its output to a file called output.json
    with open('output.json', 'r') as output_file:
        output_data = json.load(output_file)

    for i in output_data:
        print(i)

    return jsonify(output_data)

if __name__ == "__main__":
    app.run(debug=True)