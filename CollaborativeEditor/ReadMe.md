# Collaborative Python Editor

A real-time collaborative code editor for Python that allows multiple users to code together in a split-screen interface with live updates.

## Features

- Real-time code synchronization between users
- Split-screen interface with code editor and output panel
- Python syntax highlighting
- Actual Python code execution with output display
- Room-based collaboration
- Simple and intuitive UI

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/PranshuSaraswat/collaborative-python-editor.git
   cd collaborative-python-editor
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the Flask server:
   ```
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

1. **Create a Room**: Click the "Create Room" button to generate a random room ID.

2. **Join a Room**: Enter a room ID in the input field and click "Join Room".

3. **Share the Room**: Share the URL with others to collaborate. The URL format is:
   ```
   http://localhost:5000/{room_id}
   ```

4. **Write Code**: Start writing Python code in the editor. All changes will be synchronized in real-time with other users in the same room.

5. **Run Code**: Click the "Run Code" button to execute the Python code.

6. **View Output**: The results of code execution will appear in the output panel.

## Technologies Used

- **Backend**: Flask, Flask-SocketIO
- **Frontend**: HTML, CSS, JavaScript
- **Code Editor**: CodeMirror
- **Real-time Communication**: Socket.IO

## Limitations

This is a demonstration project with some limitations:

- Code execution has restricted access to Python built-ins for security
- No persistent storage of code between sessions
- Limited error handling
- No user authentication
- Execution timeout of 5 seconds for long-running code

## Future Improvements

- Add support for more Python libraries with proper sandboxing 
- Add user authentication and permissions
- Implement persistent storage for code
- Add more features like file management, version history, etc.