import mysql.connector
from mfrc522 import SimpleMFRC522
import datetime
import time

conn = mysql.connector.connect(
    host='localhost',
    user='votre_utilisateur_mysql',
    password='votre_mot_de_passe_mysql',
    database='votre_base_de_donnees'
)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        employee_id VARCHAR(255) NOT NULL,
        entry_time DATETIME NOT NULL,
        exit_time DATETIME,
        duration_minutes INT
    )
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

        if elapsed_time > 1:
            print("Approchez votre badge RFID...")
            employee_id, _ = reader.read()
            log_entry_exit(employee_id)

            last_read_time = time.time()

except KeyboardInterrupt:
    conn.close()
    GPIO.cleanup()
