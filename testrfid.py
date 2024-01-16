import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
    print("Attente du badge RFID...")
    while True:
        # Attendez jusqu'à ce qu'un badge RFID soit détecté
        id, text = reader.read()
        print("Badge détecté avec l'ID :", id)
        print("Contenu du badge :", text)

except KeyboardInterrupt:
    # Le programme se termine proprement lorsqu'on utilise Ctrl+C
    GPIO.cleanup()
    print("Programme terminé.")
