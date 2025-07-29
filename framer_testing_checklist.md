## Framer Page Testing Checklist

### Testing Instructions:
1. Open browser Developer Tools (F12 or Cmd+Option+I)
2. Go to Console tab
3. Visit each URL
4. Check for console messages and run test commands

### Pages to Test:

#### ✅ Homepage: https://lubobali.com/
- [ ] Console shows: "Portfolio Tracker initialized for page: home"
- [ ] Run: `window.portfolioTracker.pageName` → Should return: "home"
- [ ] Run: `window.portfolioTracker` → Should return tracker object

#### ✅ Portfolio: https://lubobali.com/portfolio
- [ ] Console shows: "Portfolio Tracker initialized for page: /portfolio"
- [ ] Run: `window.portfolioTracker.pageName` → Should return: "/portfolio"
- [ ] Run: `window.portfolioTracker` → Should return tracker object

#### ✅ About Me: https://lubobali.com/about-me
- [ ] Console shows: "Portfolio Tracker initialized for page: /about-me"
- [ ] Run: `window.portfolioTracker.pageName` → Should return: "/about-me"
- [ ] Run: `window.portfolioTracker` → Should return tracker object

#### ✅ Contact: https://lubobali.com/contact
- [ ] Console shows: "Portfolio Tracker initialized for page: /contact"
- [ ] Run: `window.portfolioTracker.pageName` → Should return: "/contact"
- [ ] Run: `window.portfolioTracker` → Should return tracker object

#### ✅ Resume: https://lubobali.com/resume
- [ ] Console shows: "Portfolio Tracker initialized for page: /resume"
- [ ] Run: `window.portfolioTracker.pageName` → Should return: "/resume"
- [ ] Run: `window.portfolioTracker` → Should return tracker object

#### ✅ CVS Contractor Performance: https://lubobali.com/cvs-contractor-performance
- [ ] Console shows: "Portfolio Tracker initialized for page: /cvs-contractor-performance"
- [ ] Run: `window.portfolioTracker.pageName` → Should return: "/cvs-contractor-performance"
- [ ] Run: `window.portfolioTracker` → Should return tracker object

#### ✅ CVS Pipeline: https://lubobali.com/cvs-pipeline
- [ ] Console shows: "Portfolio Tracker initialized for page: /cvs-pipeline"
- [ ] Run: `window.portfolioTracker.pageName` → Should return: "/cvs-pipeline"
- [ ] Run: `window.portfolioTracker` → Should return tracker object

#### ✅ Supply Chain: https://lubobali.com/supply-chain
- [ ] Console shows: "Portfolio Tracker initialized for page: /supply-chain"
- [ ] Run: `window.portfolioTracker.pageName` → Should return: "/supply-chain"
- [ ] Run: `window.portfolioTracker` → Should return tracker object

#### ✅ IBM: https://lubobali.com/ibm
- [ ] Console shows: "Portfolio Tracker initialized for page: /ibm"
- [ ] Run: `window.portfolioTracker.pageName` → Should return: "/ibm"
- [ ] Run: `window.portfolioTracker` → Should return tracker object

### Common Issues & Solutions:

#### ❌ If you see NO console messages:
- Script is not embedded or not in the right place
- Check Site Settings > Custom Code > Head tag
- Make sure script is wrapped in `<script>` tags

#### ❌ If you see "window.portfolioTracker is undefined":
- Script failed to load or execute
- Check for JavaScript errors in console
- Verify script syntax is correct

#### ❌ If wrong page_name is returned:
- Script is working but extracting wrong value
- This shouldn't happen with current script, but let me know

#### ❌ If some pages work, others don't:
- Script might be in page-specific custom code instead of site-wide
- Move script to Site Settings > Custom Code > Head tag

### Quick Test Commands:
Copy and paste these in console on each page:

```javascript
// Check if tracker exists
console.log('Tracker exists:', typeof window.portfolioTracker !== 'undefined');

// Check current page name
console.log('Page name:', window.portfolioTracker?.pageName);

// Check session ID
console.log('Session ID:', window.portfolioTracker?.sessionId);

// Manually trigger tracking (to test API connection)
if (window.portfolioTracker) {
    window.portfolioTracker.trackClick();
    console.log('Manual tracking triggered');
}
```

### Notes:
- Test in incognito/private browsing to avoid cache issues
- Clear browser cache if you've made recent changes
- Check Network tab to see if API calls are being made successfully
