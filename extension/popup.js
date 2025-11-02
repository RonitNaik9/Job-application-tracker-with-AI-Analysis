const API_URL = 'http://localhost:8000/api/v1';

// DOM Elements
const authSection = document.getElementById('auth-section');
const mainSection = document.getElementById('main-section');
const loginBtn = document.getElementById('login-btn');
const logoutBtn = document.getElementById('logout-btn');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const authError = document.getElementById('auth-error');

// Resume elements
const resumeTab = document.getElementById('resume-tab');
const noResume = document.getElementById('no-resume');
const hasResume = document.getElementById('has-resume');
const resumeFile = document.getElementById('resume-file');
const uploadResumeBtn = document.getElementById('upload-resume-btn');
const resumeStatus = document.getElementById('resume-status');
const updateResumeBtn = document.getElementById('update-resume-btn');
const resumeFileUpdate = document.getElementById('resume-file-update');
const resumeFilename = document.getElementById('resume-filename');

// Job elements
const saveJobBtn = document.getElementById('save-job-btn');
const jobStatus = document.getElementById('job-status');

// Check for scraped job data when popup opens
chrome.storage.local.get(['scrapedJobData', 'scrapedAt'], (result) => {
  if (result.scrapedJobData) {
    const scrapedAt = new Date(result.scrapedAt);
    const now = new Date();
    const minutesAgo = (now - scrapedAt) / 1000 / 60;
    
    // Only use data if scraped within last 5 minutes
    if (minutesAgo < 5) {
      autoFillJobForm(result.scrapedJobData);
    }
  }
});

// Listen for new scraped data
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'jobDataReady') {
    autoFillJobForm(request.data);
    
    // Switch to job tab automatically
    document.querySelector('.tab-btn[data-tab="job"]').click();
    
    // Show notification
    jobStatus.textContent = '✨ Job details auto-filled from LinkedIn!';
    jobStatus.style.color = 'green';
    
    sendResponse({ success: true });
  }
  return true;
});

function autoFillJobForm(jobData) {
  if (jobData.company_name) {
    document.getElementById('company').value = jobData.company_name;
  }
  if (jobData.job_title) {
    document.getElementById('job-title').value = jobData.job_title;
  }
  if (jobData.job_url) {
    document.getElementById('job-url').value = jobData.job_url;
  }
  if (jobData.job_description) {
    document.getElementById('job-description').value = jobData.job_description;
  }
  if (jobData.location) {
    document.getElementById('location').value = jobData.location;
  }
  if (jobData.salary_range) {
    document.getElementById('salary').value = jobData.salary_range;
  }
  
  const indicator = document.getElementById('auto-fill-indicator');
  if (indicator) {
    indicator.style.display = 'block';
  }
  
  console.log('Form auto-filled with scraped data');
}

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const tabName = btn.dataset.tab;
    
    // Update active tab button
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    // Update active tab content
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`${tabName}-tab`).classList.add('active');
  });
});

// Check if user is logged in
chrome.storage.local.get(['token', 'hasResume'], (result) => {
  if (result.token) {
    showMainSection();
    if (result.hasResume) {
      showResumeUploaded(result.hasResume);
    }
  }
});

// Login
loginBtn.addEventListener('click', async () => {
  const email = emailInput.value;
  const password = passwordInput.value;
  
  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    if (!response.ok) {
      throw new Error('Login failed');
    }
    
    const data = await response.json();
    chrome.storage.local.set({ token: data.access_token }, () => {
      showMainSection();
      checkForResume(data.access_token);
    });
  } catch (error) {
    authError.textContent = 'Invalid email or password';
  }
});

// Logout
logoutBtn.addEventListener('click', () => {
  chrome.storage.local.clear(() => {
    authSection.style.display = 'block';
    mainSection.style.display = 'none';
  });
});

