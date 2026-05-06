import struct
import math
import os
import io
import tempfile
import zipfile
import secrets  # Використовуємо замість random для проходження SonarQube

from DSS.dss_signature import DSSManager
from RC5Encryption.RC5 import RC5FileProcessor
from flask import Flask, request, jsonify, render_template, send_file
from LinearCongruentialGenerator.LCG import LCG
from MD5Hash.MD5 import MyMD5
from RSAEncryption.RSA import RSACipher

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

    # Використання безпечного генератора secrets замість random
    sys_numbers = [secrets.randbelow(m + 1) for _ in range(count)]

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
    action = request.form.get('action')

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
    except (IOError, OSError) as e:
        return jsonify({"error": f"Помилка файлової системи: {str(e)}"}), 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)


# --- Helper methods for RSA ---

def _handle_rsa_generate(key_size):
    cipher = RSACipher(key_size=key_size)
    cipher.generate_keys()

    with tempfile.TemporaryDirectory() as temp_dir:
        priv_path = os.path.join(temp_dir, 'private.pem')
        pub_path = os.path.join(temp_dir, 'public.pem')
        cipher.save_keys(priv_path, pub_path)

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            zf.write(priv_path, 'private.pem')
            zf.write(pub_path, 'public.pem')
        memory_file.seek(0)

    return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name='rsa_keys.zip')


def _handle_rsa_encrypt(file_to_encrypt, public_key_file):
    if not file_to_encrypt or not public_key_file:
        raise ValueError("Будь ласка, завантажте файл та публічний ключ.")

    with tempfile.TemporaryDirectory() as temp_dir:
        in_path = os.path.join(temp_dir, 'input_file')
        pub_path = os.path.join(temp_dir, 'public.pem')
        out_path = os.path.join(temp_dir, 'encrypted.bin')

        file_to_encrypt.save(in_path)
        public_key_file.save(pub_path)

        cipher = RSACipher()
        cipher.load_public_key(pub_path)
        cipher.encrypt_file(in_path, out_path)

        with open(out_path, 'rb') as f:
            return_data = io.BytesIO(f.read())

    return send_file(return_data, as_attachment=True, download_name=f"{file_to_encrypt.filename}.encrypted")


def _handle_rsa_decrypt(file_to_decrypt, private_key_file):
    if not file_to_decrypt or not private_key_file:
        raise ValueError("Будь ласка, завантажте зашифрований файл та приватний ключ.")

    with tempfile.TemporaryDirectory() as temp_dir:
        in_path = os.path.join(temp_dir, 'encrypted_file')
        priv_path = os.path.join(temp_dir, 'private.pem')
        out_path = os.path.join(temp_dir, 'decrypted_file')

        file_to_decrypt.save(in_path)
        private_key_file.save(priv_path)

        cipher = RSACipher()
        cipher.load_private_key(priv_path)
        cipher.decrypt_file(in_path, out_path)

        with open(out_path, 'rb') as f:
            return_data = io.BytesIO(f.read())

    original_name = file_to_decrypt.filename.replace('.encrypted', '')
    if original_name == file_to_decrypt.filename:
        original_name = "decrypted_" + file_to_decrypt.filename

    return send_file(return_data, as_attachment=True, download_name=original_name)


@app.route('/rsa', methods=['GET', 'POST'])
def rsa():
    error = None
    if request.method == 'POST':
        action = request.form.get('action')
        try:
            if action == 'generate_keys':
                key_size = int(request.form.get('key_size', 2048))
                return _handle_rsa_generate(key_size)
            elif action == 'encrypt':
                return _handle_rsa_encrypt(request.files.get('file_to_encrypt'), request.files.get('public_key'))
            elif action == 'decrypt':
                return _handle_rsa_decrypt(request.files.get('file_to_decrypt'), request.files.get('private_key'))
        except ValueError as e:
            error = f"Помилка вводу: {str(e)}"
        except (IOError, OSError) as e:
            error = f"Системна помилка: {str(e)}"

    return render_template('rsa.html', error=error)


# --- Helper methods for DSS ---

