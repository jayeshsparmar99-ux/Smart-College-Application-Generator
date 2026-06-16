

// DOM Elements
const form = document.getElementById('applicationForm');
const generateBtn = document.getElementById('generateBtn');
const applicationOutput = document.getElementById('applicationOutput');
const actionButtons = document.getElementById('actionButtons');
const copyBtn = document.getElementById('copyBtn');
const downloadBtn = document.getElementById('downloadBtn');

// Set today's date as default for date input
const dateInput = document.getElementById('date');
if (dateInput) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
}

// Function to show loading state
function showLoading() {
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="loading"></span> Generating Application...';
    applicationOutput.innerHTML = `
        <div class="placeholder">
            <div class="placeholder-icon">🤖</div>
            <p>AI is generating your professional application...</p>
            <p style="font-size: 0.85rem; margin-top: 0.5rem;">This may take a few seconds</p>
        </div>
    `;
    actionButtons.style.display = 'none';
}

// Function to hide loading state
function hideLoading() {
    generateBtn.disabled = false;
    generateBtn.innerHTML = '<span class="btn-icon">✨</span> Generate Application with AI';
}

// Function to show error message
function showError(message) {
    applicationOutput.innerHTML = `
        <div class="placeholder">
            <div class="placeholder-icon">⚠️</div>
            <p style="color: #ef476f;">${message}</p>
            <p style="font-size: 0.85rem; margin-top: 0.5rem;">Please check your details and try again.</p>
        </div>
    `;
    actionButtons.style.display = 'none';
}

// Function to show success toast notification
function showToast(message, isError = false) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    toast.style.backgroundColor = isError ? '#ef476f' : '#06d6a0';
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Function to validate form
function validateForm(formData) {
    const requiredFields = ['student_name', 'enrollment_no', 'department', 'category', 'date', 'reason'];
    
    for (let field of requiredFields) {
        const value = formData.get(field);
        if (!value || value.trim() === '') {
            showError(`Please fill in the ${field.replace(/_/g, ' ')} field`);
            return false;
        }
    }
    
    // Validate enrollment number (at least 5 characters)
    const enrollmentNo = formData.get('enrollment_no');
    if (enrollmentNo.length < 5) {
        showError('Enrollment number must be at least 5 characters long');
        return false;
    }
    
    // Validate reason (at least 20 characters)
    const reason = formData.get('reason');
    if (reason.length < 20) {
        showError('Please provide a more detailed reason (at least 20 characters)');
        return false;
    }
    
    return true;
}

// Function to display generated application
function displayApplication(applicationText) {
    // Format the application text for display
    const formattedText = applicationText.replace(/\n/g, '<br>');
    applicationOutput.innerHTML = `<div class="application-content">${formattedText}</div>`;
    actionButtons.style.display = 'flex';
    
    // Store the application text for PDF download
    window.currentApplication = applicationText;
}

// Form submission handler
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form data
    const formData = new FormData(form);
    
    // Validate form
    if (!validateForm(formData)) {
        return;
    }
    
    // Show loading state
    showLoading();
    
    try {
        // Send data to backend
        const response = await fetch('/generate', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayApplication(data.application);
            showToast('Application generated successfully! ✨');
        } else {
            showError(data.error || 'Failed to generate application');
            showToast(data.error || 'Failed to generate application', true);
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Network error. Please check your connection and try again.');
        showToast('Network error. Please try again.', true);
    } finally {
        hideLoading();
    }
});

// Copy to clipboard functionality
copyBtn.addEventListener('click', async () => {
    if (!window.currentApplication) {
        showToast('No application to copy', true);
        return;
    }
    
    try {
        await navigator.clipboard.writeText(window.currentApplication);
        showToast('Application copied to clipboard! 📋');
        
        // Visual feedback on button
        copyBtn.innerHTML = '✅ Copied!';
        setTimeout(() => {
            copyBtn.innerHTML = '📋 Copy to Clipboard';
        }, 2000);
    } catch (err) {
        console.error('Failed to copy:', err);
        showToast('Failed to copy to clipboard', true);
    }
});

// Download PDF functionality
downloadBtn.addEventListener('click', async () => {
    if (!window.currentApplication) {
        showToast('No application to download', true);
        return;
    }
    
    // Show loading state on button
    const originalText = downloadBtn.innerHTML;
    downloadBtn.innerHTML = '⏳ Generating PDF...';
    downloadBtn.disabled = true;
    
    try {
        const response = await fetch('/download-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                application: window.currentApplication
            })
        });
        
        if (response.ok) {
            // Create blob from response
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'college_application.pdf';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showToast('PDF downloaded successfully! 📥');
        } else {
            showToast('Failed to download PDF. Please try again.', true);
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to download PDF. Please try again.', true);
    } finally {
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = originalText;
    }
});