![Orion](https://static.kevinlin.info/blog/orion/banner.png)

# orion-server

[![Build Status](https://travis-ci.org/LINKIWI/orion-server.svg?branch=master)](https://travis-ci.org/LINKIWI/orion-server)
[![Coverage Status](https://coveralls.io/repos/github/LINKIWI/orion-server/badge.svg?branch=master)](https://coveralls.io/github/LINKIWI/orion-server?branch=master)

## What is Orion?

Orion is a (mostly) drop-in replacement for [OwnTracks Recorder](https://github.com/owntracks/recorder) for clients reporting locations via HTTP. Orion recognizes and respects the [client JSON payload format](http://owntracks.org/booklet/tech/json/) shipped by the OwnTracks Android client.

**But why?** The official OwnTracks Recorder is, in my opinion, needlessly complicated and difficult to set up. For simple and straightforward deployments where clients report location with periodic HTTP requests, all the server needs to do is parse that client payload and persist it somewhere in a database. That's what this project is for.

`orion-server` pairs nicely with [`orion-web`](https://github.com/LINKIWI/orion-web), a frontend visualization tool for the web similar to that supplied by the official OwnTracks recorder. Deploying the web interface alongside the server is of course optional if you don't need it.

Why "Orion"? I'm not really sure. There's probably something to be said about constellations and stars and how stars are related to your location, or something.

## Features

The scope of responsibility of Orion is deliberately very limited. Orion exposes a handler to save HTTP location reports from the Android OwnTracks client to a database. It also provides an opt-in feature to reverse geocode GPS coordinates into formatted addresses, which are persisted to the database.

Note that **an authentication mechanism is deliberately excluded from Orion itself**. Since the OwnTracks client authenticates requests with a simple Basic `Authorization` HTTP header, Orion delegates the responsibility of user authentication to your web server. This means that by the time a request reaches the Orion service itself, Orion assumes the request has already been authenticated, and will persist the data to a database exactly as-is.

Orion does *not* support or respect other types of requests, and has no support for MQTT.

## Configuration

You have the option of supplying all necessary configuration variables in a JSON file, passed as environment variables to the server process, or some combination thereof. *Note that the value of an environment variable will override the value specified in the JSON config file in the event of a conflict.*

By default, Orion will look for a config file at `/etc/orion/config.json`. You can override this by passing environment variable `ORION_CONFIG=/path/to/config.json`.

Orion respects the following configuration parameters (note that some are required to be defined before starting the server):

|JSON config file key|Equivalent environment variable|Required?|Description|Example|
|-|-|-|-|-|
|`database.host`|`DATABASE_HOST`|Yes|Hostname of the MySQL database used for storage.|`localhost`|
|`database.port`|`DATABASE_PORT`|Yes|Port of the MySQL database used for storage.|`3306`|
|`database.name`|`DATABASE_NAME`|Yes|Name of the MySQL database used for storage.|`orion`|
|`database.user`|`DATABASE_USER`|Yes|Username of the MySQL user.|`orion`|
|`database.password`|`DATABASE_PASSWORD`|Yes|Password of the MySQL user.|`super-secret-password`|
|`frontend_url`|`FRONTEND_URL`|No|The fully-qualified base URL of the [`orion-web`](https://github.com/LINKIWI/orion-web) frontend interface. Used for settings CORS headers. You should omit this configuration parameter if (1) you're not using `orion-web`, *or* (2) `orion-web` is deployed to the same base URL as `orion-server`.|`http://orion.example.com`|
|`google_api_key`|`GOOGLE_API_KEY`|No|Google Maps API key, used for reverse geocoding. If supplied, Orion will attempt to reverse geocode all incoming GPS coordinates; if omitted, Orion will skip reverse geocoding.|`AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`|

An example valid `config.json` might look something like this:

```js
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "name": "orion",
    "user": "orion",
    "password": "super-secret-password"
  },
  "frontend_url": "http://orion.example.com",
  "google_api_key": "AIzaxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

## Installation

You'll need a WSGI-friendly web server, Python, pip, the `virtualenv` package, and a SQLAlchemy-friendly database. The instructions below assume locally-hosted MySQL and Apache.

Create a database for location events:

```sql
CREATE USER 'orion'@'localhost' IDENTIFIED BY 'super-secret-password';
CREATE DATABASE orion;
GRANT ALL ON orion.* TO 'orion'@'localhost';
FLUSH PRIVILEGES;
```

Get the source code and bootstrap the application. 

Note that the virtual environment is located in a folder `env` 
inside the repository root.

```bash
$ git clone https://github.com/LINKIWI/orion-server.git
$ cd orion-server
# Install system dependencies
$ sudo apt-get install libmysqlclient-dev python-dev
# Install Python dependencies
$ virtualenv env
$ source env/bin/activate
$ make bootstrap
# Create the initial database tables
$ make init-db
```

Add an Apache virtual host:

```apache
<VirtualHost *:80>
    ServerName orion.example.com

    WSGIScriptAlias / /path/to/orion-server/orion.wsgi

    <Directory /path/to/orion-server>
        Require all granted
    </Directory>

    # Handle user authentication at the web server level
    # This is important; otherwise Orion will allow any user to publish location events
    <Location /api/publish>
        AuthType basic
        AuthName "Orion"
        AuthBasicProvider file
        AuthUserFile /etc/apache2/.htpasswd
        Require user ...
    </Location>
</VirtualHost>
```

If you are interested in enabling reverse geocoding of all GPS coordinates sent by mobile clients, [create a Google Maps API key](https://developers.google.com/maps/documentation/geocoding/start#get-a-key), and ensure it is properly set in the configuration options. This will automatically enable reverse geocoding.

## Client configuration

Assuming the above virtual host configuration, the Android OwnTracks client application can be configured as follows:

1. Set the mode to `Private HTTP`
2. Set the host to `http://orion.example.com/api/publish`
3. Enable authentication with the username/password respected in `/etc/apache2/.htpasswd`
4. Set the device ID (required) and tracker ID (optional)

## FAQ

#### iOS support

iOS ships a JSON payload that is more or less of the same shape as that of the Android client, so it should be compatible without any additional action.

#### Support for other OwnTracks features

The only feature I use is periodic background location reporting, so adding support to Orion to respect payloads sent by other features is not a high priority, but may be investigated in the future.

#### Support for MQTT

Sorry, this is not planned. To keep the server simple and friendly for small-scale deployments, only HTTP is supported.

#### Docker

It is *highly recommended* to follow the above instructions for installing Orion manually. However, you can try [`orion-docker`](https://github.com/LINKIWI/orion-docker) for a "one-click" Docker deployment solution, though stability is not guaranteed.
