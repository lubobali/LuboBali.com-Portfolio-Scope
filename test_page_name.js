// Test script to check what page_name is being generated
// Copy this into browser console to test

console.log('=== PAGE NAME TEST ===');
console.log('Current URL:', window.location.href);
console.log('Pathname:', window.location.pathname);
console.log('Search:', window.location.search);

// Test the NEW logic
const pathname = window.location.pathname;
const search = window.location.search;
let fullPath = pathname + search;

if (fullPath === '/' || fullPath === '' || fullPath === '/index') {
    var newPageName = 'home';
} else {
    var newPageName = fullPath;
    if (!newPageName.startsWith('/')) {
        newPageName = '/' + newPageName;
    }
    newPageName = newPageName.replace(/\/+$/, '');
    newPageName = newPageName.replace(/\/+/g, '/');
}

console.log('NEW page_name would be:', newPageName);

// Test the OLD logic (for comparison)
let oldPath = fullPath.replace(/^\/+/, '');
if (!oldPath || oldPath === 'index' || oldPath === '') {
    var oldPageName = document.title || 'home';
} else {
    var oldPageName = oldPath;
}
oldPageName = oldPageName.toLowerCase().replace(/[^a-z0-9]/g, '_');
oldPageName = oldPageName.replace(/_+/g, '_').replace(/^_+|_+$/g, '');

console.log('OLD page_name would be:', oldPageName);
console.log('==================');