def _handle_dss_generate(key_size):
    manager = DSSManager()
    manager.generate_keys(key_size=key_size)

    with tempfile.TemporaryDirectory() as temp_dir:
        priv_path = os.path.join(temp_dir, 'private_key.pem')
        pub_path = os.path.join(temp_dir, 'public_key.pem')
        manager.save_keys_to_files(priv_path, pub_path)

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            zf.write(priv_path, 'private_key.pem')
            zf.write(pub_path, 'public_key.pem')
        memory_file.seek(0)

    return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name='dss_keys.zip')


def _handle_dss_sign_text(request):
    text_to_sign = request.form.get('text_to_sign')
    private_key_file = request.files.get('private_key')
    if not text_to_sign or not private_key_file:
        raise ValueError("Введіть текст та завантажте приватний ключ.")

    with tempfile.TemporaryDirectory() as temp_dir:
        priv_path = os.path.join(temp_dir, 'private_key.pem')
        private_key_file.save(priv_path)
        manager = DSSManager()
        manager.load_private_key(priv_path)
        return manager.sign_text(text_to_sign), "Текст успішно підписано!"


def _handle_dss_verify_text(request):
    text_to_verify = request.form.get('text_to_verify')
    signature_hex = request.form.get('signature_hex')
    public_key_file = request.files.get('public_key')
    if not text_to_verify or not signature_hex or not public_key_file:
        raise ValueError("Заповніть всі поля та завантажте публічний ключ.")

    with tempfile.TemporaryDirectory() as temp_dir:
        pub_path = os.path.join(temp_dir, 'public_key.pem')
        public_key_file.save(pub_path)
        manager = DSSManager()
        manager.load_public_key(pub_path)
        is_valid = manager.verify_text(text_to_verify, signature_hex.strip())

    if is_valid:
        return "Успіх! Підпис дійсний (текст належить автору).", None
    return None, "Помилка! Підпис НЕ дійсний або текст було змінено."


def _handle_dss_sign_file(request):
    file_to_sign = request.files.get('file_to_sign')
    private_key_file = request.files.get('private_key')
    if not file_to_sign or not private_key_file:
        raise ValueError("Завантажте файл для підпису та приватний ключ.")

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, 'upload_file')
        priv_path = os.path.join(temp_dir, 'private_key.pem')
        file_to_sign.save(file_path)
        private_key_file.save(priv_path)
        manager = DSSManager()
        manager.load_private_key(priv_path)
        signature = manager.sign_file(file_path)
        return signature, f"Файл {file_to_sign.filename} успішно підписано!"


def _handle_dss_verify_file(request):
    file_to_verify = request.files.get('file_to_verify')
    signature_hex = request.form.get('signature_hex')
    public_key_file = request.files.get('public_key')
    if not file_to_verify or not signature_hex or not public_key_file:
        raise ValueError("Завантажте файл, публічний ключ та введіть підпис.")

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, 'upload_file')
        pub_path = os.path.join(temp_dir, 'public_key.pem')
        file_to_verify.save(file_path)
        public_key_file.save(pub_path)
        manager = DSSManager()
        manager.load_public_key(pub_path)
        is_valid = manager.verify_file(file_path, signature_hex.strip())

    if is_valid:
        return f"Успіх! Підпис для файлу {file_to_verify.filename} дійсний.", None
    return None, "Помилка! Підпис для файлу НЕ дійсний."


@app.route('/dss', methods=['GET', 'POST'])
def dss():
    error = None
    message = None
    signature = None

    if request.method == 'POST':
        action = request.form.get('action')
        try:
            if action == 'generate_keys':
                key_size = int(request.form.get('key_size', 2048))
                return _handle_dss_generate(key_size)
            elif action == 'sign_text':
                signature, message = _handle_dss_sign_text(request)
            elif action == 'verify_text':
                message, error = _handle_dss_verify_text(request)
            elif action == 'sign_file':
                signature, message = _handle_dss_sign_file(request)
            elif action == 'verify_file':
                message, error = _handle_dss_verify_file(request)
        except ValueError as e:
            error = f"Помилка вводу: {str(e)}"
        except (IOError, OSError) as e:
            error = f"Системна помилка: {str(e)}"

    return render_template('dss.html', error=error, message=message, signature=signature)