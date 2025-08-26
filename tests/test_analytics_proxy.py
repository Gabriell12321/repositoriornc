import os
import json
import types


def test_proxy_import_and_contract():
    # The client is optional; ensure importing doesn't crash and contract is respected
    import importlib
    mod = importlib.import_module('services.analytics_client')
    assert hasattr(mod, 'get_summary'), 'get_summary missing'
    fn = getattr(mod, 'get_summary')
    assert isinstance(fn, types.FunctionType)
    # When JULIA_ANALYTICS_URL is not set, function returns None
    os.environ.pop('JULIA_ANALYTICS_URL', None)
    assert mod.get_summary() is None
