from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
import sys
import io
import contextlib
import traceback
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active rooms and their content
rooms = {}

def execute_python_code(code):
    """Execute Python code and return the output."""
    # Create string buffer to capture output
    buffer = io.StringIO()
    result = {"output": ""}
    
    def run_code():
        try:
            # Redirect stdout and stderr to our buffer
            with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
                # Create a safe globals dictionary with limited builtins
                safe_builtins = {}
                allowed_builtins = [
                    "abs", "all", "any", "ascii", "bin", "bool", "bytearray", 
                    "bytes", "chr", "complex", "dict", "dir", "divmod", 
                    "enumerate", "filter", "float", "format", "frozenset", 
                    "hash", "hex", "int", "isinstance", "issubclass", "iter", 
                    "len", "list", "map", "max", "min", "next", "oct", "ord", 
                    "pow", "print", "range", "repr", "reversed", "round", 
                    "set", "slice", "sorted", "str", "sum", "tuple", "type", "zip"
                ]
                
                # Get the builtins properly
                import builtins
                for name in allowed_builtins:
                    if hasattr(builtins, name):
                        safe_builtins[name] = getattr(builtins, name)
                
                exec_globals = {'__builtins__': safe_builtins}
                
                # Execute the code with restricted globals
                exec(code, exec_globals)
            
            result["output"] = buffer.getvalue() or "Code executed successfully (no output)"
        except Exception as e:
            # Get the full traceback
            error_msg = traceback.format_exc()
            result["output"] = f"Error:\n{error_msg}"
    
    # Run the code in a separate thread
    code_thread = threading.Thread(target=run_code)
    code_thread.daemon = True
    code_thread.start()
    
    # Wait for 5 seconds or until thread finishes
    code_thread.join(5)
    
    # If thread is still running after timeout
    if code_thread.is_alive():
        return "Error: Code execution timed out after 5 seconds"
    
    return result["output"]

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
    
    # Execute the Python code securely and capture output
    result = execute_python_code(code)
    emit('code_result', {'result': result}, to=room_id)

if __name__ == '__main__':
    socketio.run(app, debug=True)