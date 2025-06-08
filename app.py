from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit, join_room
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import os
import hashlib
import logging
import socket
import uuid
import base64
from werkzeug.utils import secure_filename
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Cấu hình logging
logging.basicConfig(
    filename='file_transfer.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Tạo thư mục uploads nếu chưa có
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Danh sách người dùng mẫu với mật khẩu mã hóa
users = {
    'Alice': {'password': bcrypt.hashpw('alice123'.encode(), bcrypt.gensalt()), 'id': '1'},
    'Bob': {'password': bcrypt.hashpw('bob123'.encode(), bcrypt.gensalt()), 'id': '2'},
    'Charlie': {'password': bcrypt.hashpw('charlie123'.encode(), bcrypt.gensalt()), 'id': '3'},
    'David': {'password': bcrypt.hashpw('david123'.encode(), bcrypt.gensalt()), 'id': '4'}
}

# Lưu trữ file trong phòng
room_files = {}

class User(UserMixin):
    def __init__(self, username):
        self.id = users[username]['id']
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    for username, data in users.items():
        if data['id'] == user_id:
            return User(username)
    return None

# Tính hash SHA-256 của file
def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logging.error(f'Error calculating SHA-256 for {file_path}: {str(e)}')
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode()
        if username in users and bcrypt.checkpw(password, users[username]['password']):
            user = User(username)
            login_user(user)
            logging.info(f'Người dùng {username} đăng nhập thành công')
            return redirect(url_for('index'))
        flash('Tên người dùng hoặc mật khẩu không đúng')
        logging.warning(f'Đăng nhập thất bại với username: {username}')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    logging.info(f'Người dùng {username} đăng xuất')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    other_users = [u for u in users.keys() if u != current_user.username]
    return render_template('index.html', users=other_users, current_user=current_user.username)

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        logging.info(f'Client {current_user.username} connected: {request.sid}')
        emit('message', {'data': f'Đã kết nối với tư cách {current_user.username}'})

@socketio.on('start_room')
def handle_start_room(data):
    try:
        sender = data.get('sender')
        recipient = data.get('recipient')
        if not sender or not recipient or sender not in users or recipient not in users:
            emit('error', {'message': 'Người gửi hoặc nhận không hợp lệ'}, to=request.sid)
            logging.error(f'Invalid start_room data: {data}')
            return
        room_id = '-'.join(sorted([sender, recipient]))
        join_room(room_id)
        emit('room_started', {
            'recipient': recipient,
            'room_id': room_id
        }, to=request.sid)
        # Gửi danh sách file hiện có trong phòng
        files = room_files.get(room_id, [])
        emit('load_files', {'files': files}, to=request.sid)
        logging.info(f'{sender} đã vào phòng {room_id} với {recipient}, loaded {len(files)} files')
    except Exception as e:
        emit('error', {'message': f'Lỗi khởi tạo phòng: {str(e)}'}, to=request.sid)
        logging.error(f'Error in start_room: {str(e)}')

@socketio.on('upload_file')
def handle_upload_file(data):
    try:
        required_keys = ['filename', 'file_data', 'file_size', 'room_id', 'recipient', 'sender']
        if not all(key in data for key in required_keys):
            emit('error', {'message': 'Dữ liệu upload không đầy đủ'}, to=request.sid)
            logging.error(f'Missing data in upload_file: {data}')
            return
        
        filename = secure_filename(data['filename'])
        file_data = data['file_data']
        file_size = data['file_size']
        room_id = data['room_id']
        recipient = data['recipient']
        sender = data['sender']
        file_id = str(uuid.uuid4())
        
        # Kiểm tra định dạng file_data
        if not file_data.startswith('data:'):
            emit('error', {'message': 'Dữ liệu file không hợp lệ'}, to=request.sid)
            logging.error(f'Invalid file_data format for {filename}')
            return
        
        # Lưu file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        try:
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(file_data.split(',')[1]))
        except Exception as e:
            emit('error', {'message': f'Lỗi lưu file: {str(e)}'}, to=request.sid)
            logging.error(f'Error saving file {filename}: {str(e)}')
            return
        
        # Tính hash SHA-256
        file_hash = calculate_sha256(file_path)
        if not file_hash:
            emit('error', {'message': 'Lỗi tính hash file'}, to=request.sid)
            logging.error(f'Failed to calculate hash for {filename}')
            return
        
        # Lưu thông tin file vào room_files
        file_info = {
            'file_id': file_id,
            'filename': filename,
            'file_size': file_size,
            'file_hash': file_hash,
            'sender': sender,
            'room_id': room_id
        }
        if room_id not in room_files:
            room_files[room_id] = []
        room_files[room_id].append(file_info)
        
        # Gửi thông tin file cho phòng
        emit('file_received', file_info, room=room_id, include_self=True)
        
        logging.info(f'File uploaded by {sender} to {recipient} in room {room_id}: {filename}, Hash: {file_hash}, Size: {file_size} bytes')
        
    except Exception as e:
        emit('error', {'message': f'Lỗi upload file: {str(e)}'}, to=request.sid)
        logging.error(f'Error in upload_file: {str(e)}')

@socketio.on('download_file')
def handle_download_file(data):
    try:
        required_keys = ['file_id', 'filename', 'room_id']
        if not all(key in data for key in required_keys):
            emit('error', {'message': 'Dữ liệu download không đầy đủ'}, to=request.sid)
            logging.error(f'Missing data in download_file: {data}')
            return
        
        file_id = data['file_id']
        filename = data['filename']
        room_id = data['room_id']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        
        if os.path.exists(file_path):
            file_hash = calculate_sha256(file_path)
            if not file_hash:
                emit('error', {'message': 'Lỗi tính hash file'}, to=request.sid)
                logging.error(f'Failed to calculate hash for {filename}')
                return
            
            with open(file_path, 'rb') as f:
                file_data = base64.b64encode(f.read()).decode()
            
            emit('download_ready', {
                'file_id': file_id,
                'filename': filename,
                'file_data': f'data:application/octet-stream;base64,{file_data}',
                'file_hash': file_hash,
                'room_id': room_id
            }, to=request.sid)
            
            logging.info(f'File downloaded by {current_user.username} in room {room_id}: {filename}, Hash: {file_hash}')
        
        else:
            emit('error', {'message': 'File không tồn tại'}, to=request.sid)
            logging.error(f'File not found: {file_path}')
            
    except Exception as e:
        emit('error', {'message': f'Lỗi download file: {str(e)}'}, to=request.sid)
        logging.error(f'Error in download_file: {str(e)}')

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f" * Ứng dụng đang chạy tại:")
    print(f"   - Local: http://127.0.0.1:5000")
    print(f"   - Mạng nội bộ: http://{local_ip}:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)