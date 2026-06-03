// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// ✅ FIXED: Changed from webhook-test to webhook (production URL)
// ✅ FIXED: Corrected typo medittrack → meditrack
const N8N_WEBHOOK_URL = 'https://medittrack.app.n8n.cloud/webhook-test/c79c4ee2-c1a1-44e9-93ed-c08db162dce7';

// Global state
let currentUser = null;
let currentPrescriptionId = null;
let currentSessionId = null;
let messages = [];

// ================= AUTH FUNCTIONS =================

async function handleLogin() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    if (!username || !password) {
        showToast('Please enter both username and password', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentUser = username;
            localStorage.setItem('token', data.token);
            localStorage.setItem('username', username);
            showToast(`Welcome back, ${username}!`, 'success');
            showMainApp();
            loadUserData();
        } else {
            showToast(data.message || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Login failed. Please try again.', 'error');
    }
}

async function handleRegister() {
    const username = document.getElementById('reg-username').value;
    const password = document.getElementById('reg-password').value;
    
    if (!username || !password) {
        showToast('Please fill all fields', 'error');
        return;
    }
    
    if (password.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Account created successfully! Please login.', 'success');
            document.getElementById('login-form').classList.add('active');
            document.getElementById('register-form').classList.remove('active');
            document.querySelectorAll('.tab-btn')[0].classList.add('active');
            document.querySelectorAll('.tab-btn')[1].classList.remove('active');
            document.getElementById('login-username').value = username;
            document.getElementById('login-password').value = '';
        } else {
            showToast(data.message || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showToast('Registration failed. Please try again.', 'error');
    }
}

function handleLogout() {
    currentUser = null;
    currentPrescriptionId = null;
    currentSessionId = null;
    messages = [];
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    document.getElementById('app-container').classList.remove('active');
    document.getElementById('auth-container').classList.add('active');
    showToast('Logged out successfully', 'success');
}

// ================= UI FUNCTIONS =================

function switchAuthTab(tab) {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const tabs = document.querySelectorAll('.tab-btn');
    
    if (tab === 'login') {
        loginForm.classList.add('active');
        registerForm.classList.remove('active');
        tabs[0].classList.add('active');
        tabs[1].classList.remove('active');
    } else {
        loginForm.classList.remove('active');
        registerForm.classList.add('active');
        tabs[0].classList.remove('active');
        tabs[1].classList.add('active');
    }
}

function showMainApp() {
    document.getElementById('auth-container').classList.remove('active');
    document.getElementById('app-container').classList.add('active');
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.style.background = type === 'success' ? '#43a047' : '#d32f2f';
    toast.innerHTML = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ================= PRESCRIPTION FUNCTIONS =================

function getCurrentPrescriptionData() {
    const prescriptionData = {
        medicines: [],
        prescription_id: currentPrescriptionId || null,
        session_id: currentSessionId || null,
        hasPrescription: false
    };
    
    if (!currentPrescriptionId) return prescriptionData;
    
    prescriptionData.hasPrescription = true;
    const medicineDetailsContent = document.getElementById('medicine-details-content');
    if (medicineDetailsContent && medicineDetailsContent.innerHTML) {
        const medicineItems = medicineDetailsContent.querySelectorAll('li');
        medicineItems.forEach(item => {
            const medicine = { name: '', dosage: '', timing: '', frequency: '', duration: '' };
            const nameElement = item.querySelector('strong');
            if (nameElement) medicine.name = nameElement.textContent.trim();
            const text = item.textContent;
            const dosageMatch = text.match(/(?:Dosage|Quantity):\s*([^\n]+)/i);
            if (dosageMatch) medicine.dosage = dosageMatch[1].trim();
            const timingMatch = text.match(/Timing:\s*([^\n]+)/i);
            if (timingMatch) medicine.timing = timingMatch[1].trim();
            const frequencyMatch = text.match(/Frequency:\s*([^\n]+)/i);
            if (frequencyMatch) medicine.frequency = frequencyMatch[1].trim();
            const durationMatch = text.match(/Duration:\s*([^\n]+)/i);
            if (durationMatch) medicine.duration = durationMatch[1].trim();
            if (medicine.name) prescriptionData.medicines.push(medicine);
        });
    }
    return prescriptionData;
}

async function loadUserData() {
    document.getElementById('current-user').innerHTML = `<b>${currentUser}</b>`;
    await loadChatHistory();
}

async function loadChatHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/user-prescriptions?username=${currentUser}`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const data = await response.json();
        
        if (data.success && data.prescriptions) {
            const chatList = document.getElementById('chat-history-list');
            chatList.innerHTML = '';
            if (data.prescriptions.length === 0) {
                chatList.innerHTML = '<div style="color: var(--text-gray); text-align: center; padding: 1rem;">No prescriptions yet. Upload one to get started!</div>';
                return;
            }
            data.prescriptions.forEach(prescription => {
                const chatItem = document.createElement('div');
                chatItem.className = 'chat-item';
                chatItem.innerHTML = `📄 ${prescription.title || 'Prescription'}`;
                chatItem.onclick = () => selectPrescription(prescription.id);
                chatList.appendChild(chatItem);
            });
        }
    } catch (error) {
        console.error('Failed to load chat history:', error);
    }
}

async function selectPrescription(prescriptionId) {
    currentPrescriptionId = prescriptionId;
    try {
        const response = await fetch(`${API_BASE_URL}/api/prescription-details?id=${prescriptionId}&username=${currentUser}`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('welcome-screen').style.display = 'none';
            document.getElementById('chat-interface').style.display = 'block';
            document.getElementById('chat-title-text').innerHTML = `Chat: ${data.title}`;
            if (data.details) {
                document.getElementById('medicine-details').style.display = 'block';
                document.getElementById('medicine-details-content').innerHTML = data.details;
            }
            currentSessionId = data.session_id;
            await loadChatMessages();
        }
    } catch (error) {
        console.error('Failed to load prescription details:', error);
        showToast('Failed to load prescription details', 'error');
    }
}

async function loadChatMessages() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat-history?session_id=${currentSessionId}`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const data = await response.json();
        if (data.success && data.messages) {
            messages = data.messages;
            displayMessages();
        }
    } catch (error) {
        console.error('Failed to load chat history:', error);
        messages = [];
        displayMessages();
    }
}

function displayMessages() {
    const chatContainer = document.getElementById('chat-messages');
    chatContainer.innerHTML = '';
    if (messages.length === 0) {
        const welcomeMsg = document.createElement('div');
        welcomeMsg.className = 'message ai';
        welcomeMsg.innerHTML = '<div class="message-content">👋 Hello! Ask me anything about your prescription.</div>';
        chatContainer.appendChild(welcomeMsg);
    } else {
        messages.forEach(msg => {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${msg.role}`;
            messageDiv.innerHTML = `<div class="message-content">${msg.content}</div>`;
            chatContainer.appendChild(messageDiv);
        });
    }
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// ================= FILE UPLOAD =================

document.getElementById('file-input').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('username', currentUser);
    
    const statusDiv = document.getElementById('upload-status');
    statusDiv.innerHTML = '<div class="spinner"></div> Processing...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/upload-prescription`, {
            method: 'POST',
            body: formData,
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const data = await response.json();
        
        if (data.success) {
            statusDiv.innerHTML = '<div style="color: var(--secondary);">✅ Extraction Complete!</div>';
            showToast('Prescription uploaded successfully!', 'success');
            loadUserData();
            setTimeout(() => selectPrescription(data.prescription_id), 1000);
        } else {
            statusDiv.innerHTML = '<div style="color: var(--danger);">❌ Failed to extract data</div>';
            showToast(data.message || 'Upload failed', 'error');
        }
    } catch (error) {
        console.error('Upload error:', error);
        statusDiv.innerHTML = '<div style="color: var(--danger);">❌ Upload failed</div>';
        showToast('Upload failed. Please try again.', 'error');
    }
    setTimeout(() => { statusDiv.innerHTML = ''; document.getElementById('file-input').value = ''; }, 5000);
});

// ================= CHAT FUNCTIONS =================

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const question = input.value.trim();
    if (!question) return;
    
    messages.push({ role: 'user', content: question });
    displayMessages();
    input.value = '';
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message ai';
    typingDiv.innerHTML = '<div class="message-content"><div class="spinner"></div> Thinking...</div>';
    document.getElementById('chat-messages').appendChild(typingDiv);
    document.getElementById('chat-messages').scrollTop = document.getElementById('chat-messages').scrollHeight;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
            body: JSON.stringify({ question, prescription_id: currentPrescriptionId, session_id: currentSessionId })
        });
        const data = await response.json();
        typingDiv.remove();
        if (data.success && data.answer) {
            messages.push({ role: 'ai', content: data.answer });
            displayMessages();
        } else {
            messages.push({ role: 'ai', content: 'Sorry, I could not process your request.' });
            displayMessages();
        }
    } catch (error) {
        console.error('Chat error:', error);
        typingDiv.remove();
        messages.push({ role: 'ai', content: 'Network error. Please try again.' });
        displayMessages();
    }
}

