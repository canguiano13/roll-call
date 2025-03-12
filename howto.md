### Outline and Prerequisites
Open up VSCode and a new terminal. I'll use this branch to show how we can get a containerized flask app running as a service in Google Cloud. First, I'll describe the flask app, then we'll build a local container using docker. 
Once that's working, I'll show you how I got it uploaded and serving requests on the cloud. If something isn't working for you or you have questions just lmk. -Carlos

Some prerequisites are needed. I'll assume a Windows environment:
    Python. I'm running 3.12.9: https://www.python.org/downloads/release/python-3129/
    Docker for Desktop: https://www.docker.com/get-started/
    Google Cloud CLI: https://cloud.google.com/sdk/docs/install

You'll also want to install any dependencies if you haven't already. Recommended is to do this in a virtual environment: 
    `pip install flask`

### Running the flask app locally
First, we'll start with our flask app. I built a very simple flask app. 
One page is static, one is generated dynamically, and one renders an HTML template.

One way to run the app would just be to use `python app.py`. The other is with `python -m flask run`.
From what I can tell the latter appears to be slightly preferable due to customizability/flexibility. See https://www.restack.io/p/flask-run-vs-python-app for more info.

When you run the app with `python -m flask run`, you'll see a message saying that it's serving traffic on localhost. Then if you go to http://localhost:5000/test, we'll see flask loading one of the pages we specified. We could also specify the port we want to listen on using `python -m flask run --port 8080`, in which case we instead want to go to http://localhost:8080/test.

### Using the Dockerfile to build the container locally 
Next up is to get it containeried locally. When we build a container, Docker will use a Dockerfile to specify how we want the container image to be created. The container image is "a lightweight, standalone, executable package of software that includes everything needed to run an application: code, runtime, system tools, system libraries and settings." If we had multiple containers in our service, we could create a `compose.yaml` file to help specify containers, volumes, ports, etc, but that's not necessary yet. 

First thing is to start with the Dockerfile. We get a lot of freedom for what features we have and how we want the container to set it up. If you take a look at the Dockerfile in this folder you'll see environment variables, downloading dependencies/requirements, and running commands. Refer to https://docs.docker.com/go/dockerfile-reference/ for more on Dockerfiles.

Once the Dockerfile is done, we can build the container using `docker build -t {image-name} .` where
`-t {image-name} ` tells docker what we want the image to be named, and
`.` means the Dockerfile is in our current directory. If it was in another folder, we specify the path here.

Luckily our container is pretty lightweight, so the platform doesn't have too much effect on what CPU arch we're using, but if we had another app and the cloud used a different CPU architecture than the development machine (e.g., you are on a s M1 and your cloud provider is amd64), you'll want to build the image for that platform, e.g.: `docker build --platform=linux/amd64 -t myapp .`.

Now that the image is built, we need to start the container. If you run `docker images` in your terminal, you should see a list of container images. We'll start up the one we just with `docker run -p 8080:8080 {image-name}`. Once the container is running, you should be able to connect to our flask app by going to http://localhost:8080.

One thing to note: The `-p` flag is super necessary. It binds port 8080 on our host machine to port 8080 inside the container. If we were just to execute `docker run {image-name}`, we'd be met with a `localhost refused to connect` error when we try to go to the site.

Once the container is running locally, you'll see that traffic is being served, and you can open the flask pages in your web browser by going to http://localhost:8080 or http://localhost:8080/hello/world or http://localhost:8080/test. Press CTRL+C in your terminal to stop it.

The goal now is to get this container image uploaded to Google Cloud Run.

### Deploying to Google Cloud Run
Before we can get the container image uploaded to the artifact registry, we need to make sure we have the Google Cloud CLI installed. Then, once you install it, run `gcloud init` in your terminal to connect to our project. It will ask you to sign in and add some configuration details

When it asks for a project, ours is the one that starts with 'halogen'.
When it asks if you want a default Compute Region and Zone, put `y`. I used zone 11, but any `us-west` should be fine.

Now we can deploy directly to the cloud with `gcloud run deploy --source .`

Once the CLI is connected, we can get our container running on the app. One choice is to build the image to our artifact registry, then create a new service with it on the console. The other is to build it directly to Google Cloud Run. Since this is just a test, we'll do the second one and worry about getting the artifact built later.

Try running `gcloud run deploy --source .`. It will ask for some configuration details:
--Service name is not important. Just make sure to clean up after.
--Again, any `us-west` zone should be fine. I chose 39.
--Make sure to allow unauthenticated invocations to the service (`y`)

Google Cloud Run will start building the container/service. If you did everything right, then at the bottom you should see a message that says something like `"Done. Service [{service-name}] revision [{service-name-revision}] has been deployed and is serving 100 percent of traffic."`

Go to the service link provided at the bottom and see if it's serving traffic! After you're done, be sure to clean up the artifact from the registry to avoid incurring extra charges. Go to https://console.cloud.google.com/run?project=halogen-sol-452703-b5 > click the checkbox next to the service > "Delete" > "Yes."

I think a good next goal is to get a container running in GCR that can interact with our Cloud SQL instance.

### Deploying to GCR cont...
Started working on a  `build-and-deploy.sh` script file that should eventually allow us to expedite the steps above ^ once we decide database enginge. 

## app.py - 03/11/2025 - Container running in GCR connected to Cloud SQL instance. 
Inserted functions to initialize a database and connect to our CLOUDSQL instance. 
- variables are read from a `.env` file where they are defined. 