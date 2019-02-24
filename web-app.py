from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from werkzeug.contrib.fixers import ProxyFix
import requests
import json
import os
from datetime import datetime
import ssl

# Main app
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = 'aqwertyuiop1234567890'
app.env = "production"

# Display input form
@app.route('/')
def rootPath():
    return redirect ('/get-gists',code=301)

@app.route('/get-gists')
def getGists():
   return render_template('input-form.html')

# Process input form data
@app.route('/process-gists',methods = ['POST', 'GET'])
def processGists():
   if request.method == 'POST':
      a_username = request.form['username']
      # print("Debug username : '" + a_username + "'")

      gists_reponse = getGists(a_username)
      # print("Debug gists_reponse : '" + str(gists_reponse) + "'")

      r_username = gists_reponse[0]
      r_message = gists_reponse[1]

      if len(gists_reponse) == 4:
          r_status = gists_reponse[2]
          r_data = gists_reponse[3]
          return render_template("output-form.html", r_username = r_username, r_message = r_message, r_status = r_status, r_data = r_data)
      else:
          return render_template("output-form.html", r_username = r_username, r_message = r_message)
   else:
       return redirect ('/get-gists',code=301)

# Get the user's gists
def getGists(a_username):
    gist_headers = {'Accept': 'application/vnd.github.v3+json'}
    gist_url = 'http://api.github.com/users/' + a_username + '/gists'
    gist_request = requests.get(gist_url,headers=gist_headers)

    if gist_request.status_code != 200:
        if gist_request.status_code == 404:
            a_message = 'Error: User not found.'
            return (a_username, a_message)

    a_gist = json.loads(gist_request.content)

    if not a_gist:
        a_message = 'User has no public gists.'
        return (a_username, a_message)
    else:
        a_message = ('User has public gists.')
        a_status = getStatus(a_username, a_gist)
        return (a_username, a_message, a_status, a_gist)

# Query status, not prevouisly queried, previously queried and no updates or
# previously queried and has updates
def getStatus(a_username, a_gist):
    configPath = '/tmp/gistquery.' + a_username
    if not os.path.isfile(configPath):
        print('Github user "' + a_username +
            '" gists have not been previously queried.')
        print('Creating checkpoint file: ' + configPath)
        try:
            configFile = open(configPath, 'w')
            configFile.write(a_gist[0]['created_at'])
            configFile.close()
            return ("Gists have not been previously queried.")
        except Exception as e:
            raise
    else:
        try:
            configFile = open(configPath,'r+')
            stringDate = configFile.read()
        except Exception as e:
            raise
        lastCreateDate = datetime.strptime(stringDate,'%Y-%m-%dT%H:%M:%SZ')
        currentLastCreateDate = datetime.strptime(a_gist[0]['created_at'],
            '%Y-%m-%dT%H:%M:%SZ')
        if currentLastCreateDate > lastCreateDate:
            print('Github user "' + a_username +
                '" created a new public gist since the last query.')
            try:
                configFile.seek(0,0)
                configFile.write(a_gist[0]['created_at'])
                a_status = "Gists have been previously queried and a new public gist has been created since last query."
            except Exception as e:
                raise
        else:
            print('Github user "' + a_username +
                '" has not created a new public gist since the last query.')
            a_status = "Gists have been previously queried and no new public gist has been created since last query."
        configFile.close()
        return (a_status)

@app.route("/health")
def health():
    return ('Status Up', 200)

# Used to prettify Json in Jinja2 template
def prettyJson(value):
    return json.dumps(value, sort_keys=True,
                      indent=4, separators=(',', ': '))

app.jinja_env.filters['prettyJson'] = prettyJson

# Set SSL
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain('ssl-certs/fullchain1.pem', 'ssl-certs/privkey1.pem')

if __name__ == '__main__':
   app.run(host='0.0.0.0', ssl_context=context, port=5000, threaded=True)