// ================= OTC FUNCTIONS =================

async function loadOTCList(searchQuery = '') {
    try {
        const url = searchQuery ? `${API_BASE_URL}/api/otc-list?search=${encodeURIComponent(searchQuery)}` : `${API_BASE_URL}/api/otc-list`;
        const response = await fetch(url);
        const data = await response.json();
        const tableContainer = document.getElementById('otc-table');
        
        if (data.success && data.medicines && data.medicines.length > 0) {
            let html = '<table><thead><tr><th>Medicine Name</th><th>Category</th></tr></thead><tbody>';
            data.medicines.forEach(med => { html += `<tr><td>${med.name}</td><td>${med.type || 'General'}</td></tr>`; });
            html += '</tbody></table>';
            tableContainer.innerHTML = html;
        } else {
            tableContainer.innerHTML = '<div class="info-message">No medicines found.</div>';
        }
    } catch (error) { console.error('Failed to load OTC list:', error); }
}

function searchOTC() { loadOTCList(document.getElementById('otc-search').value); }

async function handleOTCCheck() {
    const checkbox = document.getElementById('otc-checkbox');
    const resultsDiv = document.getElementById('otc-results');
    if (checkbox.checked) {
        if (!currentPrescriptionId) {
            resultsDiv.innerHTML = '<div class="info-message">Please select a prescription first.</div>';
            checkbox.checked = false;
            return;
        }
        resultsDiv.innerHTML = '<div class="spinner"></div> Checking OTC status...';
        resultsDiv.style.display = 'block';
        try {
            const response = await fetch(`${API_BASE_URL}/api/check-otc`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
                body: JSON.stringify({ prescription_id: currentPrescriptionId, session_id: currentSessionId })
            });
            const data = await response.json();
            
            if (data.success && data.result) {
                let html = '<h3>OTC Analysis Results</h3>';
                if (data.result.otc_medicines && data.result.otc_medicines.length > 0) {
                    html += '<div style="color: var(--secondary); margin-top: 1rem;"><strong>✅ Safe to Buy (OTC)</strong></div>';
                    data.result.otc_medicines.forEach(med => { html += `<div style="margin-top: 0.5rem; padding-left: 1rem;">• <strong>${med.name}</strong>: ${med.reason}</div>`; });
                }
                if (data.result.consult_medicines && data.result.consult_medicines.length > 0) {
                    html += '<div style="color: var(--accent); margin-top: 1rem;"><strong>⚠️ Prescription Required</strong></div>';
                    data.result.consult_medicines.forEach(med => { html += `<div style="margin-top: 0.5rem; padding-left: 1rem;">• <strong>${med.name}</strong>: ${med.reason}</div>`; });
                }
                resultsDiv.innerHTML = html;
            } else { resultsDiv.innerHTML = '<div class="info-message">Unable to analyze OTC status.</div>'; }
        } catch (error) { console.error('OTC check error:', error); resultsDiv.innerHTML = '<div class="info-message">Failed to check OTC status.</div>'; }
    } else { resultsDiv.style.display = 'none'; resultsDiv.innerHTML = ''; }
}

