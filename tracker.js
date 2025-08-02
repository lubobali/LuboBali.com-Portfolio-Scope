/**
 * Portfolio Click Tracker - Production Version
 * Tracks user engagement across SPA navigation
 */

(function() {
    'use strict';
    
    // Prevent duplicate tracker instances
    if (window.TRACKER_LOADED) {
        console.log('TRACKER: Already loaded, skipping');
        return;
    }
    window.TRACKER_LOADED = true;
    console.log('TRACKER: Production tracker initialized');
    
    // Track sent requests to prevent duplicates
    const sentRequests = new Set();
    
    function generateRequestId(pageName, timeOnPage, eventType) {
        return `${pageName}-${eventType}-${Math.floor(timeOnPage/5)*5}`;
    }
    
    class PortfolioTracker {
        constructor() {
            if (window.trackerInstance) {
                console.log('TRACKER: Using existing instance');
                return window.trackerInstance;
            }
            
            console.log('TRACKER: Creating new instance');
            this.apiEndpoint = 'https://lubo-portfolio-tracker-production.up.railway.app/api/track-click';
            this.sessionId = this.getSessionId();
            this.currentPageName = null;
            this.startTime = null;
            this.sentArrival = false;
            this.sentExit = false;
            this.requestInProgress = false;
            
            // Initialize for current page
            this.initializePage();
            
            // Set up SPA navigation detection
            this.setupSPADetection();
            
            window.trackerInstance = this;
        }
        
        getSessionId() {
            let sessionId = localStorage.getItem('portfolio_session_id');
            if (!sessionId) {
                sessionId = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                localStorage.setItem('portfolio_session_id', sessionId);
            }
            return sessionId;
        }
        
        getPageName() {
            const path = window.location.pathname + window.location.search;
            return path === '/' ? 'home' : path;
        }
        
        getTimeOnPage() {
            return this.startTime ? Math.round((Date.now() - this.startTime) / 1000) : 0;
        }
        
        initializePage() {
            // Reset for new page (don't send premature exits)
            this.currentPageName = this.getPageName();
            this.startTime = Date.now();
            this.sentArrival = false;
            this.sentExit = false;
            
            // Track arrival for new page
            this.trackArrival();
            
            // Set up exit listeners for this page
            this.setupExitListeners();
        }
        
        async sendRequest(eventType) {
            const timeOnPage = this.getTimeOnPage();
            const requestId = generateRequestId(this.currentPageName, timeOnPage, eventType);
            
            // Prevent duplicate requests
            if (sentRequests.has(requestId)) {
                console.log('TRACKER: Duplicate request blocked');
                return;
            }
            
            if (this.requestInProgress) {
                console.log('TRACKER: Request in progress, blocking');
                return;
            }
            
            console.log(`TRACKER: Sending ${eventType} for ${this.currentPageName}`);
            
            this.requestInProgress = true;
            sentRequests.add(requestId);
            
            const payload = {
                page_name: this.currentPageName,
                tag: eventType, // Clean tags: 'arrival' or 'exit'
                time_on_page: timeOnPage,
                session_id: this.sessionId,
                referrer: document.referrer || 'direct',
                user_agent: navigator.userAgent,
                ip: null
            };
            
            try {
                await fetch(this.apiEndpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                    keepalive: true
                });
                console.log(`TRACKER: ${eventType} sent successfully`);
            } catch (error) {
                console.error('TRACKER: Request failed', error);
            } finally {
                this.requestInProgress = false;
            }
        }
        
        trackArrival() {
            if (this.sentArrival) {
                return;
            }
            this.sentArrival = true;
            this.sendRequest('arrival');
        }
        
        trackExit() {
            if (this.sentExit) {
                return;
            }
            if (this.getTimeOnPage() < 1) {
                return;
            }
            this.sentExit = true;
            this.sendRequest('exit');
        }
        
        setupExitListeners() {
            // Remove old listeners
            if (this.exitHandler) {
                window.removeEventListener('beforeunload', this.exitHandler);
                document.removeEventListener('visibilitychange', this.visibilityHandler);
            }
            
            // Create new handlers
            this.exitHandler = () => {
                this.trackExit();
            };
            
            this.visibilityHandler = () => {
                if (document.visibilityState === 'hidden') {
                    this.trackExit();
                }
            };
            
            // Add fresh listeners
            window.addEventListener('beforeunload', this.exitHandler);
            document.addEventListener('visibilitychange', this.visibilityHandler);
        }
        
        setupSPADetection() {
            let currentUrl = window.location.href;
            
            // Check for URL changes every 500ms
            setInterval(() => {
                if (window.location.href !== currentUrl) {
                    currentUrl = window.location.href;
                    this.initializePage();
                }
            }, 500);
            
            // Also listen for popstate (back/forward buttons)
            window.addEventListener('popstate', () => {
                setTimeout(() => this.initializePage(), 100);
            });
        }
    }
    
    // Initialize tracker
    const tracker = new PortfolioTracker();
    window.portfolioTracker = tracker;
    
})();
