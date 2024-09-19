from flask import Flask, request, jsonify, render_template
import subprocess
import time
import os
import re

app = Flask(__name__)

# Route to render the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle curl command execution
@app.route('/run_curl', methods=['POST'])
def run_curl():
    try:
        curl_command = request.json.get('command')
        
        # Ensure the command includes -i to return headers
        if '-i' not in curl_command:
            curl_command += ' -i'
        
        # Start the timing for the request
        start_time = time.time()
        
        # Execute the curl command using subprocess
        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
        
        # Calculate the timing
        end_time = time.time()
        total_time = round((end_time - start_time) * 1000, 2)  # in milliseconds

        # The entire response (headers + body)
        raw_output = result.stdout + result.stderr

        # Initialize output variables
        headers = ''
        content = ''
        status_code = None
        json_output = ''

        # Split headers and content if the output contains HTTP/1.1 or HTTP/2
        if 'HTTP/' in result.stdout:
            split_output = result.stdout.split('\r\n\r\n', 1)
            headers = split_output[0] if len(split_output) > 0 else ''
            content = split_output[1] if len(split_output) > 1 else ''

            # Extract status code from headers
            status_match = re.search(r'HTTP\/\d+\.\d+ (\d+)', headers)
            if status_match:
                status_code = int(status_match.group(1))

            # Try to extract JSON from the content if possible
            if content.startswith('{') or content.startswith('['):
                json_output = content

        # Construct status message with status code
        status_message = f"OK ({status_code})" if status_code and 200 <= status_code < 400 else f"ERROR ({status_code})"

        return jsonify({
            "status": status_message,
            "content": content.strip(),
            "headers": headers.strip(),
            "raw_output": raw_output.strip(),
            "json_output": json_output,
            "timings": f"{total_time} ms",
            "error": result.stderr.strip(),
            "status_code": status_code,
            "return_code": result.returncode
        })
    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "message": str(e)
        })

if __name__ == '__main__':
    # Use the PORT environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
