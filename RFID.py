import mysql.connector
from mfrc522 import SimpleMFRC522
import datetime
import time

# Connexion à la base de données MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='apagnan',
    database='RFID'
)
cursor = conn.cursor()

# Création de la table pour stocker les entrées et sorties avec la durée entre l'entrée et la sortie
cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id BIGINT NOT NULL,
    entry_time DATETIME NOT NULL,
    exit_time DATETIME,
    duration_minutes INT,
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
    );
''')
conn.commit()

reader = SimpleMFRC522()

def log_entry_exit(employee_id):
    current_time = datetime.datetime.now()
    entry_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    # Récupérer la dernière entrée pour cet employé
    cursor.execute('''
        SELECT id, entry_time
        FROM attendance
        WHERE employee_id = %s AND exit_time IS NULL
        ORDER BY entry_time DESC
        LIMIT 1
    ''', (employee_id,))
    
    last_entry = cursor.fetchone()

    if last_entry:
        entry_id, last_entry_time = last_entry
        exit_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        duration_minutes = (current_time - last_entry_time).total_seconds() / 60.0

        # Mise à jour de la sortie et de la durée pour la dernière entrée
        cursor.execute('''
            UPDATE attendance
            SET exit_time = %s, duration_minutes = %s
            WHERE id = %s
        ''', (exit_time, duration_minutes, entry_id))
    else:
        # Nouvelle entrée
        cursor.execute('''
            INSERT INTO attendance (employee_id, entry_time)
            VALUES (%s, %s)
        ''', (employee_id, entry_time))

    conn.commit()

try:
    last_read_time = time.time()

    while True:
        current_time = time.time()
        elapsed_time = current_time - last_read_time

        # Délai entre les lectures pour éviter les lectures trop fréquentes
        if elapsed_time > 1:
            print("Approchez votre badge RFID...")
            employee_id, _ = reader.read()
            print("Ne pas faire attention au message ci-dessus, tout marche \n :)")
            log_entry_exit(employee_id)

            # Mettez à jour le temps de la dernière lecture
            last_read_time = time.time()

except KeyboardInterrupt:
    conn.close()
    GPIO.cleanup()
