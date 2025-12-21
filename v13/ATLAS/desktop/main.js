const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')
const { spawn } = require('child_process')
const fs = require('fs')

let mainWindow
let pythonProcess

// Backend path - always use relative path in dev
const backendPath = path.join(__dirname, '..', 'backend', 'main.py')

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1200,
        minHeight: 700,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false,
            sandbox: true
        },
        icon: path.join(__dirname, 'build/icon.png'),
        backgroundColor: '#0a0a0f',
        show: false // Don't show until ready
    })

    // Start backend before loading UI
    startBackend()

    // Load frontend
    const frontendUrl = isDev
        ? 'http://localhost:3000'
        : `file://${path.join(__dirname, 'renderer', 'index.html')}`

    console.log(`[Frontend] Loading from: ${frontendUrl}`)
    mainWindow.loadURL(frontendUrl)

    // Show window when ready
    mainWindow.once('ready-to-show', () => {
        mainWindow.show()
    })

    // Development tools
    if (isDev) {
        mainWindow.webContents.openDevTools()
    }
}

function startBackend() {
    console.log('[Backend] Starting QFS API...')

    // Basic check for python availability, in prod this would use the bundled python
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3'

    pythonProcess = spawn(pythonCmd, [backendPath], {
        cwd: path.join(__dirname, '..'),
        env: {
            ...process.env,
            PYTHONUNBUFFERED: '1',
            QFS_MODE: 'beta',
            QFS_BETA_CAP: '200'
        }
    })

    pythonProcess.stdout.on('data', (data) => {
        console.log(`[Backend] ${data.toString()}`)
    })

    pythonProcess.stderr.on('data', (data) => {
        console.error(`[Backend Error] ${data.toString()}`)
    })

    pythonProcess.on('close', (code) => {
        console.log(`[Backend] Process exited with code ${code}`)
    })
}

// App lifecycle
app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
    if (pythonProcess) {
        pythonProcess.kill()
    }
    if (process.platform !== 'darwin') {
        app.quit()
    }
})

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow()
    }
})

app.on('before-quit', () => {
    if (pythonProcess) {
        pythonProcess.kill()
    }
})

// IPC handlers for frontend-backend bridge
ipcMain.handle('backend:health', async () => {
    try {
        const response = await fetch('http://localhost:8000/health')
        return await response.json()
    } catch (error) {
        return { status: 'offline', error: error.message }
    }
})

ipcMain.handle('get-user-data-path', () => {
    return app.getPath('userData')
})
