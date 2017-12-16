# orion-server

## What is Orion?

Orion is a (mostly) drop-in replacement for the server-side [OwnTracks Recorder](https://github.com/owntracks/recorder) for clients reporting locations via HTTP. Orion recognizes and respects the [client JSON payload format](http://owntracks.org/booklet/tech/json/) shipped by the OwnTracks Android client.

But why? The official OwnTracks Recorder is needlessly complicated and difficult to set up. For simple and straightforward deployments where clients report location with periodic HTTP requests, all the server needs to do is parse that client payload and persist it somewhere in a database. That's what this project is for.

What about the name? I'm not really sure, I just needed a name to create a repository. There's probably something to be said about constellations and stars and how stars are related to your location, or something.

## Features

The scope of responsibility of Orion is deliberately very limited. Orion exposes a handler to save HTTP location reports from the Android OwnTracks client to a database. That's it.

Note that **an authentication mechanism is deliberately excluded from Orion itself**. Since the OwnTracks client authenticates requests with a simple Basic `Authorization` HTTP header, Orion delegates the responsibility of user authentication to your web server. This means that by the time a request reaches the Orion service itself, Orion assumes the request has already been authenticated, and will persist the data to a database exactly as-is.

Orion does *not* support or respect other types of requests, and has no support for MQTT.

## Installation and configuration

You'll need a WSGI-friendly web server, Python, pip, the `virtualenv` package, and a SQLAlchemy-friendly database. The instructions below assume locally-hosted MySQL and Apache.

Create a database for location events:

```sql
CREATE USER 'orion'@'localhost' IDENTIFIED BY 'super-secret-password';
CREATE DATABASE orion;
GRANT ALL ON orion.* TO 'orion'@'localhost';
FLUSH PRIVILEGES;
```

Create a configuration file `/etc/orion/config.json` of the following shape:

```js
{
  "database": {
    "host": "localhost",
    "name": "orion",
    "user": "orion",
    "password": "super-secret-password"
  }
}
```

Get the source code:

```bash
# Pull source code
$ git clone git@git.kevinlin.info:personal/orion-server.git
$ cd orion-server
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
    ServerName ...

    WSGIScriptAlias / /path/to/orion-server/orion.wsgi

    <Directory /path/to/orion-server>
        Require all granted
    </Directory>

    # Handle user authentication at the web server level
    # This is important; otherwise Orion will allow any user
    <Location /api>
        AuthType basic
        AuthName "Orion"
        AuthBasicProvider file
        AuthUserFile /etc/apache2/.htpasswd
        Require user ...
    </Location>
</VirtualHost>
```

## Client configuration

Assuming the above virtual host configuration, the Android OwnTracks client application can be configured as follows:

1. Set the mode to `Private HTTP`
2. Set the host to `http://<your server name>/api/publish`
3. Enable authentication with the username/password respected in `/etc/apache2/.htpasswd`
4. Set the device ID (required) and tracker ID (optional)
