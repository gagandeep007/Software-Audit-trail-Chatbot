document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatHistory = document.getElementById('chat-history');
    
    const browseBtn = document.getElementById('browse-btn');
    const fileInput = document.getElementById('file-input');
    const uploadZone = document.getElementById('upload-zone');
    const uploadStatus = document.getElementById('upload-status');
    const uploadStatusText = document.getElementById('upload-status-text');
    
    const awsLogGroup = document.getElementById('aws-log-group');
    const awsIngestBtn = document.getElementById('aws-ingest-btn');
    
    // Auto-scroll chat to bottom
    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // Handle sending message
    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;
        
        // Add user message
        const userMsg = document.createElement('div');
        userMsg.className = 'message user';
        userMsg.innerHTML = `<div class="content">${text}</div>`;
        chatHistory.appendChild(userMsg);
        
        chatInput.value = '';
        scrollToBottom();
        
        // Setup Bot Response block
        const botMsg = document.createElement('div');
        botMsg.className = 'message bot';
        botMsg.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="content"><span class="typing">...</span></div>
        `;
        chatHistory.appendChild(botMsg);
        scrollToBottom();
        
        const contentDiv = botMsg.querySelector('.content');
        
        // Stream from API
        try {
            const eventSource = new EventSource(`/api/chat?q=${encodeURIComponent(text)}`);
            let fullText = "";
            let firstChunk = true;
            
            eventSource.onmessage = function(event) {
                if (firstChunk) {
                    contentDiv.innerHTML = '';
                    firstChunk = false;
                }
                
                try {
                    const chunk = JSON.parse(event.data);
                    fullText += chunk;
                    
                    // Parse markdown safely
                    if (window.marked) {
                        contentDiv.innerHTML = marked.parse(fullText);
                    } else {
                        // Fallback
                        contentDiv.innerHTML = fullText.replace(/\\n/g, '<br>');
                    }
                } catch (e) {
                    console.error("Error parsing JSON chunk", e);
                }
                
                scrollToBottom();
            };
            
            eventSource.onerror = function() {
                eventSource.close();
            };
        } catch (error) {
            contentDiv.innerHTML = `Error connecting to chat server.`;
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Handle Local File Upload
    async function handleFileUpload(file) {
        uploadStatus.style.display = 'flex';
        uploadStatusText.textContent = 'Uploading and processing...';
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (response.ok) {
                uploadStatusText.textContent = 'Success!';
                uploadStatusText.style.color = '#10b981';
            } else {
                uploadStatusText.textContent = data.detail || 'Error uploading.';
                uploadStatusText.style.color = '#ef4444';
            }
        } catch (error) {
            uploadStatusText.textContent = 'Connection error.';
            uploadStatusText.style.color = '#ef4444';
        }
        
        setTimeout(() => {
            uploadStatus.style.display = 'none';
            uploadStatusText.style.color = 'inherit';
        }, 5000);
    }

    browseBtn.addEventListener('click', () => fileInput.click());
    
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleFileUpload(fileInput.files[0]);
        }
    });

    // Drag and drop UI
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });
    
    // Handle AWS CloudWatch Ingest
    awsIngestBtn.addEventListener('click', async () => {
        const logGroup = awsLogGroup.value.trim();
        if (!logGroup) {
            alert('Please enter a valid Log Group name.');
            return;
        }
        
        awsIngestBtn.textContent = 'Fetching...';
        awsIngestBtn.disabled = true;
        
        try {
            const response = await fetch('/api/ingest_aws', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ log_group: logGroup })
            });
            const data = await response.json();
            
            if (response.ok) {
                alert('Success: ' + data.message);
                awsLogGroup.value = '';
            } else {
                alert('Error: ' + (data.detail || 'Failed to fetch logs.'));
            }
        } catch (error) {
            alert('Connection error.');
        } finally {
            awsIngestBtn.textContent = 'Fetch & Ingest';
            awsIngestBtn.disabled = false;
        }
    });
});
