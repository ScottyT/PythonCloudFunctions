from flask import Flask, escape, jsonify, send_file
from methods import create_excel, list_items
from google.cloud import storage
from google.oauth2 import service_account
from authlib.jose import jwt

import functions_framework
import os


@functions_framework.http
def download_excel(request):
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Content-Disposition, Accept, Authorization',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)
    
    headers = {
        'Access-Control-Allow-Origin': 'https://code-red-app-313517.web.app, https://staging-174a0.web.app',
        'Access-Control-Allow-Methods': 'GET, POST'
    }
    request_json = request.get_json()
    file_name = request_json["filename"]
    
    path = create_excel(request_json)
    return (send_file(path, as_attachment=True, download_name=file_name), 200, headers)

@functions_framework.http
def create_folder(request):
    white_origin = ['http://localhost:3000', 'https://code-red-app-313517.web.app', 'https://staging-174a0.web.app']
    if request.method == 'OPTIONS' and request.headers['Origin'] in white_origin:
        headers = {
            'Access-Control-Allow-Origin': request.headers['Origin'],
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Content-Disposition, Accept, Authorization',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    headers = {
        'Access-Control-Allow-Origin': request.headers['Origin'],
        'Access-Control-Allow-Methods': 'GET, POST'
    }

    request_json = request.get_json()
    folder_path = request_json["folderPath"]
    is_root = request_json["root"]
    delimiter = request_json["delimiter"]
    storage_bucket = request_json["storageBucket"]
    auth = request.headers['Authorization'].split(" ")[1]
    pemFilePath = os.path.join(os.getcwd(), 'code-red-app.pem')

    try:
        with open(pemFilePath, 'rb') as f:
            key = f.read()
    except:
        return ("Can't find certificate file.", 400, headers)
    
    claims = jwt.decode(auth, key)
    if claims.validate() is not None:
        return ('You are not Authorized to post to this endpoint.', 401, headers)
    cred_path = os.path.join(os.getcwd(), 'code-red.json')
    cred = service_account.Credentials.from_service_account_file(cred_path)
    client = storage.Client(credentials=cred)
    try:
        bucket = client.get_bucket(storage_bucket)
    except:
        return ("Sorry, that bucket doesn't exist!", 404)
    
    blob = bucket.blob(folder_path + "/")
    if is_root:
        folder_path = ""
    blob.upload_from_string('', content_type='application/x-www-form-urlencoded;charset=UTF-8')
    data = list_items(client, storage_bucket, folder_path, delimiter)

    resp = {'message': 'Successfully created folder!', 'data': data}
    return (resp, 200, headers)