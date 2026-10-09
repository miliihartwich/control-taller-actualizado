// src/api.js
// ===============================
// DEV MODE: sin auth, sin cookies, sin refresh, sin logout automático
// Objetivo: que la app funcione y NO se caiga por 401.
// ===============================


const BASE = '/api'; // todas las llamadas salen por el proxy

function buildURL(p) {
  const route = p.startsWith('/') ? p : `/${p}`;
  // Evita /api duplicado
  if (route.startsWith('/api/')) return route;
  return `${BASE}${route}`;
}

async function safeParseBody(res) {
  const ct = res.headers.get('content-type') || '';
  const isJson = ct.includes('application/json');
  try {
    const data = isJson ? await res.json() : await res.text();
    return { data, isJson };
  } catch {
    return { data: null, isJson };
  }
}

/**
 * apiFetch:
 * - NO agrega Authorization
 * - NO usa cookies (credentials)
 * - NO hace refresh
 * - NO redirige por 401
 * - NUNCA limpia localStorage
 */
export async function apiFetch(
  path,
  {
    method = 'GET',
    headers = {},
    body,
    timeoutMs = 15000,
  } = {}
) {
  const url = buildURL(path);

  const opts = {
    method,
    headers: { ...headers },
  };

  // Body + Content-Type automático si no es string
  if (body !== undefined) {
    const isString = typeof body === 'string';
    if (!isString) {
      opts.headers['Content-Type'] =
        opts.headers['Content-Type'] || 'application/json';
      opts.body = JSON.stringify(body);
    } else {
      opts.body = body;
    }
  }

  // Timeout defensivo
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), timeoutMs);

  let res;
  try {
    res = await fetch(url, { ...opts, signal: ctrl.signal, credentials: 'include' });
  } catch (netErr) {
    clearTimeout(t);
    throw new Error(
      `No se pudo conectar con el servidor (${netErr?.message || 'network error'})`
    );
  } finally {
    clearTimeout(t);
  }

  const { data, isJson } = await safeParseBody(res);

  // En DEV no hacemos NADA especial con 401: solo devolvemos error normal
  if (!res.ok) {
    const msg =
      (isJson && (data?.message || data?.error)) ||
      (typeof data === 'string' && data) ||
      `HTTP ${res.status}`;

    const err = new Error(msg);
    err.status = res.status;
    err.url = url;
    err.data = data;
    throw err;
  }

  return isJson ? data : { raw: data };
}

// ===== Azúcares sintácticos HTTP =====
export const apiGet  = (p, opts = {})       => apiFetch(p, { ...opts, method: 'GET' });
export const apiPost = (p, body, opts = {}) => apiFetch(p, { ...opts, method: 'POST', body });
export const apiPut  = (p, body, opts = {}) => apiFetch(p, { ...opts, method: 'PUT', body });
export const apiDel  = (p, opts = {})       => apiFetch(p, { ...opts, method: 'DELETE' });

// ===== Auth wrappers (DEV-friendly) =====
// Mantengo las funciones para no romper imports en componentes.
// No hacen refresh, no usan cookies, no guardan tokens.

export async function login({ usuario, contrasena }) {
  // OJO: según tu backend real puede ser '/auth/login' o '/login'
  // En tu código venías usando '/auth/login', lo mantengo.
  return apiPost('/auth/login', { usuario, contrasena });
}

export async function logout() {
  // En DEV: no llamamos nada que pueda fallar o devolver 401.
  // Si querés, podés limpiar SOLO la sesión de tu app (no tokens).
  // Pero por ahora lo dejamos vacío para no “romper” nada.
  return true;
}

export async function refresh() {
  // En DEV: no existe refresh
  return true;
}