// Upload Resume
uploadResumeBtn.addEventListener('click', async () => {
  const file = resumeFile.files[0];
  if (!file) {
    resumeStatus.textContent = 'Please select a PDF file';
    resumeStatus.style.color = 'red';
    return;
  }
  
  chrome.storage.local.get(['token'], async (result) => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      resumeStatus.textContent = 'Uploading...';
      resumeStatus.style.color = 'blue';
      
      const response = await fetch(`${API_URL}/resumes/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${result.token}`
        },
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Upload failed');
      }
      
      const data = await response.json();
      chrome.storage.local.set({ hasResume: file.name });
      showResumeUploaded(file.name);
      resumeStatus.textContent = 'Resume uploaded successfully!';
      resumeStatus.style.color = 'green';
    } catch (error) {
      resumeStatus.textContent = 'Upload failed. Try again.';
      resumeStatus.style.color = 'red';
    }
  });
});

// Update Resume
updateResumeBtn.addEventListener('click', () => {
  resumeFileUpdate.click();
});

resumeFileUpdate.addEventListener('change', async () => {
  const file = resumeFileUpdate.files[0];
  if (!file) return;
  
  chrome.storage.local.get(['token'], async (result) => {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      resumeStatus.textContent = 'Updating...';
      resumeStatus.style.color = 'blue';
      
      const response = await fetch(`${API_URL}/resumes/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${result.token}`
        },
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Upload failed');
      }
      
      chrome.storage.local.set({ hasResume: file.name });
      showResumeUploaded(file.name);
      resumeStatus.textContent = 'Resume updated successfully!';
      resumeStatus.style.color = 'green';
    } catch (error) {
      resumeStatus.textContent = 'Update failed. Try again.';
      resumeStatus.style.color = 'red';
    }
  });
});

// Save Job Application
saveJobBtn.addEventListener('click', async () => {
  const company = document.getElementById('company').value;
  const jobTitle = document.getElementById('job-title').value;
  const jobUrl = document.getElementById('job-url').value;
  const jobDescription = document.getElementById('job-description').value;
  const location = document.getElementById('location').value;
  const salary = document.getElementById('salary').value;
  const dateApplied = document.getElementById('date-applied').value;
  
  if (!company || !jobTitle || !dateApplied) {
    jobStatus.textContent = 'Please fill required fields';
    jobStatus.style.color = 'red';
    return;
  }
  
  chrome.storage.local.get(['token'], async (result) => {
    try {
      jobStatus.textContent = 'Saving...';
      jobStatus.style.color = 'blue';
      
      const response = await fetch(`${API_URL}/applications`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${result.token}`
        },
        body: JSON.stringify({
          company_name: company,
          job_title: jobTitle,
          job_url: jobUrl || null,
          job_description: jobDescription || null,
          location: location || null,
          salary_range: salary || null,
          date_applied: dateApplied,
          notes: null
        })
      });
      
      if (!response.ok) {
        throw new Error('Save failed');
      }
      
      jobStatus.textContent = 'Application saved! AI analysis in progress...';
      jobStatus.style.color = 'green';
      
      // Clear form
      document.getElementById('company').value = '';
      document.getElementById('job-title').value = '';
      document.getElementById('job-url').value = '';
      document.getElementById('job-description').value = '';
      document.getElementById('location').value = '';
      document.getElementById('salary').value = '';
    } catch (error) {
      jobStatus.textContent = 'Failed to save. Try again.';
      jobStatus.style.color = 'red';
    }
  });
});

// Helper functions
function showMainSection() {
  authSection.style.display = 'none';
  mainSection.style.display = 'block';
}

function showResumeUploaded(filename) {
  noResume.style.display = 'none';
  hasResume.style.display = 'block';
  resumeFilename.textContent = `File: ${filename}`;
}

async function checkForResume(token) {
  try {
    const response = await fetch(`${API_URL}/resumes/active`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (response.ok) {
      const data = await response.json();
      chrome.storage.local.set({ hasResume: data.file_url || 'resume.pdf' });
      showResumeUploaded(data.file_url || 'resume.pdf');
    }
  } catch (error) {
    // No resume found
  }
}

// Set today's date as default
document.getElementById('date-applied').valueAsDate = new Date();