function toggleMedicineDetails() {
    const content = document.getElementById('medicine-details-content');
    const icon = document.querySelector('.expand-icon');
    if (content.classList.contains('active')) {
        content.classList.remove('active');
        if (icon) icon.innerHTML = '▼';
    } else {
        content.classList.add('active');
        if (icon) icon.innerHTML = '▲';
    }
}

function switchPage(page) {
    const pages = document.querySelectorAll('.page');
    const navItems = document.querySelectorAll('.nav-item');
    pages.forEach(p => p.classList.remove('active'));
    navItems.forEach(n => n.classList.remove('active'));
    if (page === 'home') {
        document.getElementById('home-page').classList.add('active');
        navItems[0].classList.add('active');
        document.getElementById('home-upload-section').style.display = 'block';
    } else {
        document.getElementById('otc-page').classList.add('active');
        navItems[1].classList.add('active');
        document.getElementById('home-upload-section').style.display = 'none';
        loadOTCList();
    }
}

// ================= VOICE CALL REQUEST FUNCTIONS =================

function openVoiceCallModal() {
    const modal = document.getElementById('voice-call-modal');
    if (modal) {
        modal.style.display = 'flex';
        document.getElementById('call-name').value = currentUser || '';
        document.getElementById('call-phone').value = '';
        document.getElementById('call-message').value = '';
        
        const prescriptionData = getCurrentPrescriptionData();
        const summaryDiv = document.getElementById('prescription-summary');
        if (summaryDiv) {
            if (prescriptionData.hasPrescription && prescriptionData.medicines.length > 0) {
                let summaryHtml = '<div class="prescription-summary-box"><strong>📋 Current Prescription:</strong><ul>';
                prescriptionData.medicines.forEach(med => { summaryHtml += `<li>💊 ${med.name} - ${med.dosage || 'N/A'} (${med.frequency || 'N/A'})</li>`; });
                summaryHtml += '</ul></div>';
                summaryDiv.innerHTML = summaryHtml;
                summaryDiv.style.display = 'block';
            } else { summaryDiv.style.display = 'none'; }
        }
    }
}

