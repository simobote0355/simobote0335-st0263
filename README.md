﻿# simobote0335-st0263

## Estudiante
Simón Botero Villarraga - sboterov3@eafit.edu.co

## Profesor 
Edwin Nelson Montoya - emontoya@eafit.brightspace.com

# Red con Arquitectura P2P para transferencia de archivos

## 1. Breve descripción de la actividad 

Se realizó una red P2P descentralizado basado en la arquitectura DHT con topología de anillo, donde el anillo esta compuesto por nodos los cuales tiene microservicios.

**Requisitos del Sistema:** 
- Estructura de Red: Utiliza la arquitectura DHT tipo anillo para una red P2P estructurada.

- Nodos/Peers: Cada nodo (peer) consta de dos módulos, PServidor: Maneja la conexión con otros nodos y soporta concurrencia para múltiples conexiones simultáneas. PCliente: Permite al nodo interactuar con otros nodos de la red.

- Acceso al Servicio: Los peers se conectan a la red a través de un nodo inicial.

- Mantenimiento de la Red y Localización de Recursos: Usaservicios ECO o dummies para simular la carga y descarga de archivos.

- Comunicación entre Procesos: Implementa comunicación RPC utilizando middleware como API REST, gRPC y MOM.

- Recursos Compartidos: Cada peer comparte un índice de archivos disponibles en un directorio configurable durante el inicio del microservicio.

- Archivo de Configuración: Se define la IP, puerto de escucha y directorio de archivos.

### 1.1. Que aspectos cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)

- Se logró implementar una red P2P que soporta el manejo de archivos.
- Se usó el protocolo DHT.
- Se implementó la topología de anillo.
- Cada nodo cuenta con su microservicio.
- Mediante hilos, se pudo controlar la concurrencia. 

### 1.2. Que aspectos NO cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)

- No se logró el despligue de en AWS.
- No se logró la transferencia de archivos.
- No se logró ubicar los archivos de otros nodos que requeridos por otros nodos.

## 2. información general de diseño de alto nivel, arquitectura, patrones, mejores prácticas utilizadas.

### 2.1. Diseño de Alto Nivel

- Red de Nodos P2P: Cada nodo en la red está diseñado para conectarse con otros nodos y formar una red distribuida.
Los nodos se identifican y gestionan mediante un identificador hash que se calcula a partir de su dirección IP y puerto.

- Anillo de Nodos: La red está organizada en una estructura en anillo, donde cada nodo tiene un sucesor y un predecesor en el anillo. La Finger Table se utiliza para optimizar la búsqueda de nodos y gestionar el anillo de manera eficiente.

#### 2.2. Arquitectura

Nodos:

- **ID del Nodo:** Calculado usando una función hash (SHA-1) y mapeado a un espacio de identificadores de tamaño MAX_NODES.

- **Predecesor y Sucesor:** Cada nodo mantiene referencias a su predecesor y sucesor en el anillo, así como una Finger Table para la búsqueda rápida de nodos.

- **Configuración y Archivos:** Cada nodo tiene su propia carpeta para configuración y archivos, guardando la configuración del nodo en un archivo JSON.

  Comunicación:

- **Sockets:**    Los nodos se comunican entre sí mediante sockets TCP.
- **Protocolos de Mensajes:** Se utilizan diferentes tipos de mensajes para gestionar conexiones, solicitudes de búsqueda, y actualizaciones en el anillo.

Multihilo:

- **Escucha y Manejo de Conexiones:** Se utilizan hilos para manejar múltiples conexiones simultáneamente y escuchar nuevas conexiones en paralelo.

### 2.3. Patrones y Mejores Prácticas

- **Cliente-Servidor**: Cada nodo actúa como un servidor que escucha conexiones y como un cliente que puede conectarse a otros nodos.

- **Tablas de Hash Distribuidas (DHT)**: La red P2P utiliza una tabla hash distribuida para gestionar la localización de nodos y archivos.

