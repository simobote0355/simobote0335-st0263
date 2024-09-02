import requests
from node import *
#from app_flask import PORT

def upload_file():
    # URL del endpoint de Flask para subir archivos
    nodo = int(input("Enter node: "))
    file = input("Enter file name to upload: ")
    url = f"http://127.0.0.1:2222/upload/{nodo}"

    # Realizar la solicitud POST con el archivo
    with open(file, 'rb') as file:
        response = requests.post(url, files={'file': file})

    # Imprimir la respuesta del servidor
    print(response.json())

def download_file():
    # URL del endpoint de Flask para descargar archivos
    nodo = int(input("Enter node: "))
    filename = input("Enter filename to download: ")
    url = f"http://127.0.0.1:2222/download/{nodo}/{filename}"

    # Realizar la solicitud GET para descargar el archivo
    response = requests.get(url)

    if response.status_code == 200:
        # Guardar el archivo descargado en el directorio actual
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"File '{filename}' succesfully downloaded.")
    else:
        print(f"Error downloading file: {response.json()}")

def search_file():
    node = int(input("Enter node: "))
    filename = input("Enter filename to search: ")
    url = f"http://127.0.0.1:2222/search/{node}/{filename}"

    response = requests.get(url)

    if response.status_code == 200:
        print(response.json()["message"])
    else:
        print(f"Error searching for file: {response.json()}")


def main():
    while True:
        print("1. Upload file")
        print("2. Download file")
        print("3. Search file")
        print("4. Exit")

        option = input("Enter your choice: " )

        if option == '1':
            upload_file()
        elif option == '2':
            download_file()
        elif option == '3':
            search_file()
        else:
           break

if __name__ == "__main__":
    main()
