# syntax=docker/dockerfile:1
# Dockerfile reference guide at https://docs.docker.com/go/dockerfile-reference/

# First specify the python version. 
#3.12 seems to work fine. Slim version will help save some resources
ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim as base

# working directory for our app. defines where the rest of our commmnds will take effect.
WORKDIR /app

# copy the requirements file we made to the container. we'll install these in a sec 
COPY requirements.txt requirements.txt

# install all dependencies using the requirements file we just copied.
RUN pip install -r requirements.txt

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# store filepath to service account database credentials in the environment
ENV GOOGLE_APPLICATION_CREDENTIALS="./sqldevcredentials.json"

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 8080

# Run the application 
#--host specifies the IP address(es) to listen on. 
#--port will specify the port to listen on for incoming connections
CMD ["python", "-m" , "flask", "run", "--host=0.0.0.0", "--port", "8080"]
