import json   # Importo la librería para trabajar con archivos JSON

# Nombre del archivo donde están los datos
archivo = "PG_data.json"

# Abrir el archivo y convertirlo en un diccionario de Python
with open (archivo) as file:
    datos = json.load(file)

# En el archivo, la lista de proteínas está en "results"
registros = datos["results"]

# Listas donde voy a guardar la información de las proteínas que me interesan
conteo_list = []
id_list = []
ubicacion_list = []
descripcion_list = []
secuencia_list = []

contador = 1   # Para numerar cada proteína encontrada

# Recorro cada proteína dentro de la lista "results"
for registro in registros:
    # ID de la proteína
    accession = registro["primaryAccession"]

    # Descripción (nombre de la proteína)
    descripcion = ""
    if "proteinDescription" in registro:
        if "recommendedName" in registro["proteinDescription"]:
            nombre = registro["proteinDescription"]["recommendedName"]
            if "fullName" in nombre:
                descripcion = nombre["fullName"]["value"]

    # Secuencia de aminoácidos
    secuencia = ""
    if "sequence" in registro:
        secuencia = registro["sequence"]["value"]

    # Revisar si tiene anotación de "outer membrane" o "inner membrane"
    if "comments" in registro:
        for comentario in registro["comments"]:
            if comentario["commentType"] == "SUBCELLULAR LOCATION":
                for loc in comentario["subcellularLocations"]:
                    lugar = loc["location"]["value"].lower()
                    if "outer membrane" in lugar or "inner membrane" in lugar:
                        # Guardo los datos en las listas
                        conteo_list.append(contador)
                        id_list.append(accession)
                        ubicacion_list.append(lugar)
                        descripcion_list.append(descripcion)
                        secuencia_list.append(secuencia)
                        contador += 1

# Mostrar en pantalla los resultados (usando tabuladores para alinear)
print("Conteo", "ID", "Ubicacion", "Descripcion", "Secuencia", sep="\t")
for c, i, u, d, s in zip(conteo_list, id_list, ubicacion_list, descripcion_list, secuencia_list):
    # Muestro solo los primeros 30 aa en pantalla para que la salida sea legible
    print(c, i, u, d, s[:30] + "...", sep="\t")

# Guardar la información completa en un archivo TSV
with open("proteinas_membrana.tsv", "w") as salida:
    salida.write("Conteo\tID\tUbicacion\tDescripcion\tSecuencia\n")
    #salida.write("Conteo", "ID", "Ubicacion", "Descripcion", "Secuencia", sep="\t")
    for c, i, u, d, s in zip(conteo_list, id_list, ubicacion_list, descripcion_list, secuencia_list):
        # Escribir cada fila
        salida.write(f"{c}\t{i}\t{u}\t{d}\t{s}\n")



