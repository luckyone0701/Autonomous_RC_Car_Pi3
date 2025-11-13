import os, json, threading, time
from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
import RPi.GPIO as GPIO
from picamera2 import Picamera2
import serial
from voice_thread import start_voice_listener, stop_voice_listener

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

GPIO.setmode(GPIO.BCM)
motor_forward, motor_backward, servo_pin = 17, 27, 19
ENA, ENB = 18, 25
GPIO.setup([motor_forward, motor_backward, servo_pin, ENA, ENB], GPIO.OUT)
servo = GPIO.PWM(servo_pin, 50)
servo.start(7.5)

camera = Picamera2()
camera.configure(camera.create_video_configuration(main={"size": (1280, 720)}))
camera.start()

try:
    gps = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
except:
    gps = None

current_mode, voice_enabled = "manual", False
current_position = {"lat": 0, "lon": 0}

@app.route('/')
def index():
    return render_template('index.html', mode=current_mode)

def gen_frames():
    while True:
        frame = camera.capture_array()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('control')
def handle_control(data):
    d = data['direction']
    GPIO.output(motor_forward, d == "forward")
    GPIO.output(motor_backward, d == "backward")

@socketio.on('steer')
def handle_steer(data):
    duty = 2.5 + (float(data['angle']) / 18)
    servo.ChangeDutyCycle(duty)

@socketio.on('toggle_mode')
def toggle_mode():
    global current_mode
    current_mode = "auto" if current_mode == "manual" else "manual"
    emit('mode_update', current_mode, broadcast=True)

@socketio.on('toggle_voice')
def toggle_voice():
    global voice_enabled
    voice_enabled = not voice_enabled
    if voice_enabled: start_voice_listener(socketio)
    else: stop_voice_listener()
    emit('voice_update', voice_enabled, broadcast=True)

def gps_thread():
    global current_position
    while True:
        if gps:
            line = gps.readline().decode(errors='ignore')
            if line.startswith("$GPGGA"):
                parts = line.split(",")
                if len(parts) > 5:
                    current_position = {"lat": float(parts[2])/100, "lon": float(parts[4])/100}
                    socketio.emit('gps_update', current_position)
        time.sleep(1)

threading.Thread(target=gps_thread, daemon=True).start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
