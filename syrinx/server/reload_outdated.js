/**
 * Development mode live reload script for Syrinx.
 * 
 * This script checks for version changes on the server and automatically
 * reloads the page when changes are detected.
 */
(function() {
    let currentVersion = __CURRENT_VERSION__;
    setInterval(async () => {
        try {
            const response = await fetch('/__dev_reload_check__');
            const data = await response.json();
            if (data.version !== currentVersion) {
                console.log('[DEV] Reloading page...');
                window.location.reload();
            }
        } catch (e) {
            console.error('[DEV] Reload check failed:', e);
        }
    }, 1000);
})();
