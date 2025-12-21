const { contextBridge, ipcRenderer } = require('electron')

// Expose protected methods to renderer
contextBridge.exposeInMainWorld('electron', {
    // Backend communication
    checkBackendHealth: () => ipcRenderer.invoke('backend:health'),
    getUserDataPath: () => ipcRenderer.invoke('get-user-data-path'),

    // App metadata
    getVersion: () => process.env.npm_package_version,
    getPlatform: () => process.platform,
})
