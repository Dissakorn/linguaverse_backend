from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/upload-photo', methods=['POST'])
def upload_photo():
    file = request.files['file']
    if file:
        filename = file.filename
        file.save(os.path.join('temp', filename))
        return jsonify({'message': 'Photo uploaded successfully!'}), 200
    return jsonify({'error': 'No file uploaded!'}), 400

if __name__ == '__main__':
    if not os.path.exists('temp'):
        os.makedirs('temp')
    app.run(host='0.0.0.0', port=5000)
