import pytest
from app.documentation import check_url


@pytest.mark.parametrize('url', ['http://127.0.0.1:8765/api/session', 'https://evil.example/',
    'https://raw.githubusercontent.com/Nodveta/repo/main/test.py', 'https://docs.python.org:8443/',
    'https://user:password@docs.python.org/', 'file:///etc/passwd'])
def test_untrusted_destinations_are_blocked(url):
    with pytest.raises(ValueError):
        check_url(url)


def test_official_sources_are_allowed():
    assert check_url('https://raw.githubusercontent.com/python/cpython/3.12/Doc/library/sqlite3.rst')
    assert check_url('https://docs.python.org/3.12/library/unittest.html')
