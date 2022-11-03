from tidy3d_webapi import Folder
from tidy3d_webapi.environment import Env

Env.dev.active()


def test_list_folders():
    resp = Folder.list()
    assert resp is not None


def test_get_folder():
    resp = Folder.get("default")
    assert resp is not None


def test_create_and_remove_folder():
    resp = Folder.create("test folder2")
    assert resp is not None
    resp.delete()
