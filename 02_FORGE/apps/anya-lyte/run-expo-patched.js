const fs = require('fs');
const fsPromises = require('fs/promises');

const patchPath = (path) => {
  return typeof path === 'string' && (path.includes('node:') || path.includes('node_sea'));
};

const originalMkdirSync = fs.mkdirSync;
fs.mkdirSync = function(path, options) {
  if (patchPath(path)) {
    console.log('[MONKEYPATCH] Skipping mkdirSync for:', path);
    return;
  }
  try {
    return originalMkdirSync.apply(this, arguments);
  } catch (err) {
    if (patchPath(err.path)) {
      console.log('[MONKEYPATCH] Caught and skipped mkdirSync error for:', err.path);
      return;
    }
    throw err;
  }
};

const originalMkdir = fs.mkdir;
fs.mkdir = function(path, options, callback) {
  if (patchPath(path)) {
    console.log('[MONKEYPATCH] Skipping mkdir for:', path);
    const cb = typeof options === 'function' ? options : callback;
    if (cb) cb(null);
    return;
  }
  const cb = typeof options === 'function' ? options : callback;
  const wrappedCallback = function(err) {
    if (err && patchPath(err.path)) {
      console.log('[MONKEYPATCH] Caught and skipped mkdir error for:', err.path);
      if (cb) cb(null);
      return;
    }
    if (cb) cb.apply(this, arguments);
  };
  if (typeof options === 'function') {
    return originalMkdir.call(this, path, wrappedCallback);
  }
  return originalMkdir.call(this, path, options, wrappedCallback);
};

const originalPromisesMkdir = fsPromises.mkdir || fs.promises.mkdir;
const patchedPromisesMkdir = function(path, options) {
  if (patchPath(path)) {
    console.log('[MONKEYPATCH] Skipping fs.promises.mkdir for:', path);
    return Promise.resolve();
  }
  return originalPromisesMkdir.apply(this, arguments).catch((err) => {
    if (patchPath(err.path)) {
      console.log('[MONKEYPATCH] Caught and skipped fs.promises.mkdir error for:', err.path);
      return;
    }
    throw err;
  });
};

fsPromises.mkdir = patchedPromisesMkdir;
if (fs.promises) {
  fs.promises.mkdir = patchedPromisesMkdir;
}

const originalWriteFileSync = fs.writeFileSync;
fs.writeFileSync = function(path, data, options) {
  if (patchPath(path)) {
    console.log('[MONKEYPATCH] Skipping writeFileSync for:', path);
    return;
  }
  try {
    return originalWriteFileSync.apply(this, arguments);
  } catch (err) {
    if (patchPath(err.path)) {
      console.log('[MONKEYPATCH] Caught and skipped writeFileSync error for:', err.path);
      return;
    }
    throw err;
  }
};

const originalWriteFile = fs.writeFile;
fs.writeFile = function(path, data, options, callback) {
  if (patchPath(path)) {
    console.log('[MONKEYPATCH] Skipping writeFile for:', path);
    const cb = typeof options === 'function' ? options : callback;
    if (cb) cb(null);
    return;
  }
  const cb = typeof options === 'function' ? options : callback;
  const wrappedCallback = function(err) {
    if (err && patchPath(err.path)) {
      console.log('[MONKEYPATCH] Caught and skipped writeFile error for:', err.path);
      if (cb) cb(null);
      return;
    }
    if (cb) cb.apply(this, arguments);
  };
  if (typeof options === 'function') {
    return originalWriteFile.call(this, path, data, wrappedCallback);
  }
  return originalWriteFile.call(this, path, data, options, wrappedCallback);
};

const originalPromisesWriteFile = fsPromises.writeFile || fs.promises.writeFile;
const patchedPromisesWriteFile = function(path, data, options) {
  if (patchPath(path)) {
    console.log('[MONKEYPATCH] Skipping fs.promises.writeFile for:', path);
    return Promise.resolve();
  }
  return originalPromisesWriteFile.apply(this, arguments).catch((err) => {
    if (patchPath(err.path)) {
      console.log('[MONKEYPATCH] Caught and skipped fs.promises.writeFile error for:', err.path);
      return;
    }
    throw err;
  });
};

fsPromises.writeFile = patchedPromisesWriteFile;
if (fs.promises) {
  fs.promises.writeFile = patchedPromisesWriteFile;
}

// Require the actual expo CLI entry point
require('./node_modules/expo/bin/cli');
