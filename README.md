in and out boilerplate
======================

When multiple target API needs to be accessed and you wants to keep track of what is called, this template leverage Caddy to write all calls to a single file.

This also count as a FastAPI template and supervisord sample ini file and helps access self-signed internal API if the API client don't like this and don't give a way to bypass (yes, i am talking about you, OpenAI client).

This helps building demos and demonstrating the various calls, like for a AI Agent pipeline.