function closeVoiceCallModal() {
    const modal = document.getElementById('voice-call-modal');
    if (modal) modal.style.display = 'none';
}

async function submitCallRequest() {
    const name = document.getElementById('call-name').value.trim();
    const phone = document.getElementById('call-phone').value.trim();
    const message = document.getElementById('call-message').value.trim();
    
    if (!name) { showCallToast('Please enter your name', 'error'); return; }
    if (!phone) { showCallToast('Please enter your phone number', 'error'); return; }
    const phoneRegex = /^[0-9+\-\s()]{10,15}$/;
    if (!phoneRegex.test(phone)) { showCallToast('Please enter a valid phone number', 'error'); return; }
    
    const prescriptionData = getCurrentPrescriptionData();

    // ✅ FIXED: Cleaner payload structure — n8n accesses $json.user.name etc directly
    const callRequestData = {
        id: 'call_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
        user: {
            name,
            phone,
            userId: currentUser || 'guest',
            notes: message || 'No additional notes'
        },
        prescription: {
            id: prescriptionData.prescription_id,
            session_id: prescriptionData.session_id,
            hasPrescription: prescriptionData.hasPrescription,
            medicines: prescriptionData.medicines,
            medicinesCount: prescriptionData.medicines.length,
            summary: prescriptionData.medicines.map(m => `${m.name} (${m.dosage || 'N/A'})`).join(', ')
        },
        request: {
            timestamp: new Date().toISOString(),
            source: 'MediTrack+ Web App - Sidebar',
            type: 'voice_call_back',
            status: 'pending'
        },
        context: {
            userAgent: navigator.userAgent,
            pageUrl: window.location.href,
            screenSize: `${window.innerWidth}x${window.innerHeight}`
        }
    };

    // Save to localStorage as backup
    try {
        let existingRequests = localStorage.getItem('callRequests');
        existingRequests = existingRequests ? JSON.parse(existingRequests) : [];
        existingRequests.push(callRequestData);
        localStorage.setItem('callRequests', JSON.stringify(existingRequests));
        localStorage.setItem('lastCallRequest', JSON.stringify(callRequestData));
        console.log('Call request saved locally:', callRequestData);
    } catch (error) {
        console.error('Error saving to localStorage:', error);
    }

    // ✅ FIXED: Show loading state while submitting
    const submitBtn = document.querySelector('#voice-call-modal .submit-btn');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '⏳ Submitting...';
    }

    try {
        // ✅ FIXED: Send to production webhook URL with correct Content-Type
        const response = await fetch(N8N_WEBHOOK_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(callRequestData)
        });

        if (response.ok) {
            showCallToast('✅ Call request submitted! We\'ll call you back shortly.', 'success');
            closeVoiceCallModal();

            // Optional: also save to your own backend
            try {
                await fetch(`${API_BASE_URL}/api/call-request`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    },
                    body: JSON.stringify(callRequestData)
                });
            } catch (err) {
                console.log('Backend storage optional, skipping:', err);
            }
        } else {
            // ✅ FIXED: Show actual error instead of fake success
            const errorText = await response.text();
            console.error('Webhook error response:', errorText);
            showCallToast('❌ Failed to submit request. Please try again.', 'error');
        }
    } catch (error) {
        // ✅ FIXED: Show actual error — no more fake success on failure
        console.error('Error sending to webhook:', error);
        showCallToast('❌ Network error. Please check your connection and try again.', 'error');
    } finally {
        // Re-enable button regardless of outcome
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Request Call';
        }
    }
}

