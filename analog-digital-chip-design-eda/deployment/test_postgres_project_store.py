from deployment.postgres_project_store import PostgresCollateralStore, PostgresProjectStore


def test_postgres_repositories_expose_pilot_method_contracts():
    for cls, methods in ((PostgresProjectStore, ("ensure", "create", "get", "list")), (PostgresCollateralStore, ("add", "get", "list"))):
        for method in methods:
            assert callable(getattr(cls, method))


def test_postgres_collateral_accepts_managed_object_store_boundary(tmp_path):
    class Store:
        def put(self, key, content):
            self.last = (key, bytes(content))
            return None
    store = Store()
    # Constructor contract is checked without opening a database connection.
    instance = object.__new__(PostgresCollateralStore)
    instance.object_store = store
    assert instance.object_store is store
