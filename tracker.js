/**
 * Portfolio Click Tracker for lubobali.com
 * Collects user engagement data and sends to FastAPI backend
 * Uses navigator.sendBeacon for reliable data transmission
 */

class PortfolioTracker {
    constructor(apiEndpoint = 'https://your-api-domain.com/api/track-click') {
        this.apiEndpoint = apiEndpoint;
        this.sessionId = this.getOrCreateSessionId();
        this.startTime = Date.now();
        this.pageName = this.getPageName();
        this.tag = 'general';
        
        // Bind methods to preserve context
        this.handleBeforeUnload = this.handleBeforeUnload.bind(this);
        this.handleVisibilityChange = this.handleVisibilityChange.bind(this);
        
        // Set up event listeners
        this.initializeTracking();
        
        console.log('Portfolio Tracker initialized for page:', this.pageName);
    }
    
    /**
     * Get or create a unique session ID stored in localStorage
     */
    getOrCreateSessionId() {
        const storageKey = 'portfolio_session_id';
        let sessionId = localStorage.getItem(storageKey);
        
        if (!sessionId) {
            // Generate a unique session ID
            sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem(storageKey, sessionId);
        }
        
        return sessionId;
    }
    
    /**
     * Extract page name from current URL (pathname + search) or document title
     */
    getPageName() {
        // Get both pathname and search parameters
        const pathname = window.location.pathname;
        const search = window.location.search;
        
        // Combine pathname and search parameters
        let fullPath = pathname + search;
        
        // Remove leading slash and clean up
        let pageName = fullPath.replace(/^\/+/, '');
        
        // If empty or just index, use document title or default
        if (!pageName || pageName === 'index' || pageName === '') {
            pageName = document.title || 'home';
        }
        
        // Sanitize by replacing non-alphanumeric characters with underscores
        pageName = pageName.toLowerCase().replace(/[^a-z0-9]/g, '_');
        
        // Clean up multiple consecutive underscores and trailing underscores
        pageName = pageName.replace(/_+/g, '_').replace(/^_+|_+$/g, '');
        
        return pageName || 'unknown';
    }
    
    /**
     * Calculate time spent on page in seconds
     */
    getTimeOnPage() {
        return Math.round((Date.now() - this.startTime) / 1000);
    }
    
    /**
     * Get referrer URL with fallback
     */
    getReferrer() {
        return document.referrer || 'direct';
    }
    
    /**
     * Get user agent string
     */
    getUserAgent() {
        return navigator.userAgent || 'unknown';
    }
    
    /**
     * Create the data payload to send to API
     */
    createPayload() {
        return {
            page_name: this.pageName,
            tag: this.tag,
            time_on_page: this.getTimeOnPage(),
            session_id: this.sessionId,
            referrer: this.getReferrer(),
            user_agent: this.getUserAgent()
        };
    }
    
    /**
     * Send tracking data to the API endpoint
     */
    sendTrackingData() {
        const payload = this.createPayload();
        
        // Log the payload for debugging
        console.log('Sending tracking data:', payload);
        
        // Only send if user spent at least 1 second on page
        if (payload.time_on_page < 1) {
            console.log('Skipping tracking - insufficient time on page');
            return;
        }
        
        try {
            // Use sendBeacon for reliable delivery even during page unload
            if (navigator.sendBeacon) {
                const success = navigator.sendBeacon(
                    this.apiEndpoint,
                    JSON.stringify(payload)
                );
                
                if (success) {
                    console.log('Tracking data sent successfully via sendBeacon');
                } else {
                    console.warn('sendBeacon failed, falling back to fetch');
                    this.fallbackSend(payload);
                }
            } else {
                // Fallback for browsers that don't support sendBeacon
                this.fallbackSend(payload);
            }
        } catch (error) {
            console.error('Error sending tracking data:', error);
        }
    }
    
    /**
     * Fallback method using fetch for browsers without sendBeacon support
     */
    fallbackSend(payload) {
        fetch(this.apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
            keepalive: true // Important for requests during page unload
        }).then(response => {
            if (response.ok) {
                console.log('Tracking data sent successfully via fetch');
            } else {
                console.warn('Failed to send tracking data:', response.status);
            }
        }).catch(error => {
            console.error('Fetch fallback failed:', error);
        });
    }
    
    /**
     * Handle page unload event
     */
    handleBeforeUnload() {
        this.sendTrackingData();
    }
    
    /**
     * Handle visibility change (tab switch, minimize, etc.)
     */
    handleVisibilityChange() {
        if (document.visibilityState === 'hidden') {
            this.sendTrackingData();
        }
    }
    
    /**
     * Initialize event listeners for tracking
     */
    initializeTracking() {
        // Track when user leaves the page
        window.addEventListener('beforeunload', this.handleBeforeUnload);
        
        // Track when user switches tabs or minimizes window
        document.addEventListener('visibilitychange', this.handleVisibilityChange);
        
        // Track when page loses focus (additional safety net)
        window.addEventListener('blur', this.handleBeforeUnload);
        
        // For single-page applications, you might want to track route changes
        // window.addEventListener('popstate', this.handleBeforeUnload);
    }
    
    /**
     * Manually trigger tracking (useful for SPAs or custom events)
     */
    track() {
        this.sendTrackingData();
    }
    
    /**
     * Update the tag for more specific tracking
     */
    setTag(newTag) {
        this.tag = newTag || 'general';
    }
    
    /**
     * Clean up event listeners (call when tracker is no longer needed)
     */
    destroy() {
        window.removeEventListener('beforeunload', this.handleBeforeUnload);
        document.removeEventListener('visibilitychange', this.handleVisibilityChange);
        window.removeEventListener('blur', this.handleBeforeUnload);
    }
}

// Auto-initialize the tracker when script loads
// You can customize the API endpoint here
const tracker = new PortfolioTracker('https://lubo-portfolio-tracker-production.up.railway.app/api/track-click');

// Expose tracker globally for manual tracking if needed
window.portfolioTracker = tracker;

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PortfolioTracker;
}
