source venv/bin/activate
echo -e "yes" | python manage.py collectstatic
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo nginx -t
sudo systemctl restart nginx
deactivate
