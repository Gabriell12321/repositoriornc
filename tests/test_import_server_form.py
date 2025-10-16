import importlib
m = importlib.import_module('server_form')
print('APP', bool(getattr(m, 'app', None)))
print('HAS_DEBUG', bool(getattr(m, 'api_debug_session', None)))
