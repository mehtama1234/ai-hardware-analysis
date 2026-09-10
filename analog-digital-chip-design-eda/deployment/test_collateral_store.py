from deployment.collateral_store import CollateralStore


def test_content_addressed_collateral_is_deduplicated(tmp_path):
    store = CollateralStore(tmp_path / "jobs.sqlite", tmp_path / "artifacts")
    first = store.add("p1", "spec.md", "specification", "v1", "module spec;")
    second = store.add("p1", "spec.md", "specification", "v1", "module spec;")
    assert first["sha256"] == second["sha256"]
    assert len(store.list("p1")) == 1
    assert (tmp_path / "artifacts" / first["path"]).is_file()
