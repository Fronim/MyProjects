import random
import struct
import math
import os

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
