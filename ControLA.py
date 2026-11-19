from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Optional


# Crear la API
app = FastAPI(
    title="Control de Tareas",
    description="Prueba sencilla para Becario",
    version="1.0.0"
)


# Datos: id, titulo, prioridad y estado
class Tarea(BaseModel):
    id: int = Field(description="ID único de la tarea", example=1)
    titulo: str = Field(min_length=1, description="La tarea necesita un titulo unico", example="Estudiar")
    prioridad: Literal["alta", "media", "baja"] = Field(description="Prioridad: alta, media o baja", example="alta")
    estado: Literal["pendiente", "completada"] = Field(description="Estado: pendiente o completada", example="pendiente")

    #Validador del titulo 
    @field_validator("titulo")
    @classmethod
    def validar_titulo(cls, titulo):
        if not titulo.strip():
            raise ValueError("El título no puede estar vacio")
        return titulo.strip()


# Datos que se necesitan para crear o reemplazar una tarea
class DatosTarea(BaseModel):
    titulo: str = Field(min_length=1, description="Título obligatorio", example="Estudiar para el examen")
    prioridad: Literal["alta", "media", "baja"] = Field(description="alta, media o baja", example="alta")
    estado: Literal["pendiente", "completada"] = Field(description="pendiente o completada", example="pendiente")

    @field_validator("titulo")
    @classmethod
    def validar_titulo(cls, titulo):
        if not titulo.strip():
            raise ValueError("El título no puede estar vacio")
        return titulo.strip()


# Datos para modificar solamente algunos campos
class CambiosTarea(BaseModel):
    titulo: Optional[str] = Field(default=None, min_length=1, description="Nuevo título")
    prioridad: Optional[Literal["alta", "media", "baja"]] = Field(default=None, description="Nueva prioridad")
    estado: Optional[Literal["pendiente", "completada"]] = Field(default=None, description="Nuevo estado")

    @field_validator("titulo")
    @classmethod
    def validar_titulo(cls, titulo):
        if titulo is not None and not titulo.strip():
            raise ValueError("El título no puede estar vacio.")
        if titulo is not None:
            return titulo.strip()
        return titulo


# arreglo para guardar 
lista_tareas: List[Tarea] = []

# Generador de id unico
siguiente_id = 1


# registrar una tarea nueva
@app.post(
    "/tareas",
    response_model=Tarea,
    summary="Registrar una tarea",
    tags=["Tareas"]
)
def registrar_tarea(datos: DatosTarea):
    global siguiente_id

    nueva_tarea = Tarea(
        id=siguiente_id,
        titulo=datos.titulo,
        prioridad=datos.prioridad,
        estado=datos.estado
    )

    lista_tareas.append(nueva_tarea)
    siguiente_id += 1 #Contador del ID unico

    return nueva_tarea

# Consultar las tareas
@app.get(
    "/tareas",
    response_model=List[Tarea],
    summary="Consultar todas las tareas",
    tags=["Tareas"]
)
def consultar_tareas():
    return lista_tareas


# Buscar la tarea 
@app.get(
    "/tareas/{id_tarea}",
    response_model=Tarea,
    summary="Buscar una tarea por ID",
    tags=["Tareas"]
)
def buscar_tarea(id_tarea: int):
    for tarea in lista_tareas:
        if tarea.id == id_tarea:
            return tarea

    raise HTTPException(status_code=404, detail="La tarea no existe.")


# Remplazar todos los datos de una tarea
@app.put(
    "/tareas/{id_tarea}",
    response_model=Tarea,
    summary="Modificar todos los datos de una tarea",
    tags=["Tareas"]
)
def modificar_tarea(id_tarea: int, nuevos_datos: DatosTarea):
    for posicion, tarea in enumerate(lista_tareas):
        if tarea.id == id_tarea:
            tarea_actualizada = Tarea(
                id=id_tarea,
                titulo=nuevos_datos.titulo,
                prioridad=nuevos_datos.prioridad,
                estado=nuevos_datos.estado
            )
            lista_tareas[posicion] = tarea_actualizada
            return tarea_actualizada

    raise HTTPException(status_code=404, detail="La tarea no existe.")


# Modificar solamente el campo que se envie
@app.patch(
    "/tareas/{id_tarea}",
    response_model=Tarea,
    summary="Modificar una parte de una tarea",
    tags=["Tareas"]
)
def modificar_parte_tarea(id_tarea: int, cambios: CambiosTarea):
    for posicion, tarea in enumerate(lista_tareas):
        if tarea.id == id_tarea:
            datos_actualizados = tarea.dict()
            cambios_recibidos = cambios.dict(exclude_unset=True)

            if not cambios_recibidos:
                raise HTTPException(status_code=400, detail="Debes enviar al menos un dato para modificar.")

            datos_actualizados.update(cambios_recibidos)

            # Volvemos a validar la tarea completa antes de guardarla
            tarea_actualizada = Tarea(**datos_actualizados)
            lista_tareas[posicion] = tarea_actualizada

            return tarea_actualizada

    raise HTTPException(status_code=404, detail="La tarea no existe.")


# Elimina una tarea
@app.delete(
    "/tareas/{id_tarea}",
    summary="Eliminar una tarea",
    tags=["Tareas"]
)
def eliminar_tarea(id_tarea: int):
    for posicion, tarea in enumerate(lista_tareas):
        if tarea.id == id_tarea:
            lista_tareas.pop(posicion)
            return {"mensaje": "Tarea eliminada correctamente."}

    raise HTTPException(status_code=404, detail="La tarea no existe.")


