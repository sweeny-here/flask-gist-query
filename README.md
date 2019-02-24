# flask-gist-query
Python Flask web app that queries a Github user's Gists.

# Homage
Mr flybd5 created the inspriation for this project as found here - https://github.com/flybd5/gistquery

# What it does
The web app queries a Github's user's public Gists. If the user exists it pulls back the public Gists. If the user's Gists have already been queried, it reports this fact, else it reports that new Gists have been published and displays the updated data set in Json format. The app run's in SSL mode using certs created using Let's Encrypt. The App has been tested with an AWS ALB running out of an ECS cluster, and it required the fix -

```
from werkzeug.contrib.fixers import ProxyFix
...
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
...
```

In order to get the X-Forward headers to work, thus SSL end to end encryption to work.

# Future work
1. Extend the app to run on a more rubust server other than Flask.
2. Tie the app into a database so the query records are permanently stored, rather than to the local disk.
3. Automate Let's Encrypt renewal process.

# Get it going

Prerequisites -

Python3.6+ required.

To run locally -

pip install -r requirements.txt

Create SSL certs -

If running on Mac.

```
brew install certbot
```

The following command works if you have access to your domains DNS servers.

```
sudo certbot certonly --manual --cert-name <cert-id> -d <domain-name> -d <wildcard-domain-name> --preferred-challenges dns-01 --email <email> --server https://acme-v02.api.letsencrypt.org/directory --agree-tos
```

Edit your local hosts file adding entry for your SSL certs to work.

127.0.0.1      <domain-name>

Now run the app

cd flask-gits-query/
python3 web-app.py

Then you should see output similar to

```
* Serving Flask app "web-app" (lazy loading)
* Environment: production
WARNING: Do not use the development server in a production environment.
Use a production WSGI server instead.
* Debug mode: off
* Running on https://0.0.0.0:5000/ (Press CTRL+C to quit)
```

Test server health
https://ssl-certs-domain-name:5000/health

Submit a gist request
https://ssl-certs-domain-name:5000/get-gists

Gist request response
https://ssl-certs-domain-name:5000/process-gists


Build Docker Image

cd flask-gits-query/

docker build --no-cache -t sweeny-here/flask-app:v1.0 .

Run the docker image

docker run -it --name flask-app -p 443:5000 --privileged sweeny-here/flask-app:v1.0 .

Now you can test without the port number 5000 in the URL.

Test server health
https://ssl-certs-domain-name/health

Submit a gist request
https://ssl-certs-domain-name/get-gists

Gist request response
https://ssl-certs-domain-name/process-gists

Now push to your ECR of choice and deploy as a container.

# Gotcha's

If running in AWS using Cloudformation, the Flask port number 5000 was set in the AWS::ECS::TaskDefinition PortMappings ContainerPort field and also in AWS::ECS::Service LoadBalancers ContainerPort field. All other SSL fields / protocols / ports  were set to 443 and HTTPS or 80 and HTTP. NB - according to Let's Encrypt its best practice to keep HTTP traffic enabled. I'd be interested in your opinion on this point.

Happy coding!
