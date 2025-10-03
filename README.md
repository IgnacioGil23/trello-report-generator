# 📊 TrelloAuto - Generador de Reportes de Trello

Una aplicación de escritorio desarrollada en Python que permite generar reportes automáticos detallados de tableros de Trello, incluyendo análisis de tiempos, movimientos de tarjetas y productividad del equipo.

![TrelloAuto](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen.svg)

## 🚀 Configuración inicial

### 1. Crear y activar entorno virtual (RECOMENDADO)
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
.\venv\Scripts\Activate.ps1

# O si tienes problemas con PowerShell:
.\venv\Scripts\activate.bat
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar credenciales de Trello

1. Ve a https://trello.com/app-key para obtener tu API Key
2. En esa misma página, genera un Token
3. Copia el archivo `.env.example` como `.env`
4. Completa las variables con tus datos reales

### 4. Obtener el ID del tablero

Puedes obtener el ID del tablero de varias formas:

**Opción 1: Desde la URL**
Si tu tablero es `https://trello.com/b/ABC123/mi-tablero`, el ID es `ABC123`

**Opción 2: Desde la API**
```bash
curl "https://api.trello.com/1/members/me/boards?key=TU_API_KEY&token=TU_TOKEN"
```

## 📊 Tipos de reportes disponibles

### 1️⃣ **Reporte Detallado**
- Historial completo de cada cliente
- Fechas de entrada y salida de cada etapa
- Tiempo permanecido en cada etapa
- **Ideal para:** Análisis detallado de casos específicos

### 2️⃣ **Reporte de Tiempos**
- Tiempo promedio, mínimo y máximo por etapa
- Cantidad de casos analizados por etapa
- **Ideal para:** Optimización de procesos y identificación de cuellos de botella

### 3️⃣ **Reporte de Movimientos**
- Flujo de clientes entre etapas
- Cantidad de movimientos por cada transición
- **Ideal para:** Entender el flujo del proceso y patrones de movimiento

### 4️⃣ **Reporte de Estado Actual**
- Ubicación actual de cada cliente
- Resumen de clientes por etapa
- **Ideal para:** Vista panorámica del estado actual del negocio

### 5️⃣ **Reporte por Período**
- Actividad filtrada por rango de fechas
- Permite análisis de períodos específicos
- **Ideal para:** Análisis de rendimiento mensual/trimestral

### 6️⃣ **Reporte de Velocidad**
- Clientes más rápidos y lentos en el proceso
- Tiempo total por cliente
- **Ideal para:** Identificar casos que requieren atención

### 7️⃣ **Reporte Completo**
- Todos los análisis anteriores en un solo archivo Excel
- Múltiples hojas con diferentes perspectivas
- **Ideal para:** Análisis exhaustivo y presentaciones ejecutivas

## 📊 Ejecutar el reporte

```bash
# Asegúrate de que el entorno virtual esté activado
.\venv\Scripts\Activate.ps1

# Ejecutar el programa
python reporte_trello.py
```

## 📋 Qué hace el programa

El programa ofrece **7 tipos diferentes de análisis**:

1. **Conecta con Trello** usando tu API Key y Token
2. **Obtiene las listas** (etapas del proceso) del tablero
3. **Obtiene las tarjetas** (clientes) del tablero  
4. **Rastrea el historial** de movimientos de cada tarjeta
5. **Presenta un menú interactivo** para seleccionar el tipo de análisis
6. **Genera reportes especializados** según tu elección
7. **Guarda archivos Excel** con nombres únicos y timestamp

## 📈 Ejemplos de uso

### 🏢 **Para Gerentes de Proyecto:**
- Usa el **Reporte de Tiempos** para identificar etapas lentas
- Usa el **Reporte de Estado Actual** para reuniones de seguimiento

### 📊 **Para Analistas de Datos:**
- Usa el **Reporte Completo** para análisis exhaustivos
- Usa el **Reporte de Movimientos** para mapear flujos de proceso

### 👥 **Para Atención al Cliente:**
- Usa el **Reporte de Velocidad** para identificar casos urgentes
- Usa el **Reporte por Período** para análisis mensuales

## � Estructura de los reportes

### **Reporte Detallado:**
- **Cliente**: Nombre de la tarjeta
- **Etapa**: Nombre de la lista/etapa
- **Fecha de entrada**: Cuándo entró a esa etapa
- **Fecha de salida**: Cuándo salió de esa etapa (si aplicable)
- **Tiempo en etapa**: Días que permaneció en esa etapa

### **Reporte de Tiempos:**
- **Etapa**: Nombre de la etapa
- **Promedio**: Tiempo promedio en días
- **Mínimo/Máximo**: Rangos de tiempo
- **Total casos**: Cantidad de casos analizados

### **Reporte de Movimientos:**
- **De**: Etapa origen
- **A**: Etapa destino  
- **Cantidad de movimientos**: Frecuencia de esa transición

### **Y más tipos según tu selección...**

## 🔧 Solución de problemas

- **Error de credenciales**: Verifica que tu `.env` esté configurado correctamente
- **Error de tablero**: Asegúrate de que el BOARD_ID sea correcto
- **Sin datos**: Verifica que tengas tarjetas en el tablero y permisos de acceso
- **Reportes vacíos**: Algunos reportes requieren historial de movimientos entre etapas
- **Errores de fechas**: El programa maneja automáticamente formatos de fecha inconsistentes

## 🆕 **Características nuevas**

✅ **Menú interactivo** - Selecciona fácilmente el tipo de reporte  
✅ **Múltiples análisis** - 7 tipos diferentes de reportes  
✅ **Filtros por fecha** - Analiza períodos específicos  
✅ **Archivos organizados** - Nombres únicos con timestamp  
✅ **Análisis de velocidad** - Identifica clientes rápidos/lentos  
✅ **Reportes combinados** - Múltiples hojas en un archivo Excel  
✅ **Interfaz amigable** - Emojis y mensajes claros  

## 🎯 **Próximas mejoras sugeridas**

- 📊 Gráficos automáticos en Excel
- 📧 Envío automático por email  
- 🔄 Programación automática de reportes
- 📱 Notificaciones push
- 🎨 Dashboard web interactivo