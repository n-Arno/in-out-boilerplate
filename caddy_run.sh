#!/bin/bash

set -a
source .env
set +a

caddy run --config ./Caddyfile
