document.addEventListener('DOMContentLoaded', () => {
    // Initialize variables
    let socket;
    let editor;
    let currentRoom = null;
    let isInitialLoad = true;
    let isConnected = false;
    let isTyping = false;
    let typingTimeout;

    // DOM elements
    const createRoomBtn = document.getElementById('create-room');
    const joinRoomBtn = document.getElementById('join-room');
    const roomInput = document.getElementById('room-input');
    const roomIdElement = document.getElementById('room-id');
    const userCountElement = document.getElementById('user-count');
    const runCodeBtn = document.getElementById('run-code');
    const clearOutputBtn = document.getElementById('clear-output');
    const outputElement = document.getElementById('output');

    // Initialize CodeMirror
    editor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
        mode: 'python',
        theme: 'material',
        lineNumbers: true,
        indentUnit: 4,
        tabSize: 4,
        indentWithTabs: false,
        autoCloseBrackets: true,
        matchBrackets: true,
        extraKeys: {
            "Tab": function(cm) {
                cm.replaceSelection("    ", "end");
            }
        }
    });

    // Check if room ID is in URL
    const pathParts = window.location.pathname.split('/');
    if (pathParts.length > 1 && pathParts[1] !== '') {
        const roomFromUrl = pathParts[1];
        connectToRoom(roomFromUrl);
    }

    // Initialize Socket.IO connection
    function initSocketConnection() {
        if (socket) return;

        socket = io();

        socket.on('connect', () => {
            isConnected = true;
            console.log('Connected to server');
        });

        socket.on('disconnect', () => {
            isConnected = false;
            console.log('Disconnected from server');
        });

        socket.on('init_code', (data) => {
            if (isInitialLoad) {
                editor.setValue(data.code);
                isInitialLoad = false;
            }
        });

        socket.on('code_updated', (data) => {
            // Only update if we're not typing
            if (!isTyping) {
                const currentPosition = editor.getCursor();
                editor.setValue(data.code);
                editor.setCursor(currentPosition);
            }
        });

        socket.on('user_count', (data) => {
            userCountElement.textContent = `Users: ${data.count}`;
        });

        socket.on('code_result', (data) => {
            appendToOutput(data.result);
        });

        // Handle editor changes
        editor.on('change', (instance, changeObj) => {
            if (currentRoom && isConnected && !isInitialLoad) {
                clearTimeout(typingTimeout);
                isTyping = true;
                
                // Emit the code update after a brief pause in typing
                typingTimeout = setTimeout(() => {
                    socket.emit('code_update', {
                        room: currentRoom,
                        code: editor.getValue(),
                        position: editor.getCursor()
                    });
                    isTyping = false;
                }, 300);
            }
        });
    }

    // Connect to a room
    function connectToRoom(roomId) {
        initSocketConnection();
        
        if (currentRoom) {
            socket.emit('leave', { room: currentRoom });
        }
        
        currentRoom = roomId;
        isInitialLoad = true;
        roomIdElement.textContent = `Room: ${roomId}`;
        
        // Update URL without reloading the page
        history.pushState({}, '', `/${roomId}`);
        
        socket.emit('join', { room: roomId });
    }

    // Create a new room with a random ID
    createRoomBtn.addEventListener('click', () => {
        const randomRoomId = Math.random().toString(36).substring(2, 10);
        connectToRoom(randomRoomId);
    });

    // Join an existing room
    joinRoomBtn.addEventListener('click', () => {
        const roomId = roomInput.value.trim();
        if (roomId) {
            connectToRoom(roomId);
        }
    });

    // Allow Enter key to submit room ID
    roomInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            joinRoomBtn.click();
        }
    });

    // Run code
    runCodeBtn.addEventListener('click', () => {
        if (currentRoom && isConnected) {
            socket.emit('run_code', {
                room: currentRoom,
                code: editor.getValue()
            });
        } else {
            appendToOutput('Error: Not connected to a room');
        }
    });

    // Clear output
    clearOutputBtn.addEventListener('click', () => {
        outputElement.innerHTML = '';
    });

    // Helper function to append text to output
    function appendToOutput(text) {
        const outputLine = document.createElement('div');
        outputLine.textContent = text;
        outputElement.appendChild(outputLine);
        outputElement.scrollTop = outputElement.scrollHeight;
    }

    // Handle page unload
    window.addEventListener('beforeunload', () => {
        if (socket && currentRoom) {
            socket.emit('leave', { room: currentRoom });
        }
    });
});