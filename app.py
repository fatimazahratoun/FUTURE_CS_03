from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
import os
import base64
from werkzeug.utils import secure_filename
from encryption import encrypt_file, decrypt_file_with_key, generate_key, save_key, load_key
import uuid

app = Flask(__name__)
app.secret_key = 'secure-file-sharing-secret-key-2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['KEYS_FOLDER'] = 'keys'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB max
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'zip', 'csv', 'py', 'js', 'html', 'css'}

# Create folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['KEYS_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Home page"""
    files = get_file_list()
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload and encrypt a file"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        flash('File type not allowed. Allowed: ' + ', '.join(app.config['ALLOWED_EXTENSIONS']), 'error')
        return redirect(url_for('index'))
    
    # Generate unique ID for the file
    file_id = str(uuid.uuid4())
    original_filename = secure_filename(file.filename)
    encrypted_filename = f"{file_id}_{original_filename}.enc"
    
    # Temporary save
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{file_id}")
    file.save(temp_path)
    
    # Generate key and encrypt
    key = generate_key()
    encrypted_data = encrypt_file(temp_path, key)
    
    # Save encrypted file
    encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], encrypted_filename)
    with open(encrypted_path, 'wb') as f:
        f.write(encrypted_data)
    
    # Save the key
    save_key(file_id, key)
    
    # Remove temporary file
    os.remove(temp_path)
    
    flash(f'✅ File "{original_filename}" encrypted and saved successfully!', 'success')
    flash(f'🔑 File ID: {file_id} (Keep this for download)', 'info')
    flash(f'🔐 Encrypted file: {encrypted_filename}', 'info')
    
    return redirect(url_for('index'))

@app.route('/files')
def list_files():
    """API to list files (JSON)"""
    files = get_file_list()
    return jsonify(files)

@app.route('/download/<file_id>')
def download_file(file_id):
    """Download and decrypt a file (automatic decryption)"""
    # Find encrypted file
    encrypted_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) 
                      if f.startswith(file_id) and f.endswith('.enc')]
    
    if not encrypted_files:
        flash('File not found', 'error')
        return redirect(url_for('index'))
    
    encrypted_filename = encrypted_files[0]
    encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], encrypted_filename)
    
    # Load key
    key = load_key(file_id)
    if not key:
        flash('Decryption key not found', 'error')
        return redirect(url_for('index'))
    
    # Decrypt
    decrypted_data = decrypt_file_with_key(encrypted_path, key)
    
    if decrypted_data is None:
        flash('Decryption error. File may be corrupted.', 'error')
        return redirect(url_for('index'))
    
    # Extract original name
    original_name = encrypted_filename.split('_', 1)[1].replace('.enc', '')
    
    # Create temporary decrypted file
    temp_decrypted = os.path.join(app.config['UPLOAD_FOLDER'], f"decrypted_{file_id}")
    with open(temp_decrypted, 'wb') as f:
        f.write(decrypted_data)
    
    # Send file
    response = send_file(temp_decrypted, 
                        as_attachment=True, 
                        download_name=original_name,
                        mimetype='application/octet-stream')
    
    # Cleanup after sending
    @response.call_on_close
    def cleanup():
        if os.path.exists(temp_decrypted):
            os.remove(temp_decrypted)
    
    return response

@app.route('/download-encrypted/<file_id>')
def download_encrypted(file_id):
    """Download encrypted file only (no decryption)"""
    # Find encrypted file
    encrypted_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) 
                      if f.startswith(file_id) and f.endswith('.enc')]
    
    if not encrypted_files:
        flash('File not found', 'error')
        return redirect(url_for('index'))
    
    encrypted_filename = encrypted_files[0]
    encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], encrypted_filename)
    
    # Keep .enc extension for encrypted file
    download_name = encrypted_filename
    
    return send_file(encrypted_path, 
                    as_attachment=True, 
                    download_name=download_name,
                    mimetype='application/octet-stream')

@app.route('/download-key/<file_id>')
def download_key(file_id):
    """Download encryption key separately"""
    key_path = os.path.join(app.config['KEYS_FOLDER'], f"{file_id}.key")
    
    if not os.path.exists(key_path):
        flash('Encryption key not found', 'error')
        return redirect(url_for('index'))
    
    # Read key
    with open(key_path, 'r') as f:
        key_content = f.read()
    
    # Create informative key file
    info_content = f"""=== ENCRYPTION KEY FILE ===
File ID: {file_id}
Key (base64): {key_content}

=== INSTRUCTIONS ===
1. Download the encrypted file (.enc extension)
2. Save this key file
3. Use the decryption tool:
   python decrypt.py [encrypted_file.enc] [key_file.key]

=== SECURITY WARNING ===
Keep this key secure! Anyone with this key can decrypt your file.
"""
    
    return info_content, 200, {
        'Content-Type': 'text/plain',
        'Content-Disposition': f'attachment; filename="{file_id}_key.txt"'
    }

@app.route('/delete/<file_id>', methods=['POST'])
def delete_file(file_id):
    """Delete a file and its key"""
    # Find and delete encrypted file
    encrypted_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) 
                      if f.startswith(file_id) and f.endswith('.enc')]
    
    if encrypted_files:
        encrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], encrypted_files[0])
        if os.path.exists(encrypted_path):
            os.remove(encrypted_path)
    
    # Delete key
    key_path = os.path.join(app.config['KEYS_FOLDER'], f"{file_id}.key")
    if os.path.exists(key_path):
        os.remove(key_path)
    
    flash('🗑️ File and encryption key deleted successfully', 'success')
    return redirect(url_for('index'))

@app.route('/api/info')
def api_info():
    """API endpoint for system information"""
    import platform
    info = {
        'system': 'Secure File Sharing System',
        'version': '1.0.0',
        'encryption': 'AES-256-GCM',
        'files_count': len([f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.enc')]),
        'keys_count': len([f for f in os.listdir(app.config['KEYS_FOLDER']) if f.endswith('.key')]),
        'python_version': platform.python_version(),
        'flask_version': '2.3.3'
    }
    return jsonify(info)

def get_file_list():
    """Get list of files with metadata"""
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.endswith('.enc'):
            parts = filename.split('_', 1)
            if len(parts) == 2:
                file_id = parts[0]
                original_name = parts[1].replace('.enc', '')
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(file_path):
                    files.append({
                        'id': file_id,
                        'name': original_name,
                        'size': os.path.getsize(file_path),
                        'uploaded': os.path.getctime(file_path)
                    })
    # Sort by upload time (newest first)
    files.sort(key=lambda x: x['uploaded'], reverse=True)
    return files

if __name__ == '__main__':
    app.run(debug=True, port=5000)