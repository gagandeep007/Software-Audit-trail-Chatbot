document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatHistory = document.getElementById('chat-history');
    
    const browseBtn = document.getElementById('browse-btn');
    const fileInput = document.getElementById('file-input');
    const uploadZone = document.getElementById('upload-zone');
    
    // Auto-scroll chat to bottom
    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // Handle sending message
    function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;
        
        // Add user message
        const userMsg = document.createElement('div');
        userMsg.className = 'message user';
        userMsg.innerHTML = `<div class="content">${text}</div>`;
        chatHistory.appendChild(userMsg);
        
        chatInput.value = '';
        scrollToBottom();
        
        // Mock Bot Response
        setTimeout(() => {
            const botMsg = document.createElement('div');
            botMsg.className = 'message bot';
            botMsg.innerHTML = `
                <div class="avatar"><i class="fa-solid fa-robot"></i></div>
                <div class="content">This is a mockup! I am echoing back your text: <br><br><em>"${text}"</em><br><br>Once you approve the design, I'll connect it to the real RAG backend!</div>
            `;
            chatHistory.appendChild(botMsg);
            scrollToBottom();
        }, 600);
    }

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Handle file upload UI
    browseBtn.addEventListener('click', () => fileInput.click());
    
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            browseBtn.textContent = fileInput.files[0].name;
            browseBtn.style.background = 'rgba(16, 185, 129, 0.2)';
            browseBtn.style.borderColor = '#10b981';
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
            fileInput.files = e.dataTransfer.files;
            browseBtn.textContent = e.dataTransfer.files[0].name;
            browseBtn.style.background = 'rgba(16, 185, 129, 0.2)';
            browseBtn.style.borderColor = '#10b981';
        }
    });
});
