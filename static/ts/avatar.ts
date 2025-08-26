// Basic TypeScript scaffold for avatar UI integration
// Sends selected avatar URL or file upload to your Flask endpoints

type Json = Record<string, unknown>;

async function getCsrf(): Promise<string | null> {
  try {
    const res = await fetch('/api/csrf-token');
    const data = (await res.json()) as Json;
    return (data && (data['csrf_token'] as string)) || null;
  } catch {
    return null;
  }
}

export async function setAvatarFromUrl(url: string): Promise<boolean> {
  const csrf = await getCsrf();
  const res = await fetch('/api/user/avatar', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(csrf ? { 'X-CSRF-Token': csrf } : {}),
    },
    body: JSON.stringify({ avatar_key: 'ava-image', prefs: { url } }),
  });
  return res.ok;
}

export async function uploadAvatar(file: File): Promise<string | null> {
  const csrf = await getCsrf();
  const form = new FormData();
  form.append('file', file);
  const res = await fetch('/api/user/avatar/upload', {
    method: 'POST',
    headers: {
      ...(csrf ? { 'X-CSRF-Token': csrf } : {}),
    },
    body: form,
  });
  if (!res.ok) return null;
  const data = (await res.json()) as Json;
  return (data && (data['url'] as string)) || null;
}

// Small helper to wire an input[type=file]
export function wireAvatarFileInput(input: HTMLInputElement, imgPreview?: HTMLImageElement) {
  input.addEventListener('change', async () => {
    const file = input.files?.[0];
    if (!file) return;
    const url = await uploadAvatar(file);
    if (url && imgPreview) imgPreview.src = url;
  });
}
