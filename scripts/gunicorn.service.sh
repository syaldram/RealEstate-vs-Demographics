#  /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon for serve flask application...
After=network.target
[Service]
User=ubuntu
Group=nginx
WorkingDirectory=/home/ubuntu/flask-application/app
ExecStart=/home/ubuntu/flask-application/app/.venv/bin/gunicorn -b localhost:8000 app:app                                                  
Restart=always
[Install]
WantedBy=multi-user.target



getent group nginx
sudo groupadd nginx
sudo usermod -aG nginx ubuntu
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl status gunicorn

/var/log/nginx/error.log

#Note to self, change the user to ubuntu on /etc/nginx/nginx.conf 