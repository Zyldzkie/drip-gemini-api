from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/personalize', methods=['POST'])
def personalize():
    data = request.get_json()
    prompt = data.get('prompt')
    
    # Perform your personalization logic here
    response_data = {
        'status': 'success',
        'prompt_received': prompt,
        'message': f'Personalized content for prompt: {prompt}'
    }

    print(prompt)

    return jsonify(response_data)



if __name__ == '__main__':
    # Expose the API on all network interfaces (0.0.0.0) and a specific port (e.g., 5000)
    app.run(host='0.0.0.0', port=5000, debug=True)
