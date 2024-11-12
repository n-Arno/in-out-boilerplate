all: run

install:
	apt-get update && apt-get install debian-keyring debian-archive-keyring apt-transport-https curl -y
	curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
	curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' > /etc/apt/sources.list.d/caddy-stable.list
	apt-get update && apt-get install caddy python3-pip -y
	python3 -m pip install --break-system-packages -r requirements.txt
	caddy add-package github.com/caddyserver/transform-encoder

run:
	supervisord -c ./supervisord.ini -s -l ./logs/supervisord.log 

kill:
	- pkill supervisord

clean:
	- rm -rf __pycache__ ./logs/*.log server.pem
