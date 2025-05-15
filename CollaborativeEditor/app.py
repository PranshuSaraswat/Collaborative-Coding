from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active rooms and their content
rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<room_id>')
def room(room_id):
    return render_template('index.html', room_id=room_id)

@socketio.on('join')
def on_join(data):
    room_id = data['room']
    join_room(room_id)
    
    # Initialize room if it doesn't exist
    if room_id not in rooms:
        rooms[room_id] = {
            'code': '',
            'users': 0
        }
    
    # Increment user count
    rooms[room_id]['users'] += 1
    
    # Send current code to the new user
    emit('init_code', {'code': rooms[room_id]['code']})
    
    # Notify all users in the room about the new connection
    emit('user_count', {'count': rooms[room_id]['users']}, to=room_id)

@socketio.on('leave')
def on_leave(data):
    room_id = data['room']
    
    if room_id in rooms:
        rooms[room_id]['users'] -= 1
        
        # Remove the room if no users are left
        if rooms[room_id]['users'] <= 0:
            rooms.pop(room_id, None)
        else:
            emit('user_count', {'count': rooms[room_id]['users']}, to=room_id)

@socketio.on('code_update')
def on_code_update(data):
    room_id = data['room']
    code = data['code']
    position = data.get('position', 0)  # Editor cursor position
    
    if room_id in rooms:
        rooms[room_id]['code'] = code
        
        # Broadcast code update to all users in the room except sender
        emit('code_updated', {
            'code': code, 
            'position': position
        }, to=room_id, include_self=False)

@socketio.on('run_code')
def on_run_code(data):
    room_id = data['room']
    code = data['code']
    
    # In a production environment, you'd want to run this code in a sandbox
    # For demonstration, we're just echoing back that the code would be executed
    emit('code_result', {'result': 'Code execution would happen here'}, to=room_id)

if __name__ == '__main__':
    socketio.run(app, debug=True)