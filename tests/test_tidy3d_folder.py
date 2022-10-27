from tidy3d_webapi import Tidy3DFolder
from tidy3d_webapi.environment import Env

Env.dev.active()


def test_list_folders():
    resp = Tidy3DFolder.list()
    assert resp is not None


def test_get_folder():
    resp = Tidy3DFolder.get("default")
    assert resp is not None


def test_create_and_remove_folder():
    resp = Tidy3DFolder.create("test folder2")
    assert resp is not None
    resp.delete()
