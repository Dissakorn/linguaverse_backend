from flask import Flask, request, jsonify
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pymongo import MongoClient
from dotenv import load_dotenv

app = Flask(__name__)

@app.route('/upload-photo', methods=['POST'])
def upload_photo():
    file = request.files['file']
    if file:
        load_dotenv()
        filename = file.filename
        temp_path = os.path.join('temp', filename)
        file.save(temp_path)
        
        # Upload to Google Drive
        file_url = upload_to_drive(temp_path, os.getenv('FOLDER_ID'))

        # Save the file URL to MongoDB
        save_url_to_mongo(file_url)

        return jsonify({'message': 'Photo uploaded successfully!', 'file_url': file_url}), 200
    return jsonify({'error': 'No file uploaded!'}), 400

load_dotenv()
creds = None
PATH = os.getenv('PATH_ID')
creds = service_account.Credentials.from_service_account_file(
    PATH,
    scopes=['https://www.googleapis.com/auth/drive']
)
# Build the drive service
drive_service = build('drive', 'v3', credentials=creds)

def upload_to_drive(file_path, folder_id):
    load_dotenv()
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [os.getenv('FOLDER_ID')]
    }
    media = MediaFileUpload(file_path, mimetype='image/jpeg')
    request = drive_service.files().create(
        media_body=media,
        body=file_metadata,
        fields='id'
    )
    file = request.execute()
    file_id = file.get('id')
    print(f'File ID: {file_id}')
    file_url = f'https://drive.google.com/file/d/{file_id}/view'
    print(f'File URL: {file_url}')
    return file_url

def save_url_to_mongo(file_url):
    load_dotenv()
    client = MongoClient(os.getenv('MONGO_URI'))
    db = client['lingua']
    collection = db['photo']
    doc = {
        'file_url': file_url
    }
    collection.insert_one(doc)
    client.close()

if __name__ == '__main__':
    load_dotenv()
    if not os.path.exists('temp'):
        os.makedirs('temp')
    # Path to the file you want to upload
    file_path = r'./temp/photo.png'
    folder_id = os.getenv('FOLDER_ID')
    
    file_url = upload_to_drive(file_path, folder_id)  # Upload photo to Google Drive
    save_url_to_mongo(file_url)  # Save the file URL to MongoDB

    app.run(host='0.0.0.0', port=5000, debug=True)
