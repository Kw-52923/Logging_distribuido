# Sistema de Logging Centralizado

Sistema web para recolectar y consultar logs de múltiples servicios usando Flask y SQLite.

## 🚀 Características

- **API RESTful** para recibir y consultar logs
- **Autenticación por tokens** para múltiples servicios
- **Base de datos SQLite** para almacenamiento persistente
- **Filtros de búsqueda** por fecha, servicio y severidad
- **Simulador de servicios** incluido para pruebas

## 📋 Requisitos

- Python 3.7+
- Flask
- requests

```bash
pip install flask requests
```

## 🛠️ Instalación

1. Clona el repositorio
2. Instala las dependencias
3. Ejecuta el servidor:

```bash
python app.py
```

El servidor estará disponible en `http://localhost:5000`

## 📡 Endpoints

### POST `/logs`
Envía logs al sistema.

**Headers:**
```
Authorization: Token servicio1_token123
Content-Type: application/json
```

**Body:**
```json
{
  "logs": [
    {
      "timestamp": "2024-01-15T10:30:00",
      "service": "auth-service",
      "severity": "INFO",
      "message": "Inicio de sesión exitoso"
    }
  ]
}
```

### GET `/logs`
Consulta logs con filtros opcionales.

**Parámetros de consulta:**
- `timestamp_start` / `timestamp_end`: Filtrar por fecha del evento
- `received_at_start` / `received_at_end`: Filtrar por fecha de recepción
- `service`: Filtrar por servicio
- `severity`: Filtrar por nivel (INFO, DEBUG, WARNING, ERROR, CRITICAL)

**Ejemplo:**
```
GET /logs?service=auth-service&severity=ERROR
```

## 🧪 Pruebas

### Simulador individual
```bash
python servicio1.py 0  # Simula auth-service
python servicio1.py 1  # Simula payment-service
```

### Múltiples servicios
```bash
python multiple_servicio.py
```

## 🔑 Tokens Válidos

- `servicio1_token123`
- `servicio2_token456`
- `servicio3_token789`

## 📊 Estructura de la Base de Datos

```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    service TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    received_at TEXT NOT NULL
);
```

## 🔍 Ejemplo de Respuesta

```json
{
  "logs": [
    {
      "id": 1,
      "timestamp": "2024-01-15T10:30:00",
      "service": "auth-service",
      "severity": "INFO",
      "message": "Inicio de sesión exitoso",
      "received_at": "2024-01-15T10:30:15.123456"
    }
  ],
  "count": 1
}
```
