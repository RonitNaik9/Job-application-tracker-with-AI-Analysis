// background.js

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'jobDataExtracted') {
    console.log('Job data received in background:', request.data);
    
    // Store the scraped job data
    chrome.storage.local.set({ 
      scrapedJobData: request.data,
      scrapedAt: new Date().toISOString()
    }, () => {
      console.log('Job data stored');
      
      // Notify popup if it's open
      chrome.runtime.sendMessage({
        action: 'jobDataReady',
        data: request.data
      }).catch(() => {
        // Popup might not be open, that's okay
      });
    });
    
    sendResponse({ success: true });
  }
  return true;
});

console.log('Job Tracker extension loaded');