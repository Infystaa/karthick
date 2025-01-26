from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)

# AWS credentials and bucket details
AWS_ACCESS_KEY = 'Your-Access-Key'
AWS_SECRET_KEY = 'Your-Secret-Key'
AWS_REGION = 'ap-south-1'
BUCKET_NAME = 'infy-s3-bucket'

# S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

@app.route('/')
def index():
    return '''
    <!doctype html>
    <title>Upload File</title>
    <h1>Upload File to AWS S3</h1>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        <input type="file" name="file"><br><br>
        <button type="submit">Upload</button>
    </form>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    try:
        # Upload file to S3
        s3.upload_fileobj(
            file,
            BUCKET_NAME,
            file.filename
        )
        
        # Construct the file URL
        file_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file.filename}"
        return jsonify({'message': 'File uploaded successfully', 'file_url': file_url}), 200

    except NoCredentialsError:
        return jsonify({'error': 'AWS credentials not available'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
