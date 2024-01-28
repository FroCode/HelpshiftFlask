from flask import Flask, request, render_template_string , render_template
import requests
import mimetypes
import base64
import datetime

app = Flask(__name__)

# Constants
DOMAIN = "frocode"
API_KEY = "frocode_api_20240126210826327-28837e54048524c"

# HTML Template
HTML = '''<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Form Submission</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #333;
            color: #fff;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        .form-container {
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            color: #333;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
        }

        .form-group input[type="text"],
        .form-group input[type="file"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }

        .submit-btn {
            background-color: #007bff;
            color: #fff;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s;
        }

        .submit-btn:hover {
            background-color: #0056b3;
        }
        h1 {
            text-align: center;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="form-container">
        <form action="/submit" method="post" enctype="multipart/form-data">
            <h1>HelpShift</h1>
            <h4>Replay to an Issue </h4>
            <div class="form-group">
                <label for="issue_id">Issue ID:</label>
                <input type="text" id="issue_id" name="issue_id" required>
            </div>
            <div class="form-group">
                <label for="message_body">Message Body:</label>
                <input type="text" id="message_body" name="message_body" required>
            </div>
            <div class="form-group">
                <label for="file">Attachment:</label>
                <input type="file" id="file" name="file" required>
            </div>
            <button type="submit" class="submit-btn">Submit</button>
        </form>
        <form action="/fetch-issues" method="post">
    <h4>Fetch Issues</h4>
    <div class="form-group">
        <label for="query">Query (optional):</label>
        <input type="text" id="query" name="query">
    </div>
    <button type="submit" class="submit-btn">Fetch Issues</button>
</form>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

def construct_attachment_object(file):
    filename = file.filename
    file_type = mimetypes.guess_type(filename)[0]
    return {"attachment": (filename, file.stream, file_type)}

@app.route('/submit', methods=['POST'])
def submit():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    issue_id = request.form['issue_id']
    message_body = request.form['message_body']
    api_endpoint = f"https://api.helpshift.com/v1/{DOMAIN}/issues/{issue_id}/messages"

    attachment_object = construct_attachment_object(file)
    payload = {"message-body": message_body, "message-type": "Text"}

    response = requests.post(api_endpoint,
                             auth=(API_KEY, ""),
                             data=payload,
                             files=attachment_object)

    # Check if the request was successful
    if response.status_code in [200, 201]:
        return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="refresh" content="5;url=/" />
            <title>Submission Successful</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #333;
                    color: white;
                    text-align: center;
                    padding-top: 20%;
                }
            </style>
        </head>
        <body>
            <h2>Message sent successfully✅<h2>
            <p>You will be redirected in 5 seconds...</p>
        </body>
        </html>
        '''
        # ... [your existing code for handling unsuccessful submission]
    else:
        return ''' <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="refresh" content="5;url=/" />
            <title>Error</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #333;
                    color: white;
                    text-align: center;
                    padding-top: 20%;
                }
            </style>
        </head>
        <body>
            <h2>Message failed to send ❌</h2>
            <p>Please try again.</p>
            <p>Failed to send message.</p>
        </body>
        </html>'''
         


@app.route('/fetch-issues', methods=['POST'])
def fetch_issues():
    DOMAIN = "frocode"  # Replace with your domain
    api_endpoint = f"https://api.helpshift.com/v1/{DOMAIN}/issues"

    headers = {
        'Accept': 'application/json',
        'Authorization': 'Basic ZnJvY29kZV9hcGlfMjAyNDAxMjAyMjMwMzUxMzYtNzcxOGQxYTRiMmE5OWY4'
    }

    response = requests.get(api_endpoint, headers=headers)

    if response.status_code == 200:
        data = response.json()
        issues = data.get('issues', [])

        # Preprocess the titles
        for issue in issues:
            issue['title'] = issue.get('title', '').title()
            assignee_name = issue.get('assignee_name', '')
            

        return render_template('issue-tracker/index.html', issues=issues)
    else:
        return f"Error fetching issues: Status Code {response.status_code}, Response: {response.text}", 400

if __name__ == '__main__':
    app.run(debug=True)

