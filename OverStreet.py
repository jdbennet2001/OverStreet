'''
Main File, Web UI for validating ML code 
'''

import io

from flask import Flask, render_template, send_from_directory, send_file, request

from web.web_app import comic, update_model
from lib.comic import extract_cover
from urllib.parse import unquote


# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='/static')

app.debug = True

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/cover/<cover>")
def get_cover(cover):
    location = unquote(unquote(cover)) 
    print(f'Serving file {location}')
    try:
        image_data = extract_cover(location)
        return send_file(io.BytesIO(image_data), mimetype='image/jpg')
    except Exception as e:
        print( f'Exception serving cover: {e}')
        filename = 'static/blank-cover.jpg'
        return send_file(filename, mimetype='image/jpg')

@app.route("/file/<cover>")
def get_file(cover):
    location = unquote(unquote(cover)) 
    print(f'Serving file {location}')
    try:
        return send_file(location, mimetype='image/jpg')
    except Exception as e:
        print( f'Exception serving cover: {e}')
        filename = 'static/blank-cover.jpg'
        return send_file(filename, mimetype='image/jpg')

# Return data about the next comic to be processed
@app.route('/comic/<offset>')
def get_next(offset):
    issue = comic(int(offset))
    return issue

@app.route('/classify', methods=['POST'])
def classify():
    content = request.get_json(silent=True)
    print(f'Classify event: {content}')
    update_model(content)
    return {'response' : 200}

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)