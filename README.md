# Modpacks API

Este proyecto es una API basica construida con FastAPI y SQLite para gestionar modpacks.

## Instalacion y Ejecucion

1. Instalar las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecutar el servidor:
   ```bash
   uvicorn main:app --reload
   ```

La base de datos SQLite (database.db) se creara automaticamente en el directorio del proyecto la primera vez que se ejecute la aplicacion. No es necesario instalar ningun motor de base de datos externo.


## Endpoints

### 1. Obtener modpacks de un juego
- Ruta: GET /game/{gameId}/modpacks
- Parametros:
  - gameId (Path): ID del juego.
  - page (Query, opcional): Numero de pagina para la paginacion (por defecto es 1). Retorna 10 resultados por pagina.
- Respuesta: Arreglo de modpacks.

### 2. Obtener modpacks del usuario
- Ruta: GET /user/modpacks
- Autenticacion: Requiere una cookie llamada user_id.
- Respuesta: Arreglo de todos los modpacks creados por el usuario especificado en la cookie.

### 3. Crear un modpack
- Ruta: POST /game/{gameId}/modpacks
- Autenticacion: Requiere una cookie llamada user_id.
- Parametros:
  - gameId (Path): ID del juego al que pertenece el modpack.
- Cuerpo de la peticion (JSON):
  ```json
  {
    "nombre": "Nombre del modpack",
    "descripcion": "Descripcion detallada",
    "mods": {
      "ejemplo": "JSON no descriptivo"
    }
  }
  ```
- Respuesta: Objeto del modpack creado, incluyendo su ID unico generado.