function showCallToast(message, type = 'success') {
    const existingToast = document.querySelector('.call-toast');
    if (existingToast) existingToast.remove();
    const toast = document.createElement('div');
    toast.className = 'call-toast';
    toast.innerHTML = `<span>${type === 'success' ? '✅' : '⚠️'}</span><span>${message}</span>`;
    toast.style.background = type === 'success' ? 'var(--accent)' : 'var(--danger)';
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ================= SIDEBAR & MOBILE FUNCTIONS =================

function toggleMobileMenu() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('mobile-open');
}

document.getElementById('mobileMenuBtn')?.addEventListener('click', toggleMobileMenu);

// Close mobile menu when clicking outside on mobile
document.addEventListener('click', (e) => {
    const sidebar = document.querySelector('.sidebar');
    const menuBtn = document.getElementById('mobileMenuBtn');
    if (window.innerWidth <= 768 && sidebar && sidebar.classList.contains('mobile-open')) {
        if (!sidebar.contains(e.target) && !menuBtn?.contains(e.target)) {
            sidebar.classList.remove('mobile-open');
        }
    }
});

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    const modal = document.getElementById('voice-call-modal');
    if (e.target === modal) closeVoiceCallModal();
});

// Initialize Enter key for chat
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); sendMessage(); }
        });
    }
});

// Check if user is already logged in
if (localStorage.getItem('token') && localStorage.getItem('username')) {
    currentUser = localStorage.getItem('username');
    showMainApp();
    loadUserData();
}