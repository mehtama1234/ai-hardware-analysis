from pathlib import Path

import yaml


def test_backup_cronjob_is_non_overlapping_and_secret_backed():
    path = Path(__file__).parent / "kubernetes" / "verification-backup-cronjob.yaml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert document["kind"] == "CronJob"
    spec = document["spec"]
    assert spec["concurrencyPolicy"] == "Forbid"
    assert spec["schedule"] == "0 * * * *"
    container = spec["jobTemplate"]["spec"]["template"]["spec"]["containers"][0]
    env = {item["name"]: item for item in container["env"]}
    assert env["VERIFICATION_DATABASE_URL"]["valueFrom"]["secretKeyRef"]["name"] == "verification-production-database"
    assert "deployment.run_scheduled_backup" in " ".join(container["command"])
