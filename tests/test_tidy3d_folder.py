from tidy3d_webapi.environment import Env
from tidy3d_webapi.types import Tidy3DFolder

Env.dev.active()


def test_list_folders():
    resp = Tidy3DFolder.list()
    assert resp is not None


def test_get_folder():
    resp = Tidy3DFolder.get("default")
    assert resp is not None


def test_create_and_remove_folder():
    resp = Tidy3DFolder.create("test folder")
    assert resp is not None
    resp.remove()
