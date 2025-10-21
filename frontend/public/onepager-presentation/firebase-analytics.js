// Firebase Analytics for AxWise One-Pager Presentation

// Load Firebase scripts
document.addEventListener('DOMContentLoaded', function() {
  // Load Firebase scripts dynamically
  const firebaseAppScript = document.createElement('script');
  firebaseAppScript.src = 'https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js';
  firebaseAppScript.type = 'module';

  const firebaseAnalyticsScript = document.createElement('script');
  firebaseAnalyticsScript.src = 'https://www.gstatic.com/firebasejs/10.8.0/firebase-analytics.js';
  firebaseAnalyticsScript.type = 'module';

  // Initialize Firebase after scripts are loaded
  firebaseAppScript.onload = function() {
    document.head.appendChild(firebaseAnalyticsScript);
  };

  firebaseAnalyticsScript.onload = function() {
    initializeFirebase();
  };

  document.head.appendChild(firebaseAppScript);
});

// Initialize Firebase
function initializeFirebase() {
  // Your web app's Firebase configuration
  const firebaseConfig = {
    apiKey: "YOUR_FIREBASE_API_KEY",
    authDomain: "axwise-73425.firebaseapp.com",
    projectId: "axwise-73425",
    storageBucket: "axwise-73425.appspot.com",
    messagingSenderId: "1098040621778",
    appId: "1:1098040621778:web:e1a0e0a7f7f2c8b8b8b8b8",
    measurementId: "G-MEASUREMENT_ID" // Replace with your actual measurement ID
  };

  // Initialize Firebase
  firebase.initializeApp(firebaseConfig);
  const analytics = firebase.analytics();

  // Make analytics available globally
  window.analytics = analytics;

  // Track key conversion events
  trackConversionEvents();
}

// Track the most important conversion events
function trackConversionEvents() {
  // Track the main CTA button (Contact Us)
  const ctaButton = document.querySelector('.c-cta__button');
  if (ctaButton) {
    ctaButton.addEventListener('click', function() {
      console.log('Tracking contact_us_click event');
      window.analytics.logEvent('contact_us_click', {
        link_location: 'final_cta',
        link_url: 'mailto:vitalijs@axwise.de',
        link_text: 'Contact Us'
      });
    });
  }

  // Track the header CTA button (Join Us)
  const headerButton = document.querySelector('.c-header .c-button');
  if (headerButton) {
    headerButton.addEventListener('click', function() {
      console.log('Tracking join_us_click event');
      window.analytics.logEvent('join_us_click', {
        link_location: 'header',
        link_url: '#cta',
        link_text: 'Join Us'
      });
    });
  }

  // Track team member clicks (important for VC interest)
  const teamMembers = document.querySelectorAll('.c-team__member');
  teamMembers.forEach(member => {
    member.addEventListener('click', function() {
      const memberName = member.querySelector('.c-team__member-name')?.textContent || 'Unknown Member';
      console.log(`Tracking team_member_click event: ${memberName}`);
      window.analytics.logEvent('team_member_click', {
        member_name: memberName,
        section: 'team_section'
      });
    });
  });
}

// Export a simplified analytics interface
window.axwiseAnalytics = {
  logEvent: function(eventName, params) {
    if (window.analytics) {
      console.log(`Logging event: ${eventName}`, params);
      window.analytics.logEvent(eventName, params);
    } else {
      console.error('Analytics not initialized yet');
    }
  }
};
