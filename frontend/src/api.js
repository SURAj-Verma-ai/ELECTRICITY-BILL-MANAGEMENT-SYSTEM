let csrfToken = null;

async function getCsrfToken() {
  if (csrfToken) return csrfToken;
  const res = await fetch('/api/csrf-token', { credentials: 'include' });
  const data = await res.json();
  csrfToken = data.csrf_token;
  return csrfToken;
}

export async function apiGet(url) {
  const res = await fetch(url, { credentials: 'include' });
  return res.json();
}

export async function apiPost(url, body) {
  const token = await getCsrfToken();
  const res = await fetch(url, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': token,
    },
    body: JSON.stringify(body || {}),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || 'Request failed');
  }
  return data;
}
