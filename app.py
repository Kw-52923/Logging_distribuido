""" Flask framework para crear aplicaciones web, request Para recibir información que nos envían,jsonify  Para enviar respuestas en formato JSON  """
from flask import Flask, request,jsonify
from datetime import datetime # Para trabajar con fechas y horas
import sqlite3
#import json # para manejar datos en formato JSON 

app = Flask(__name__) # Crea instancia de la app Flask.Es como decir "voy a empezar a construir mi aplicación web""

# Toquens validos para autenticar servicios que envian logs
VALID_TOKENS = {
    "servicio1_token123",
    "servicio2_token456",
    "servicio3_token789"
}
DB_NAME = "logging.db" # Guarda el nombre de la BD

# Configuracion de la BD 
def init_database():
    """Inicializa la BD y crea la tabla si no existe"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    service TEXT NOT NULL,
    severity  TEXT NOT NULL,
    message  TEXT NOT NULL,
    received_at  TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def validacion_token (auth_header):
    """Valida el token de autenticacion"""
    if not auth_header or not auth_header.startswith('Token'): # startswith -> comprueba que la cadena de texto comience con TOKEN
        return False
    token = auth_header[6:] # Da la cadena desde el caracter 6 en adelante
    return token in VALID_TOKENS

def save_log_to_db(log_data):
    """GUARDA UN LOG EN LA BD"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(''' 
    INSERT INTO logs (timestamp, service, severity, message, received_at)
    VALUES (?,?,?,?,?)
    ''', (
        log_data['timestamp'],
        log_data['service'],
        log_data['severity'],
        log_data['message'],
        datetime.now().isoformat() # Obtiene la hora y fecha actual en formato texto
    ))

    conn.commit()
    conn.close()

"""Funcion que busca logs aplicando filtros"""
def get_logs_from_db(filters):
    """Recupera logs de la base de datos con filtros opcionales"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    query = "SELECT * FROM logs WHERE 1=1" # Truco para qu siempre devuelva true
    params = [] # Usa parametros en la consulta para proteger el sistema contra inyecciones maliciosas
    
    # Aplicar filtros
    """Busca solo los logs que ocurrieron despues o en esa fecha"""
    if 'timestamp_start' in filters:
        query += " AND timestamp >= ?"
        params.append(filters['timestamp_start'])
    """Busca logs que ocurrieron antes o en esa fecha"""
    if 'timestamp_end' in filters:
        query += " AND timestamp <= ?"
        params.append(filters['timestamp_end'])
        """Filtra por la fecha en el que el servidor recibio el log, no cuando ocurrio"""
    if 'received_at_start' in filters:
        query += " AND received_at >= ?"
        params.append(filters['received_at_start'])
    """Filtra por la fecha en el que el servidor finalizó el log"""
    if 'received_at_end' in filters:
        query += " AND received_at <= ?"
        params.append(filters['received_at_end'])
    """Filtra por el nombre del servicio que genero el log (autenticacio,pagos,correos)"""
    if 'service' in filters:
        query += " AND service = ?"
        
        params.append(filters['service'])
    """Filtra por el nivel del log: INFO,ERROR,DEBUG"""
    if 'severity' in filters:
        query += " AND severity = ?"
        params.append(filters['severity'])#
    
    
    query += " ORDER BY received_at DESC"
    
    cursor.execute(query, params)
    logs = cursor.fetchall() # Recupera todas las filas
    
    conn.close()
    
    # Formatear resultados
    resultado = []
    for log in logs:
        resultado.append({
            # Posiciones de cada campo en la tupla que devuelve fetchall
            'id': log[0],
            'timestamp': log[1],
            'service': log[2],
            'severity': log[3],
            'message': log[4],
            'received_at': log[5]
        })
    
    return resultado
"""Define una ruta o endpoint en la web"""
@app.route('/logs', methods=['POST']) # Envia datos desde el cliente hacia el servidor

def receive_log():
    
    # Verificar autorizacion y rechaza si no es válida
    auth_header = request.headers.get('Authorization')
    if not validacion_token(auth_header):
        return jsonify({"error": "Quién sos, bro?"}), 401 # no estás autorizado porque la autenticación falló.
    
    # Obtiene los datos enviados en formato JSON
    data = request.get_json()
    if not data or 'logs' not in data:
        return jsonify({"error": "Formato inválido. Se espera {'logs': []}"}), 400 #la petición del cliente está mal formada.
    
    # Procesar cada log
    for log in data['logs']:
        # Validar campos requeridos
        required_fields = ['timestamp', 'service', 'severity', 'message']
        if not all(field in log for field in required_fields):
            continue  # Saltar log inválido
        
        # Guardar en base de datos
        save_log_to_db(log)
    
    return jsonify({"message": "Logs recibidos correctamente"}), 200

"""Otra ruta para el mismo URL pero en metodo GET(consultar logs)"""
@app.route('/logs', methods=['GET'])
 # Recoge los filtros desde la URL y los prepara
def get_logs():
    
    filters = {} # Prepara un diccionario vacio para los filtros
    
    # Recoger filtros de los parámetros de consulta

    if 'timestamp_start' in request.args:
        filters['timestamp_start'] = request.args['timestamp_start']
    
    if 'timestamp_end' in request.args:
        filters['timestamp_end'] = request.args['timestamp_end']
        
    if 'received_at_start' in request.args:
        filters['received_at_start'] = request.args['received_at_start']
        
    if 'received_at_end' in request.args:
        filters['received_at_end'] = request.args['received_at_end']
        
    if 'service' in request.args:
        filters['service'] = request.args['service']
        
    if 'severity' in request.args:
        filters['severity'] = request.args['severity']
    
    # Obtener logs
    logs = get_logs_from_db(filters)
    
    return jsonify({"logs": logs, "count": len(logs)}), 200

if __name__ == '__main__':
    init_database()
    app.run(debug=True, port=5000)# Puerto por defecto que usa flask