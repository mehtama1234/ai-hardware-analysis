from deployment.project_store import ProjectStore


def test_project_store_create_ensure_and_list(tmp_path):
    store = ProjectStore(tmp_path / "jobs.sqlite")
    created = store.create("customer_demo", "Customer Demo")
    assert created["name"] == "Customer Demo"
    assert store.get("customer_demo")["id"] == "customer_demo"
    assert store.ensure("default")["name"] == "default"
    assert [project["id"] for project in store.list()] == ["customer_demo", "default"]
