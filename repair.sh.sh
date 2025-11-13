##!/bin/bash
echo "🔧 Repairing setup..."
sudo raspi-config nonint do_camera 0
sudo systemctl enable rc_car.service
sudo systemctl restart rc_car.service
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl status rc_car.service | head -n 10
