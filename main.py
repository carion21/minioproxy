from flask import Flask, request, Response
from dotenv import load_dotenv
import requests
import time
import os

load_dotenv()

app = Flask(__name__)


@app.route('/hello')
def index():
    return 'Hello, World!'


@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def catch_all(path):
    print('='*50)
    query_string = request.query_string.decode('utf-8')
    complete_path = f'{path}?{query_string}' if query_string else path
    url = f'{os.getenv("HOST")}/{complete_path}'

    print(f'complete_path: {complete_path}')
    print('-'*50)

    start = time.time()

    response = requests.request(
        method=request.method,
        url=url,
        headers={key: value for key,
                 value in request.headers if key.lower() != 'host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )

    end = time.time()
    print(f'{url} - {response.status_code} - {end-start} seconds')

    # Détection du type de fichier
    content_type = response.headers.get('Content-Type', '')
    filename = path.split("/")[-1]

    # Forcer le bon type MIME si Excel ou PDF
    if filename.endswith('.xlsx'):
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif filename.endswith('.pdf'):
        content_type = 'application/pdf'

    # Forcer Content-Disposition si fichier à télécharger
    force_download = filename.endswith('.xlsx') or filename.endswith('.pdf')
    headers = {
        'Content-Type': content_type
    }

    if force_download:
        headers['Content-Disposition'] = f'attachment; filename="{filename}"'

    return Response(
        response.content,
        status=response.status_code,
        headers=headers
    )


if __name__ == '__main__':
    port = int(os.getenv('PORT'))
    app.run(host='0.0.0.0', port=port, debug=True)