- **Búsqueda y Actualización:** Los nodos buscan archivos en la red utilizando el ID del archivo y actualizan sus tablas de hash y estructuras de red según sea necesario.

- **Excepciones y Errores de Socket:** Se manejan errores de socket y otros errores potenciales para asegurar que el nodo pueda recuperarse de fallos en la red.
Persistencia de Configuración:

- **Archivos JSON:** La configuración del nodo se guarda en archivos JSON para persistencia y facilidad de lectura/escritura.

- **Concurrente:** Se utilizan hilos para manejar múltiples conexiones simultáneamente, permitiendo que el nodo gestione múltiples clientes y conexiones de pares en paralelo.

## 3. Descripción del ambiente de desarrollo y técnico: lenguaje de programación, librerias, paquetes, etc, con sus numeros de versiones.

### 3.1. Lenguaje de programación
Se realizo el proyecto en Python

### 3.2. Librerías

- socket: Comunicación de red.
- threading: Manejo de hilos para conexiones simultáneas.
- pickle: Serialización de datos.
- hashlib: Generación de hashes para identificadores.
- time
- json: Manejo de archivos JSON para configuración.
- os: Operaciones del sistema de archivos.
- collections

### 3.3. Compilación y ejeución

Primero,
```bash
python node.py 127.0.0.1 <puerto>
```

Segundo,    
```bash
python app_flask
```

Finalmente,    
```bash
python client.py
```

Para conectar los nodos de hace de siguiente manera. Suponga que tiene los nodos en los puertos 5000, 5001 y 5002, conecta el nodo el puerto 5002 al nodo del puerto 5001 y, este nodo del puerto 5001 al nodo del puerto 5000.

Para subir un archivo, este debe estar en la carpeta principal del proyecto. Para comprobar la descargar del archivo, primero subirlo a un nodo, luego, eliminar el archivo del carpe   ta principal y descarga el archivo mediante el cliente.

### 3.4. Detalles de desarrollo y técnicos

- **Cliente-Servidor:** Nodo como servidor y cliente.
- **Multihilo:** Conexiones simultáneas manejadas por hilos.
- **Red Distribuida:** Uso de tabla de dedos para localizar nodos.
- **Hashing:** Identificadores únicos para nodos y archivos.
- **Configuración:** Guarda configuración en JSON, crea directorios.
- **Comunicación:** Serialización y deserialización de datos.
- **Unión y Salida de la Red:** Actualiza predecesor y sucesor.
- **Búsqueda de Archivos:** Localización de archivos a través de sucesores.
- **Directorio:** Cada nodo tiene su propio directorio para archivos.
- **Replicación:** Archivos replicados al salir de la red.
- **Modularidad:** Métodos específicos para funcionalidades.
- **Resiliencia:** Manejo de errores de red y fallos.

### 3.5. Descripción y como se configura los parámetros del proyecto (ej: ip, puertos, conexión a bases de datos, variables de ambiente, parámetros, etc)

Al no poder desplegar el proyecto en AWS, se uso la IP local 127.0.0.1. Para los puertos, se puede cualquiera. 

### 3.6. Detalles de la organización del código por carpetas o descripción de algún archivo. (ESTRUCTURA DE DIRECTORIOS Y ARCHIVOS IMPORTANTE DEL PROYECTO, comando 'tree' de linux)

- La carpeta *config* tiene el JSON de cada nodo.
- La carpeta *files* contine un carpetas para uno de los nodos donde se guardan los archivos.
- El archivo *node* es donde se crea los nodos y la red P2P.
- El archivo *app_flask* es el servidor de Flask es el intermediario para hacer las peticiones al red P2P.
- El archivo *client.py* es para hacer solicitudes a la red P2P mediante el servidor de Flask.

## 4. Descripción del ambiente de EJECUCIÓN (en producción) lenguaje de programación, librerias, paquetes, etc, con sus numeros de versiones.

Mirar el numeral anterior.

## 5. Video
https://youtu.be/N8IS6avlVuU

## 6. Referencias

https://github.com/MNoumanAbbasi/Chord-DHT-for-File-Sharing
