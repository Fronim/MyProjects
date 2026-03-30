import random
import struct
import math
import os
import io
from flask import send_file

from RC5Encryption.RC5 import RC5FileProcessor
from flask import Flask, request, jsonify, render_template
from LinearCongruentialGenerator.LCG import LCG
from MD5Hash.MD5 import MyMD5


app = Flask(__name__)
app.json.sort_keys = False

@app.route('/')
def home():
    return render_template('index.html')


md5_tool = MyMD5()

@app.route('/md5')
def md5_page():
    return render_template('md5.html')

@app.route('/api/v1/md5/text', methods=['POST'])
def api_md5_text():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    md5_tool.hash(data['text'])

    result = struct.pack('<4I', md5_tool.A, md5_tool.B, md5_tool.C, md5_tool.D).hex()

    return jsonify({
        "input_type": "text",
        "input_value": data['text'],
        "hash": result
    })


@app.route('/api/v1/md5/file', methods=['POST'])
def api_md5_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    temp_path = os.path.join("temp_upload.bin")
    file.save(temp_path)

    try:
        result = md5_tool.hash_file(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return jsonify({
        "input_type": "file",
        "filename": file.filename,
        "hash": result
    })

@app.route('/lcg')
def lcg_page():
    return render_template('lcg.html')


@app.route('/api/v1/generate', methods=['POST'])
def api_generate():
    data = request.json

    if not data:
        return jsonify({"error": "Відсутні дані у запиті"}), 400

    try:
        m = int(data.get('m', 2 ** 31 - 7))
        a = int(data.get('a', 2 ** 14))
        c = int(data.get('c', 75025))
        x0 = int(data.get('x0', 41))
        count = int(data.get('count', 10000))

        if count <= 0 or m <= 0:
            return jsonify({"error": "Значення count та m мають бути додатними числами"}), 400

    except (TypeError, ValueError):
        return jsonify({"error": "Некоректний формат даних. Очікуються цілі числа."}), 400

    generator = LCG(x0=x0, m=m, a=a, c=c)
    numbers = generator.generate(count)
    pi_estimate = generator.cesaro_test(numbers)

    return jsonify({
        "configuration": {"m": m, "a": a, "c": c, "seed": x0},
        "statistics": {
            "pi_estimate": round(pi_estimate, 6),
            "theoretical_pi": round(math.pi, 6),
            "error_margin": round(abs(math.pi - pi_estimate), 6)
        },
        "data_sample": numbers[:50],
        "chart_data": numbers[:1000]
    })

@app.route('/api/v1/period', methods=['POST'])
def api_period():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Відсутні дані у запиті"}), 400

    try:
        m = int(data.get('m', 2 ** 31 - 7))
        a = int(data.get('a', 2 ** 14))
        c = int(data.get('c', 75025))
        x0 = int(data.get('x0', 41))

        if m <= 0:
            return jsonify({"error": "Модуль m має бути додатним"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Некоректний формат даних"}), 400

    generator = LCG(x0=x0, m=m, a=a, c=c)
    period = generator.find_period()

    if period == -1:
        return jsonify({"message": "> 5 000 000 (занадто великий для миттєвого пошуку)"})

    return jsonify({"period": period})


@app.route('/api/v1/system_generate', methods=['POST'])
def api_system_generate():
    data = request.get_json(silent=True) or {}

    try:
        count = int(data.get('count', 10000))
        m = int(data.get('m', 2 ** 31 - 7))
    except (TypeError, ValueError):
        return jsonify({"error": "Некоректний формат даних"}), 400

    sys_numbers = [random.randint(0, m) for _ in range(count)]

    dummy_generator = LCG()
    pi_estimate = dummy_generator.cesaro_test(sys_numbers)

    return jsonify({
        "statistics": {
            "pi_estimate": round(pi_estimate, 6),
            "theoretical_pi": round(math.pi, 6),
            "error_margin": round(abs(math.pi - pi_estimate), 6)
        },
        "chart_data": sys_numbers[:1000]
    })



@app.route('/rc5')
def rc5_page():
    return render_template('rc5.html')


@app.route('/api/v1/rc5/process', methods=['POST'])
def api_rc5_process():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    password = request.form.get('password')
    key_length = int(request.form.get('key_length', 128))
    action = request.form.get('action')  # 'encrypt' або 'decrypt'

    if not password:
        return jsonify({"error": "Введіть парольну фразу"}), 400

    input_path = os.path.join(f"temp_rc5_in_{file.filename}")
    output_path = os.path.join(f"temp_rc5_out_{file.filename}")

    file.save(input_path)

    try:
        processor = RC5FileProcessor(password=password, key_length_bits=key_length)

        if action == 'encrypt':
            processor.encrypt_file(input_path, output_path)
            prefix = "encrypted_"
        elif action == 'decrypt':
            processor.decrypt_file(input_path, output_path)
            prefix = "decrypted_"
        else:
            return jsonify({"error": "Невідома дія"}), 400

        with open(output_path, 'rb') as f:
            return_data = io.BytesIO(f.read())

        return send_file(
            return_data,
            as_attachment=True,
            download_name=f"{prefix}{file.filename}",
            mimetype='application/octet-stream'
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Сталася помилка: {str(e)}"}), 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)