// File selection handling
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const fileName = document.getElementById('fileName');
    const selectedFileName = document.getElementById('selectedFileName');
    const fileSize = document.getElementById('fileSize');
    const fileType = document.getElementById('fileType');
    const fileInfo = document.getElementById('fileInfo');

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            if (this.files.length > 0) {
                const file = this.files[0];
                const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
                const fileSizeKB = (file.size / 1024).toFixed(2);
                
                // Update interface
                fileName.textContent = file.name;
                selectedFileName.textContent = file.name;
                
                // Format size
                if (file.size < 1024) {
                    fileSize.textContent = `${file.size} B`;
                } else if (file.size < 1048576) {
                    fileSize.textContent = `${fileSizeKB} KB`;
                } else {
                    fileSize.textContent = `${fileSizeMB} MB`;
                }
                
                // Get file type
                const extension = file.name.split('.').pop().toUpperCase();
                fileType.textContent = `.${extension} file`;
                
                // Show info
                fileInfo.style.display = 'block';
                
                // Check size
                if (file.size > 100 * 1024 * 1024) {
                    alert('⚠️ File too large! Maximum size is 100MB');
                    this.value = '';
                    resetFileInfo();
                }
            } else {
                resetFileInfo();
            }
        });
    }

    // Copy file ID to clipboard
    document.querySelectorAll('.file-id code').forEach(element => {
        element.addEventListener('click', function() {
            const fileId = this.textContent.includes('...') 
                ? this.getAttribute('title') 
                : this.textContent;
            
            navigator.clipboard.writeText(fileId).then(() => {
                // Visual feedback
                const originalText = this.textContent;
                const originalColor = this.style.background;
                
                this.textContent = '✅ Copied!';
                this.style.background = '#28a745';
                this.style.color = 'white';
                
                setTimeout(() => {
                    this.textContent = originalText;
                    this.style.background = originalColor;
                    this.style.color = '';
                }, 1500);
            }).catch(err => {
                console.error('Failed to copy: ', err);
            });
        });
    });

    // Auto-hide alerts after 7 seconds
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            alert.style.transition = 'opacity 0.5s, transform 0.5s';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 500);
        });
    }, 7000);

    // Initialize tooltips
    initTooltips();
});

function resetFileInfo() {
    document.getElementById('fileName').textContent = 'Choose a file to encrypt...';
    document.getElementById('fileInfo').style.display = 'none';
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show toast notification
        showToast('File ID copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy: ', err);
        alert('Failed to copy to clipboard. Please copy manually.');
    });
}

function showToast(message) {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 300);
    }, 3000);
}

function initTooltips() {
    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        .toast {
            font-family: 'Poppins', sans-serif;
            font-weight: 500;
        }
    `;
    document.head.appendChild(style);
}

// File size formatting helper
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Confirm before refresh if upload in progress
let uploadInProgress = false;
window.addEventListener('beforeunload', function(e) {
    if (uploadInProgress) {
        e.preventDefault();
        e.returnValue = 'File upload is in progress. Are you sure you want to leave?';
    }
});

// Set upload flag when form is submitted
document.addEventListener('submit', function(e) {
    if (e.target.classList.contains('upload-form')) {
        uploadInProgress = true;
        // Show loading indicator
        const submitBtn = e.target.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Encrypting...';
            submitBtn.disabled = true;
        }
    }
});