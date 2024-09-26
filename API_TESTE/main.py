from flask import Flask, jsonify, request

app = Flask(__name__)

# Dicionário para armazenar contagem de requisições por endpoint
request_data = {
    '/norte':{'count': 0, 'ips':{}},
    '/sul': {'count': 0, 'ips':{}},
    '/reset': {'count': 0, 'ips':{}},
    '/health':{'count': 0, 'ips':{}},
    '/counts':{'counts':0, 'ips':{}}
}

# Função para incrementar o contador de um endpoint
def increment_count(endpoint):
    if endpoint in request_data:
        # Aumenta a contagem total do enpoint
        request_data[endpoint]['count'] += 1
        # Armazena o IP do Cliente
        client_ip = request.remote_addr
         
        #Incremente a contagem par ao ip
        if client_ip in request_data[endpoint]['ips']:
            request_data[endpoint]['ips'][client_ip] +=1
        else:
            request_data[endpoint]['ips'][client_ip] =1

# Endpoint de saúde
@app.route('/health', methods=['GET'])
def health():
    increment_count('/health')
    return jsonify({'status': 'OK'}), 200

# Primeiro endpoint de teste
@app.route('/norte', methods=['GET'])
def norte():
    increment_count('/norte')
    return jsonify({'message': 'Norte encontrado!'}), 200

# Segundo endpoint de teste
@app.route('/sul', methods=['GET'])
def sul():
    increment_count('/sul')
    return jsonify({'message': 'Sul encontrado!'}), 200

# Endpoint para resetar o contador de requisições
@app.route('/reset', methods=['POST'])
def reset():
    for key in request_data.keys():
        request_data[key]['count'] = 0
        request_data[key]['ips'] = {}
    increment_count('/reset')
    return jsonify({'message': 'Contadores Resetados!'}), 200

# Endpoint para mostrar a contagem de requisições
@app.route('/counts', methods=['GET'])
def get_counts():
    return jsonify(request_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
