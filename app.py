from flask import Flask, request, jsonify
import subprocess
import time
import os

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
        
        # Start the timing for the request
        start_time = time.time()
        
        # Execute the curl command using subprocess
        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
        
        # Calculate the timing
        end_time = time.time()
        total_time = round((end_time - start_time) * 1000, 2)  # in milliseconds
        
        # Split the output to headers and content if possible
        headers = ''
        content = result.stdout
        raw_output = result.stdout + result.stderr
        json_output = ''
        
        try:
            json_output = result.stdout if result.stdout.startswith('{') or result.stdout.startswith('[') else ''
        except Exception as e:
            json_output = ''
        
        # Simulate headers section for a more detailed output (if curl is run with -i)
        if 'HTTP/' in result.stdout:
            headers, content = result.stdout.split('\r\n\r\n', 1)

        return jsonify({
            "status": "OK" if result.returncode == 0 else "ERROR",
            "content": content,
            "headers": headers,
            "raw_output": raw_output,
            "json_output": json_output,
            "timings": f"{total_time} ms",
            "error": result.stderr,
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
