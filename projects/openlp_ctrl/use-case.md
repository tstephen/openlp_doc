Ok, proof of concept works:

1. start magic mediation server
2. load slides on stream machine, connects automatically to mediation server
3. load slides on projection machine, also connects to mediation server (different client id)
4. click next slide on projection machine,
  a. sends message to mediation server,
  b. which forwards on to all registered clients,
  c. which in turn navigate to the specified slide.

The beauty of this is that _either_ slide machine can be in charge.
When the projection machine is told to navigate to the slide it's already on it just does nothing.

Or the other option is to hack the OpenLP remote to connect to the mediation server.

The mediation server is very dumb and has no sensitive knowledge so can be hardened to put on the internet.
