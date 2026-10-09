// src/sessionStore.js
export let currentUser = null;

export function setCurrentUser(u) {
  currentUser = u
    ? { ...u, rol: (u.rol || '').toLowerCase() }
    : null;
}

export function getCurrentUser() {
  return currentUser;
}

export function clearCurrentUser() {
  currentUser = null;
}

