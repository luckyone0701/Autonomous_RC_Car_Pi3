import threading, speech_recognition as sr
listener_thread, listening = None, False

def listen_loop(socketio):
    global listening
    recognizer, mic = sr.Recognizer(), sr.Microphone()
    with mic as src: recognizer.adjust_for_ambient_noise(src)
    commands = ["forward","backward","stop","left","right","autonomous on","autonomous off"]
    while listening:
        with mic as src:
            print("🎤 Listening...")
            audio = recognizer.listen(src, timeout=5, phrase_time_limit=4)
        try:
            text = recognizer.recognize_sphinx(audio).lower()
            print("Heard:", text)
            for cmd in commands:
                if cmd in text:
                    socketio.emit('voice_command', cmd)
                    break
        except: pass

def start_voice_listener(socketio):
    global listener_thread, listening
    listening = True
    listener_thread = threading.Thread(target=listen_loop, args=(socketio,), daemon=True)
    listener_thread.start()

def stop_voice_listener():
    global listening
    listening = False
