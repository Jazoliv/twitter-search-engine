# Tweet Indexer & Search Engine
Sistema de indexación, almacenamiento y búsqueda de publicaciones escrito en Python. Desarrollado como proyecto académico para la **Universidad de Buenos Aires (UBA)**.

El sistema implementa un motor de búsqueda en memoria con tokenización avanzada y persistencia local de datos.

## 🚀 Funcionalidades Principales

* **Indexación y Búsqueda Eficiente:** Procesa y tokeniza texto por palabras clave y n-gramas (segmentos) para realizar búsquedas por intersección.
* **Normalización de Texto:** Limpieza de caracteres especiales, tildes y conversión a minúsculas para mejorar la precisión de coincidencia.
* **Persistencia de Datos:** Módulo de persistencia local en disco para mantener el índice e historial de IDs sin pérdida de datos al reiniciar.
* **Importación y Exportación Masiva:** Procesamiento de archivos `.txt` individuales o carpetas enteras para carga masiva de tweets.
* **Gestión Integrada:** Interfaz por consola interactiva que permite crear, buscar, eliminar e importar/exportar registros en tiempo real.

## 🛠️ Tecnologías y Conceptos Aplicados

* **Lenguaje:** Python 3
* **Estructuras de Datos:** Hash Maps (Diccionarios) e Inverted Index (Sets para búsqueda eficiente)
* **Conceptos:** Tokenización de texto, N-gramas, Manejo de Archivos (I/O), Normalización de datos

## ⚙️ Requisitos e Instalación

Para poder iniciar el programa debe existir en el directorio raíz (misma carpeta donde está el ejecutable) una subcarpeta llamada `db/`, donde se almacenan y leen los archivos de texto de los tweets.

1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/Jazoliv/tp3.git](https://github.com/Jazoliv/tp3.git)
