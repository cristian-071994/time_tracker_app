"""
Aplicación para el seguimiento y registro de tiempo de actividades laborales.
Permite registrar inicio y fin de jornada, actividades y consultar historial.
"""
import sqlite3
import datetime
import os


class TimeTracker:
    """Clase para gestionar el seguimiento de tiempo de actividades laborales."""

    def __init__(self):
        """Inicializa la aplicación de seguimiento de tiempo"""
        # Crear la base de datos si no existe
        self.db_file = "time_tracker.db"
        self.connection = None
        self.cursor = None
        self.working_day_id = None
        self.current_activity_id = None

        # Conectar a la base de datos
        self.connect_db()

        # Crear tablas si no existen
        self.create_tables()

    def connect_db(self):
        """Conecta a la base de datos SQLite"""
        self.connection = sqlite3.connect(self.db_file)
        self.cursor = self.connection.cursor()

    def create_tables(self):
        """Crea las tablas necesarias si no existen"""
        # Tabla para días laborales
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS working_days (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT NOT NULL,
            end_time TEXT,
            total_duration INTEGER
        )
        ''')

        # Tabla para actividades
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            working_day_id INTEGER,
            description TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            duration INTEGER,
            FOREIGN KEY (working_day_id) REFERENCES working_days (id)
        )
        ''')

        self.connection.commit()

    def start_working_day(self):
        """Registra el inicio de un día laboral"""
        # Verificar si ya hay un día laboral activo
        if self.working_day_id is not None:
            print(
                "Ya tienes un día laboral activo. Finalízalo antes de iniciar uno nuevo.")
            return

        # Registrar inicio del día laboral
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO working_days (start_time) VALUES (?)",
            (start_time,)
        )
        self.connection.commit()

        # Obtener el ID del día laboral actual
        self.working_day_id = self.cursor.lastrowid

        print(f"Día laboral iniciado a las {start_time}")

    def start_activity(self, description):
        """Inicia una nueva actividad"""
        # Verificar si hay un día laboral activo
        if self.working_day_id is None:
            print("No hay un día laboral activo. Inicia tu día laboral primero.")
            return

        # Verificar si hay una actividad activa
        if self.current_activity_id is not None:
            print(
                "Ya tienes una actividad en curso. Finalízala antes de iniciar una nueva.")
            return

        # Registrar inicio de la actividad
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO activities (working_day_id, description, start_time) VALUES (?, ?, ?)",
            (self.working_day_id, description, start_time)
        )
        self.connection.commit()

        # Obtener el ID de la actividad actual
        self.current_activity_id = self.cursor.lastrowid

        print(f"Actividad '{description}' iniciada a las {start_time}")

    def end_activity(self):
        """Finaliza la actividad en curso"""
        # Verificar si hay una actividad activa
        if self.current_activity_id is None:
            print("No hay una actividad en curso que finalizar.")
            return

        # Obtener la hora de inicio de la actividad
        self.cursor.execute(
            "SELECT start_time FROM activities WHERE id = ?",
            (self.current_activity_id,)
        )
        start_time_str = self.cursor.fetchone()[0]
        start_time = datetime.datetime.strptime(
            start_time_str, "%Y-%m-%d %H:%M:%S")

        # Registrar fin de la actividad
        end_time = datetime.datetime.now()
        end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

        # Calcular duración en segundos
        duration = int((end_time - start_time).total_seconds())

        # Actualizar la actividad en la base de datos
        self.cursor.execute(
            "UPDATE activities SET end_time = ?, duration = ? WHERE id = ?",
            (end_time_str, duration, self.current_activity_id)
        )
        self.connection.commit()

        # Mostrar información de la actividad finalizada
        self.cursor.execute(
            "SELECT description FROM activities WHERE id = ?", (self.current_activity_id,))
        description = self.cursor.fetchone()[0]
        duration_str = self.format_duration(duration)
        print(f"Actividad '{description}' finalizada a las {end_time_str}")
        print(f"Duración: {duration_str}")

        # Limpiar el ID de la actividad actual
        self.current_activity_id = None

    def end_working_day(self):
        """Finaliza el día laboral actual"""
        # Verificar si hay un día laboral activo
        if self.working_day_id is None:
            print("No hay un día laboral activo que finalizar.")
            return

        # Verificar si hay una actividad activa
        if self.current_activity_id is not None:
            print(
                "Tienes una actividad en curso. Finalízala antes de terminar el día laboral.")
            return

        # Obtener la hora de inicio del día laboral
        self.cursor.execute(
            "SELECT start_time FROM working_days WHERE id = ?",
            (self.working_day_id,)
        )
        start_time_str = self.cursor.fetchone()[0]
        start_time = datetime.datetime.strptime(
            start_time_str, "%Y-%m-%d %H:%M:%S")

        # Registrar fin del día laboral
        end_time = datetime.datetime.now()
        end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

        # Calcular duración total del día en segundos
        total_duration = int((end_time - start_time).total_seconds())

        # Actualizar el día laboral en la base de datos
        self.cursor.execute(
            "UPDATE working_days SET end_time = ?, total_duration = ? WHERE id = ?",
            (end_time_str, total_duration, self.working_day_id)
        )
        self.connection.commit()

        # Mostrar resumen del día
        duration_str = self.format_duration(total_duration)
        print(f"Día laboral finalizado a las {end_time_str}")
        print(f"Duración total del día: {duration_str}")

        # Mostrar resumen de actividades
        self.cursor.execute(
            "SELECT description, duration FROM activities WHERE working_day_id = ?",
            (self.working_day_id,)
        )
        activities = self.cursor.fetchall()

        if activities:
            print("\nResumen de actividades:")
            for desc, dur in activities:
                dur_str = self.format_duration(dur)
                print(f"- {desc}: {dur_str}")

        # Limpiar el ID del día laboral actual
        self.working_day_id = None

    def view_history(self, days=7):
        """Muestra el historial de días laborales y actividades"""
        # Obtener los últimos días laborales
        self.cursor.execute(
            """
    SELECT id, start_time, end_time, total_duration
    FROM working_days
    ORDER BY start_time DESC
    LIMIT ?
    """,
            (days,)
        )
        working_days = self.cursor.fetchall()

        if not working_days:
            print("No hay historial de días laborales para mostrar.")
            return

        print(f"\n=== Historial de los últimos {days} días laborales ===")

        for day_id, start, end, duration in working_days:
            day_date = datetime.datetime.strptime(
                start, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")

            # Verificar si el día se completó
            if end is None:
                status = "EN CURSO"
                duration_str = "N/A"
            else:
                status = "COMPLETADO"
                duration_str = self.format_duration(duration)

            print(f"\nFecha: {day_date} - {status}")
            print(f"Inicio: {start} - Fin: {end or 'En curso'}")
            print(f"Duración total: {duration_str}")

            # Obtener actividades de ese día
            self.cursor.execute(
                """
                SELECT description, start_time, end_time, duration 
                FROM activities 
                WHERE working_day_id = ? 
                ORDER BY start_time
                """,
                (day_id,)
            )
            activities = self.cursor.fetchall()

            if activities:
                print("Actividades:")
                for i, (desc, act_start, act_end, act_dur) in enumerate(activities, 1):
                    if act_end is None:
                        act_status = "EN CURSO"
                        act_dur_str = "N/A"
                    else:
                        act_status = "COMPLETADA"
                        act_dur_str = self.format_duration(act_dur)

                    print(f"  {i}. {desc} - {act_status}")
                    print(
                        f"     Inicio: {act_start} - Fin: {act_end or 'En curso'}")
                    print(f"     Duración: {act_dur_str}")
            else:
                print("No hay actividades registradas para este día.")

    def format_duration(self, seconds):
        """Formatea la duración en segundos a formato hh:mm:ss"""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.connection:
            self.connection.close()


def clear_screen():
    """Limpia la pantalla de la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """Función principal del programa"""
    tracker = TimeTracker()

    try:
        while True:
            clear_screen()
            print("\n=== REGISTRO DE TIEMPO LABORAL ===")
            print("\nEstado actual:")

            if tracker.working_day_id is None:
                print("- No hay día laboral activo")
            else:
                print("- Día laboral activo")

            if tracker.current_activity_id is None:
                print("- No hay actividad en curso")
            else:
                # Obtener descripción de la actividad actual
                tracker.cursor.execute(
                    "SELECT description, start_time FROM activities WHERE id = ?",
                    (tracker.current_activity_id,)
                )
                desc, start = tracker.cursor.fetchone()
                print(f"- Actividad en curso: '{desc}' (iniciada: {start})")

            print("\nOpciones:")
            print("1. Iniciar día laboral")
            print("2. Iniciar nueva actividad")
            print("3. Finalizar actividad actual")
            print("4. Finalizar día laboral")
            print("5. Ver historial")
            print("6. Salir")

            choice = input("\nElige una opción (1-6): ")

            if choice == '1':
                tracker.start_working_day()
                input("\nPresiona Enter para continuar...")

            elif choice == '2':
                if tracker.working_day_id is None:
                    print("Primero debes iniciar un día laboral.")
                else:
                    description = input("Describe la actividad: ")
                    tracker.start_activity(description)
                input("\nPresiona Enter para continuar...")

            elif choice == '3':
                tracker.end_activity()
                input("\nPresiona Enter para continuar...")

            elif choice == '4':
                tracker.end_working_day()
                input("\nPresiona Enter para continuar...")

            elif choice == '5':
                days = input("¿Cuántos días quieres ver? (Enter para 7): ")
                days = int(days) if days.isdigit() else 7
                tracker.view_history(days)
                input("\nPresiona Enter para continuar...")

            elif choice == '6':
                break

            else:
                print("Opción no válida. Intenta nuevamente.")
                input("\nPresiona Enter para continuar...")

    finally:
        # Asegurar que la conexión a la base de datos se cierre al salir
        tracker.close()
        print("\nPrograma finalizado.")


if __name__ == "__main__":
    main()
