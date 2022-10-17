from tidy3d_webapi.environment import Env
from tidy3d_webapi.material_libray import MaterialLibray

Env.dev.active()


def test_lib():
    libs = MaterialLibray.list()
    lib = libs[0]
    assert lib.medium
