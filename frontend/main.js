const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const { autoUpdater } = require('electron-updater');

const BACKEND_URL = 'http://127.0.0.1:5000/health';
const UPDATE_CHECK_INTERVAL_MS = 6 * 60 * 60 * 1000;
const shouldStartManagedBackend = process.env.SAVEYOURMONEY_SKIP_BACKEND !== '1';
let backendProcess = null;
let updateCheckTimer = null;
let isDownloadingUpdate = false;
let backendExitedBeforeReady = false;
let backendExitInfo = '';

function resolveBackendConfig() {
  const backendRoot = app.isPackaged
    ? path.join(process.resourcesPath, 'backend')
    : path.resolve(__dirname, '..', 'backend');

  const preferredPythonPath = path.join(backendRoot, '.venv', 'Scripts', 'python.exe');
  const pythonCommand = fs.existsSync(preferredPythonPath) ? preferredPythonPath : 'python';
  const projectRoot = app.isPackaged ? process.resourcesPath : path.resolve(__dirname, '..');

  return { pythonCommand, projectRoot };
}

async function waitForBackendReady(timeoutMs = 60000, retryDelayMs = 500) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < timeoutMs) {
    if (backendExitedBeforeReady) {
      throw new Error(`Backend encerrou antes de iniciar. ${backendExitInfo}`.trim());
    }
    try {
      const response = await fetch(BACKEND_URL);
      if (response.ok) return;
    } catch (error) {
      // Backend ainda iniciando.
    }
    await new Promise((resolve) => setTimeout(resolve, retryDelayMs));
  }
  throw new Error('Backend não respondeu a tempo.');
}

function startBackend() {
  const { pythonCommand, projectRoot } = resolveBackendConfig();
  const env = {
    ...process.env,
    PYTHONUNBUFFERED: '1',
    SAVEYOURMONEY_DATA_DIR: app.getPath('userData'),
  };
  const logDir = path.join(app.getPath('userData'), 'logs');
  fs.mkdirSync(logDir, { recursive: true });
  const backendLogPath = path.join(logDir, 'backend.log');
  const backendLogFd = fs.openSync(backendLogPath, 'a');

  backendExitedBeforeReady = false;
  backendExitInfo = '';

  backendProcess = spawn(pythonCommand, ['-m', 'backend.app'], {
    cwd: projectRoot,
    env,
    windowsHide: true,
    stdio: ['ignore', backendLogFd, backendLogFd],
  });

  backendProcess.on('exit', (code, signal) => {
    if (code !== 0 || signal) {
      backendExitedBeforeReady = true;
      backendExitInfo = `(code=${code ?? 'null'}, signal=${signal ?? 'null'}) Verifique: ${backendLogPath}`;
    }
    backendProcess = null;
    fs.closeSync(backendLogFd);
  });

  backendProcess.on('error', (error) => {
    backendExitedBeforeReady = true;
    backendExitInfo = `${error.message}. Verifique: ${backendLogPath}`;
    dialog.showErrorBox(
      'Erro ao iniciar backend',
      `Não foi possível iniciar o servidor local.\n\n${error.message}`
    );
  });
}

function stopBackend() {
  if (!backendProcess) return;
  backendProcess.kill();
  backendProcess = null;
}

function loadUpdateConfig() {
  const configPath = app.isPackaged
    ? path.join(process.resourcesPath, 'update-config.json')
    : path.join(__dirname, 'update-config.json');

  if (!fs.existsSync(configPath)) return null;

  try {
    const raw = fs.readFileSync(configPath, 'utf8');
    const config = JSON.parse(raw);
    if (!config || config.provider !== 'generic' || !config.url) return null;
    return config;
  } catch (error) {
    return null;
  }
}

function setupAutoUpdater() {
  if (!app.isPackaged) return;

  const updateConfig = loadUpdateConfig();
  if (!updateConfig) return;

  autoUpdater.autoDownload = false;
  autoUpdater.autoInstallOnAppQuit = true;
  autoUpdater.setFeedURL(updateConfig);

  autoUpdater.on('error', (error) => {
    console.error('Auto-update error:', error?.message || error);
    isDownloadingUpdate = false;
  });

  autoUpdater.on('update-available', async () => {
    if (isDownloadingUpdate) return;
    const result = await dialog.showMessageBox({
      type: 'info',
      title: 'Atualização disponível',
      message: 'Uma nova versão está disponível. Deseja baixar agora?',
      buttons: ['Baixar agora', 'Depois'],
      defaultId: 0,
      cancelId: 1,
    });

    if (result.response === 0) {
      isDownloadingUpdate = true;
      autoUpdater.downloadUpdate();
    }
  });

  autoUpdater.on('update-not-available', () => {
    isDownloadingUpdate = false;
  });

  autoUpdater.on('update-downloaded', async () => {
    isDownloadingUpdate = false;
    const result = await dialog.showMessageBox({
      type: 'info',
      title: 'Atualização pronta',
      message: 'A atualização foi baixada. Reiniciar agora para instalar?',
      buttons: ['Reiniciar agora', 'Depois'],
      defaultId: 0,
      cancelId: 1,
    });

    if (result.response === 0) {
      autoUpdater.quitAndInstall();
    }
  });

  autoUpdater.checkForUpdates().catch(() => {});
  updateCheckTimer = setInterval(() => {
    autoUpdater.checkForUpdates().catch(() => {});
  }, UPDATE_CHECK_INTERVAL_MS);
}

function createWindow () {
  const windowIconPath = path.join(__dirname, 'assets', 'icon.ico');
  const win = new BrowserWindow({
    width: 1280,
    height: 720,
    icon: windowIconPath,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  win.loadFile('pages/dashboard.html');
}

app.whenReady().then(async () => {
  app.setAppUserModelId('com.saveyourmoney.desktop');

  if (shouldStartManagedBackend) {
    startBackend();
  }
  try {
    await waitForBackendReady();
  } catch (error) {
    dialog.showErrorBox('Erro ao iniciar o app', error.message);
    app.quit();
    return;
  }

  createWindow();
  setupAutoUpdater();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (updateCheckTimer) {
    clearInterval(updateCheckTimer);
    updateCheckTimer = null;
  }
  if (shouldStartManagedBackend) {
    stopBackend();
  }
  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', () => {
  if (updateCheckTimer) {
    clearInterval(updateCheckTimer);
    updateCheckTimer = null;
  }
  if (shouldStartManagedBackend) {
    stopBackend();
  }
});
