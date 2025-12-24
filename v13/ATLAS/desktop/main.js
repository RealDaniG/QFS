const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');

let mainWindow;

// v19 Configuration: Centralized config for 4-Layer Architecture
const CONFIG = {
    backendUrl: process.env.BACKEND_URL || 'http://127.0.0.1:8001',
    p2pUrl: process.env.P2P_URL || 'ws://127.0.0.1:9000/ws',
    ipfsApi: process.env.IPFS_API || 'http://127.0.0.1:5001',
    ipfsGateway: process.env.IPFS_GATEWAY || 'http://127.0.0.1:8080'
};

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        title: 'ATLAS v19 – Decentralized Intelligence',
        icon: path.join(__dirname, 'build/icon.png'),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            webSecurity: true, // IMPORTANT: Keep enabled for security
            preload: path.join(__dirname, 'preload.js'),
        }
    });

    // v19 CSP for Web3 + IPFS + P2P
    mainWindow.webContents.session.webRequest.onHeadersReceived((details, callback) => {
        callback({
            responseHeaders: {
                ...details.responseHeaders,
                'Content-Security-Policy': [
                    "default-src 'self' http://localhost:3000;",
                    "script-src 'self' 'unsafe-eval' 'unsafe-inline';", // Needed for Next.js // TODO: Tighten for prod
                    "style-src 'self' 'unsafe-inline';",
                    `connect-src 'self' http://localhost:3000 ${CONFIG.backendUrl} ${CONFIG.p2pUrl} ${CONFIG.ipfsApi} ${CONFIG.ipfsGateway} ws://localhost:3000 ws://127.0.0.1:9000;`, // Allow P2P & IPFS
                    "img-src 'self' data: blob: http://localhost:3000 https://ipfs.io http://127.0.0.1:8080;", // Allow IPFS images
                    "font-src 'self' data:;",
                    "object-src 'none';",
                    "base-uri 'self';",
                    "form-action 'self';",
                    "frame-ancestors 'none';"
                ].join(' ')
            }
        });
    });

    const startUrl = isDev
        ? 'http://localhost:3000'
        : `file://${path.join(__dirname, '../out/index.html')}`;

    mainWindow.loadURL(startUrl);

    // Open external links in default browser
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        if (url.startsWith('http:') || url.startsWith('https:')) {
            shell.openExternal(url);
            return { action: 'deny' };
        }
        return { action: 'allow' };
    });

    if (isDev) {
        mainWindow.webContents.openDevTools();
    }

    mainWindow.on('closed', () => (mainWindow = null));
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (mainWindow === null) {
        createWindow();
    }
});

// IPC Handler for v19 Desktop Features (Future)
ipcMain.handle('get-app-version', () => app.getVersion());
