import pytest
from core.libs.assertions import assert_auth, assert_found, assert_true, assert_valid, base_assert
from core.libs.exceptions import FyleError



def test_base_assert():
    with pytest.raises(FyleError) as excinfo:
        base_assert(404, "NOT_FOUND")
    assert excinfo.value.status_code == 404
    assert excinfo.value.message == "NOT_FOUND"


def test_assert_auth():
    with pytest.raises(FyleError) as excinfo:
        assert_auth(False)
    assert excinfo.value.status_code == 401
    assert excinfo.value.message == "UNAUTHORIZED"
    assert_auth(True)


def test_assert_true():
    with pytest.raises(FyleError) as excinfo:
        assert_true(False)
    assert excinfo.value.status_code == 403
    assert excinfo.value.message == "FORBIDDEN"
    assert_true(True)  


def test_assert_valid():
    with pytest.raises(FyleError) as excinfo:
        assert_valid(False)
    assert excinfo.value.status_code == 400
    assert excinfo.value.message == "BAD_REQUEST"
    assert_valid(True) 


def test_assert_found():
    with pytest.raises(FyleError) as excinfo:
        assert_found(None)
    assert excinfo.value.status_code == 404
    assert excinfo.value.message == "NOT_FOUND"
    some_object = object()
    assert_found(some_object)






