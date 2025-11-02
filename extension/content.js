function extractLinkedInJobData() {
  try {
    // Wait for page to load
    const checkElement = setInterval(() => {
      const titleElement = document.querySelector('.job-details-jobs-unified-top-card__job-title');
      
      if (titleElement) {
        clearInterval(checkElement);
        
        // Extract job details
        const jobTitle = titleElement?.innerText?.trim() || '';
        
        const companyElement = document.querySelector('.job-details-jobs-unified-top-card__company-name');
        const companyName = companyElement?.innerText?.trim() || '';
        
        const locationElement = document.querySelector('.job-details-jobs-unified-top-card__bullet');
        const location = locationElement?.innerText?.trim() || '';
        
        // Job description - THE FIX IS HERE
        let jobDescription = '';
        
        // Target the actual content div
        const descElement = document.querySelector('.jobs-box__html-content') ||
                           document.querySelector('.jobs-description-content__text--stretch') ||
                           document.querySelector('article.jobs-description__container');
        
        if (descElement) {
          jobDescription = descElement.innerText?.trim() || '';
          console.log('Found description element, length:', jobDescription.length);
        } else {
          console.log('Description element not found');
        }
        
        // Salary (if available)
        const salaryElements = document.querySelectorAll('.job-details-jobs-unified-top-card__job-insight');
        let salary = '';
        salaryElements.forEach(el => {
          const text = el.innerText?.trim();
          if (text && (text.includes('$') || text.includes('salary'))) {
            salary = text;
          }
        });
        
        // Current URL
        const jobUrl = window.location.href;
        
        const jobData = {
          company_name: companyName,
          job_title: jobTitle,
          job_url: jobUrl,
          job_description: jobDescription,
          location: location,
          salary_range: salary || null,
          scraped: true,
          source: 'linkedin'
        };
        
        console.log('LinkedIn job data extracted:', jobData);
        console.log('Description preview:', jobDescription.substring(0, 200));
        
        // Send to background script
        chrome.runtime.sendMessage({
          action: 'jobDataExtracted',
          data: jobData
        });
      }
    }, 1000);
    
    // Stop checking after 15 seconds
    setTimeout(() => clearInterval(checkElement), 15000);
    
  } catch (error) {
    console.error('Error extracting LinkedIn job data:', error);
  }
}

// Run extraction when page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', extractLinkedInJobData);
} else {
  extractLinkedInJobData();
}

// Listen for URL changes (LinkedIn is SPA)
let lastUrl = location.href;
new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    if (url.includes('/jobs/view/')) {
      setTimeout(extractLinkedInJobData, 2000);
    }
  }
}).observe(document, { subtree: true, childList: true });