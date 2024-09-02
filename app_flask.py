from flask import Flask, request, jsonify, send_file
import os
from node import Node

app = Flask(__name__)
PORT = 2222

# Ruta para subir un archivo a un nodo específico
@app.route('/upload/<int:node_port>', methods=['POST'])
def upload_file(node_port):
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Definir la carpeta de destino para el archivo
    upload_folder = f'files/node_{node_port}'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Guardar el archivo en la carpeta correspondiente
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)
    
    return jsonify({"message": f"File '{file.filename}' uploaded successfully to node port {node_port}"}), 200

@app.route('/download/<int:node_port>/<string:filename>', methods=['GET'])
def download_file(node_port, filename):
    # Definir la carpeta donde se encuentra el archivo
    upload_folder = f'files/node_{node_port}'
    file_path = os.path.join(upload_folder, filename)
    
    # Verificar si el archivo existe
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:       
        return jsonify({"error": "File not found"}), 404
    
@app.route('/search/<int:node_port>/<string:filename>', methods=['GET'])
def search_file(node_port, filename):
    node = Node("127.0.0.1", node_port)  # O usa un mecanismo para obtener el nodo en ejecución
    result = node.find_file(filename)
    
    if result:
        return jsonify({"message": f"File '{filename}' found at node with ID {result}"}), 200
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(port = PORT, debug=True)
