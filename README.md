# Time Tracker App

Una aplicación de línea de comandos para registrar el tiempo dedicado a distintas actividades laborales.

## Características

- Registro de inicio y fin de jornada laboral
- Seguimiento de actividades individuales
- Cálculo automático de duración de actividades
- Consulta de historial de actividades
- Almacenamiento en base de datos SQLite

## Requisitos

- Python 3.x

## Instalación

1. Clona este repositorio:
```
git clone https://github.com/tu-usuario/time-tracker-app.git
cd time-tracker-app
```

2. No requiere dependencias adicionales, solo Python estándar.

## Uso

Ejecuta la aplicación:
```
python time_tracker.py
```

### Flujo típico:

1. Inicia tu día laboral
2. Registra actividades a medida que las realizas
3. Finaliza cada actividad al terminarla
4. Al final del día, cierra tu jornada laboral
5. Consulta el historial cuando lo necesites

## Estructura del proyecto

- `time_tracker.py`: Archivo principal de la aplicación
- `time_tracker.db`: Base de datos SQLite (se crea automáticamente)