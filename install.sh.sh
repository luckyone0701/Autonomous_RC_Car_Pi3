#!/bin/bash
echo "Installing Autonomous RC Car..."
sudo apt update
sudo apt install -y python3-pip python3-venv flac pulseaudio
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
sudo raspi-config nonint do_camera 0
sudo cp rc_car.service /etc/systemd/system/
sudo systemctl enable rc_car.service
sudo systemctl start rc_car.service
echo "✅ Installation complete. Access via http://<pi-ip>:5000"
