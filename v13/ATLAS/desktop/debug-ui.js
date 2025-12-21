// Electron DevTools Diagnostic Script
// Run these commands in the Electron DevTools Console tab

console.log('=== ATLAS Desktop UI Diagnostic ===\n');

// 1. Check Theme Variables
console.log('1. THEME VARIABLES:');
console.log('--background:', getComputedStyle(document.body).getPropertyValue('--background'));
console.log('--foreground:', getComputedStyle(document.body).getPropertyValue('--foreground'));
console.log('--primary:', getComputedStyle(document.body).getPropertyValue('--primary'));
console.log('--secondary:', getComputedStyle(document.body).getPropertyValue('--secondary'));
console.log('');

// 2. Check Body Styles
console.log('2. BODY STYLES:');
console.log('backgroundColor:', getComputedStyle(document.body).backgroundColor);
console.log('color:', getComputedStyle(document.body).color);
console.log('dark class:', document.body.classList.contains('dark'));
console.log('');

// 3. Check Main Content
console.log('3. MAIN CONTENT:');
const main = document.querySelector('main');
console.log('main element exists:', !!main);
console.log('main children count:', main?.children.length || 0);
console.log('main innerHTML length:', main?.innerHTML.length || 0);
console.log('');

// 4. Check #__next
console.log('4. REACT ROOT:');
const nextRoot = document.getElementById('__next');
console.log('#__next exists:', !!nextRoot);
console.log('#__next children count:', nextRoot?.children.length || 0);
console.log('#__next innerHTML length:', nextRoot?.innerHTML.length || 0);
console.log('');

// 5. Check Stylesheets
console.log('5. STYLESHEETS:');
const stylesheets = Array.from(document.styleSheets);
console.log('Total stylesheets:', stylesheets.length);
stylesheets.forEach((sheet, i) => {
    try {
        console.log(`  ${i + 1}. ${sheet.href || 'inline'} (${sheet.cssRules?.length || 0} rules)`);
    } catch (e) {
        console.log(`  ${i + 1}. ${sheet.href || 'inline'} (CORS blocked)`);
    }
});
console.log('');

// 6. Check for React Errors
console.log('6. REACT STATE:');
console.log('window.__NEXT_DATA__ exists:', !!window.__NEXT_DATA__);
console.log('');

// 7. Check Main Element Computed Styles
if (main) {
    console.log('7. MAIN ELEMENT COMPUTED STYLES:');
    const mainStyles = getComputedStyle(main);
    console.log('display:', mainStyles.display);
    console.log('visibility:', mainStyles.visibility);
    console.log('opacity:', mainStyles.opacity);
    console.log('backgroundColor:', mainStyles.backgroundColor);
    console.log('color:', mainStyles.color);
    console.log('width:', mainStyles.width);
    console.log('height:', mainStyles.height);
} else {
    console.log('7. MAIN ELEMENT: NOT FOUND');
}
console.log('');

// 8. Check for Common Issues
console.log('8. COMMON ISSUES CHECK:');
console.log('window.location.href:', window.location.href);
console.log('document.title:', document.title);
console.log('');

console.log('=== END DIAGNOSTIC ===');
console.log('Copy this entire output and share it for analysis.');
