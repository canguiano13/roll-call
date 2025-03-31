# UPDATE 04/01/24 - Carlos:

## Prerequisites
This branch switches our connection paradigm from UNIX Sockets to Cloud SQL Connectors. This requires an addtional package. Make sure to install the Connectors package and any others you might be missing. Again, recommended is to do this in a virtual environment:

`pip install -r requirements.txt`

## ORM with models.py
One of the things that we can do with flask-sqlalchemy is define
models. Models allow us to create object-relational mappings between our code and the sql instance, adding a layer of abstraction when we go to query data within the app. 

This makes interacting with the database much simpler, since we can operate on them like we would any other Object. For example, if we wanted to query the database for the user with id 1, we can run:

   `User.query.filter_by(user_id="1")`

and it will handle some of the behind the scenes stuff like opening/closing the db connection. More info about models below: 

-https://flask-sqlalchemy.readthedocs.io/en/stable/models/

-https://medium.com/@shivamkhandelwal555/a-proper-way-of-declaring-models-in-flask-9ce0bb0e42c1

## Reaching the SQL instance with connectors instead of sockets
One of the bigger challenges this branch addresses is getting the app connected to the Cloud SQL instance so that we can start querying to/from the database. One of the things that I discovered was that the default SQLAlchemy Engine has some compatibility issues with Cloud SQL Connectors since Connectors use IAM-based authentication. Luckily the default engine settings can be changed. (see app.py)

Since Cloud SQl requires IAM-authentication, I had to create a service account in the cloud console that sort of acts as a proxy account for logging into the instance and reading/writing. Since our engine uses this service account to login, we need the account credentials as well as the file path to the credentials to be specified when the container is built. That's what `sqldevcredentials.json` is for. The service account is called `SQLDEV`

## Separating the routes with routes.py
One thing that I also implemented was a separate file that will hold all of our routes. This should remove some of the clutter from app.py, especially if we're also going to be including user management and/or any other flask extensions.

The way that we separate the routes is to define a Flask "Blueprint." Blueprints define how to construct or extend an application, but aren't apps themselves. See more info here: 

https://flask.palletsprojects.com/en/stable/blueprints/

Using blueprints, we can define our routes in a separate file, then render them when the app starts up with `app.register_blueprints(routes)`

The one downside to this is that in our frontend we have to specify that we're using a route when doing redirection. For example, instead of using...

`url_for('index')`

...to get to the homepage, we have to modify that to...

`url_for('routes.index')`
