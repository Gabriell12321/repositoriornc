import os
import importlib

class DummyResp:
    def __init__(self, ok=True, content=b"FAKEWEBP", headers=None):
        self.ok = ok
        self.content = content
        self.headers = headers or {"Content-Type": "image/webp"}


def test_sanitize_image_uses_rust_when_configured(monkeypatch):
    os.environ['RUST_IMAGES_URL'] = 'http://localhost:8081'

    # Reimport module to ensure it reads env and requests
    mod = importlib.import_module('services.image_utils')

    def fake_post(url, files=None, timeout=10):
        assert url.endswith('/sanitize')
        assert 'file' in files
        return DummyResp()

    # Patch requests.post inside the module
    monkeypatch.setattr(mod, 'requests', type('R', (), {'post': staticmethod(fake_post)}))

    # Provide any bytes; it won't reach Pillow path when rust is configured and returns ok
    data, ext, size = mod.sanitize_image(b'12345', max_size=(256,256), out_format='WEBP')
    assert data == b'FAKEWEBP'
    assert ext == 'webp'
    assert size == (0, 0)

    # Cleanup
    os.environ.pop('RUST_IMAGES_URL', None)
