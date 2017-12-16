# orion-server

## What is Orion?

Orion is a (mostly) drop-in replacement for the server-side [OwnTracks Recorder](https://github.com/owntracks/recorder) for clients reporting locations via HTTP. Orion recognizes and respects the [client JSON payload format](http://owntracks.org/booklet/tech/json/) shipped by the OwnTracks Android client.

But why? The official OwnTracks Recorder is needlessly complicated and difficult to set up. For simple and straightforward deployments where clients report location with periodic HTTP requests, all the server needs to do is parse that client payload and persist it somewhere in a database. That's what this project is for.

What about the name? I'm not really sure, I just needed a name to create a repository. There's probably something to be said about constellations and stars and how stars are related to your location, or something.
