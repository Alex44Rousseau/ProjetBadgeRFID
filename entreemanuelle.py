import mysql.connector
import datetime

def log_entry_exit_manual(employee_id):
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
        cursor.execute('''
            INSERT INTO attendance (employee_id, entry_time)
            VALUES (%s, %s)
        ''', (employee_id, entry_time))

    conn.commit()

if __name__ == "__main__":
    # Connexion à la base de données MySQL
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='apagnan',
        database='RFID'
    )
    cursor = conn.cursor()

    try:
        # Saisie manuelle de l'identifiant de l'employé
        employee_id_manual = input("Entrez l'identifiant de l'employé : ")
        log_entry_exit_manual(employee_id_manual)
        print("Entrée manuelle enregistrée avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement de l'entrée manuelle : {e}")
    finally:
        conn.close()
