from pathlib import Path
from datetime import datetime, timezone
import json
from uuid import uuid4


class ModelStore:
    def __init__(self, root):
        self.root = Path(root)
        self.uploads = self.root / "uploads"
        self.packages = self.root / "packages"
        self.model_index = self.root / "models.json"
        self.project_index = self.root / "projects.json"
        self.run_index = self.root / "runs.json"
        self.uploads.mkdir(parents=True, exist_ok=True)
        self.packages.mkdir(parents=True, exist_ok=True)
        self.records = self._load_model_index()
        self.projects = self._load_project_index()
        self.runs = self._load_run_index()
        self._recover_uploaded_models()

    def _load_model_index(self):
        if not self.model_index.exists():
            return {}
        return json.loads(self.model_index.read_text())

    def _write_model_index(self):
        self.model_index.write_text(json.dumps(self.records, indent=2, sort_keys=True) + "\n")

    def _load_project_index(self):
        if not self.project_index.exists():
            return {}
        return json.loads(self.project_index.read_text())

    def _write_project_index(self):
        self.project_index.write_text(json.dumps(self.projects, indent=2, sort_keys=True) + "\n")

    def _load_run_index(self):
        if not self.run_index.exists():
            return {}
        return json.loads(self.run_index.read_text())

    def _write_run_index(self):
        self.run_index.write_text(json.dumps(self.runs, indent=2, sort_keys=True) + "\n")

    def _recover_uploaded_models(self):
        changed = False
        malformed = [
            model_id
            for model_id, record in self.records.items()
            if record.get("recovered")
            and len(model_id) != 36
            and len(Path(record.get("path", "")).name) > 37
            and Path(record.get("path", "")).name[36] == "-"
        ]
        for model_id in malformed:
            self.records.pop(model_id, None)
            changed = True
        for path in sorted(self.uploads.glob("*.onnx")):
            if len(path.name) > 37 and path.name[36] == "-":
                model_id = path.name[:36]
                filename = path.name[37:]
            else:
                model_id, _, filename = path.name.partition("-")
            if not model_id or not filename or model_id in self.records:
                continue
            self.records[model_id] = {
                "model_id": model_id,
                "filename": filename,
                "path": str(path),
                "recovered": True,
            }
            changed = True
        if changed:
            self._write_model_index()

    def save_upload(self, filename, content):
        model_id = str(uuid4())
        safe_name = Path(filename or "model.onnx").name
        if not safe_name.lower().endswith(".onnx"):
            safe_name = f"{safe_name}.onnx"
        path = self.uploads / f"{model_id}-{safe_name}"
        path.write_bytes(content)
        self.records[model_id] = {
            "model_id": model_id,
            "filename": safe_name,
            "path": str(path),
            "recovered": False,
        }
        self._write_model_index()
        return self.records[model_id]

    def get(self, model_id):
        record = self.records.get(model_id)
        if not record:
            return None
        if not Path(record["path"]).exists():
            return None
        return record

    def list_models(self):
        return [
            {
                "model_id": record["model_id"],
                "filename": record["filename"],
                "path": record["path"],
                "recovered": record.get("recovered", False),
            }
            for record in sorted(self.records.values(), key=lambda item: item["filename"])
            if Path(record["path"]).exists()
        ]

    def create_project(
        self,
        name,
        target_profile="wearable",
        modality="audio_wake_word",
        calibration_profile="sim-wearable-v0",
        runtime_mode="balanced",
    ):
        project_id = str(uuid4())
        project = {
            "project_id": project_id,
            "name": name or "Untitled project",
            "target_profile": target_profile,
            "modality": modality,
            "calibration_profile": calibration_profile,
            "runtime_mode": runtime_mode,
            "model_ids": [],
            "package_ids": [],
            "run_ids": [],
        }
        self.projects[project_id] = project
        self._write_project_index()
        return project

    def get_project(self, project_id):
        project = self.projects.get(project_id)
        if project and "run_ids" not in project:
            project["run_ids"] = []
            self._write_project_index()
        return project

    def list_projects(self):
        changed = False
        for project in self.projects.values():
            if "run_ids" not in project:
                project["run_ids"] = []
                changed = True
        if changed:
            self._write_project_index()
        return sorted(self.projects.values(), key=lambda item: item["name"])

    def update_project(self, project_id, **changes):
        project = self.get_project(project_id)
        if not project:
            return None
        allowed = {"name", "target_profile", "modality", "calibration_profile", "runtime_mode"}
        for key, value in changes.items():
            if key in allowed and value is not None:
                project[key] = value or project[key]
        self._write_project_index()
        return project

    def attach_model_to_project(self, project_id, model_id):
        project = self.projects.get(project_id)
        if not project:
            return None
        if model_id not in project["model_ids"]:
            project["model_ids"].append(model_id)
            self._write_project_index()
        return project

    def attach_package_to_project(self, project_id, package_id):
        project = self.projects.get(project_id)
        if not project:
            return None
        if package_id not in project["package_ids"]:
            project["package_ids"].append(package_id)
            self._write_project_index()
        return project

    def save_project_run(self, project_id, model_id, package_id, artifacts):
        project = self.get_project(project_id)
        if not project:
            return None
        run_id = str(uuid4())
        package_report = artifacts["package"]
        analysis = artifacts["analysis"]
        runtime = artifacts["runtime"]
        baseline = artifacts["baseline"]
        evidence = artifacts["evidence"]
        run = {
            "run_id": run_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "project_id": project_id,
            "project_name": project.get("name"),
            "model_id": model_id,
            "package_id": package_id,
            "target_profile": project.get("target_profile"),
            "modality": project.get("modality"),
            "calibration_profile": project.get("calibration_profile"),
            "runtime_mode": project.get("runtime_mode"),
            "summary": {
                "fit": analysis["summary"]["fit"],
                "grade": analysis["summary"]["grade"],
                "analog_coverage_percent": analysis["summary"]["analog_coverage_percent"],
                "fallback_count": analysis["summary"]["fallback_count"],
                "latency_ms": runtime["summary"]["latency_ms"],
                "energy_uj": runtime["summary"]["energy_uj"],
                "energy_efficiency_x": baseline["summary"]["energy_efficiency_x"],
                "overall_status": evidence["overall_status"],
                "safe_claim": evidence["safe_claim"],
                "readiness_stage": package_report["readiness_stage"],
                "claim_level": package_report["claim_level"],
            },
            "saved_artifacts": package_report.get("saved_artifacts", {}),
        }
        self.runs[run_id] = run
        if run_id not in project["run_ids"]:
            project["run_ids"].append(run_id)
        if package_id not in project["package_ids"]:
            project["package_ids"].append(package_id)
        self._write_run_index()
        self._write_project_index()
        return run

    def get_project_run(self, run_id):
        return self.runs.get(run_id)

    def list_project_runs(self, project_id=None):
        runs = self.runs.values()
        if project_id:
            runs = [run for run in runs if run.get("project_id") == project_id]
        return sorted(runs, key=lambda item: item.get("created_at", ""), reverse=True)

    def save_package(self, model_id, package_id, artifacts, archive_bytes, archive_filename):
        package_dir = self.packages / package_id
        package_dir.mkdir(parents=True, exist_ok=True)
        existing_metadata_path = package_dir / "metadata.json"
        existing_imports = []
        existing_adapter_runs = []
        if existing_metadata_path.exists():
            existing_metadata = json.loads(existing_metadata_path.read_text())
            existing_imports = existing_metadata.get("imported_evidence", [])
            existing_adapter_runs = existing_metadata.get("adapter_runs", [])
        artifact_files = {
            "package": "package-readiness.json",
            "analysis": "analysis.json",
            "quantization": "quantization-report.json",
            "runtime": "runtime-profile.json",
            "baseline": "baseline-comparison.json",
            "workload_fit": "workload-fit.json",
            "system_boundary": "system-boundary.json",
            "research": "research-guide.json",
            "glossary": "concept-glossary.json",
            "measurement": "measurement-evidence.json",
            "toolchain": "toolchain-readiness.json",
            "connection_playbook": "connection-playbook.json",
            "adapter_execution_plan": "adapter-execution-plan.json",
            "adapter_connection_kit": "adapter-connection-kit.json",
            "adapter_evidence_templates": "adapter-evidence-templates.json",
            "adapter_connection_self_test": "adapter-connection-self-test.json",
            "adapter_integration_readiness": "adapter-integration-readiness.json",
            "external_connector_contract": "external-connector-contract.json",
            "connector_implementation_guide": "connector-implementation-guide.json",
            "connector_test_harness": "connector-test-harness.json",
            "connector_acceptance_drills": "connector-acceptance-drills.json",
            "connector_acceptance_report": "connector-acceptance-report.json",
            "connector_backlog": "connector-backlog.json",
            "connector_delivery_plan": "connector-delivery-plan.json",
            "connector_risk_register": "connector-risk-register.json",
            "evidence": "evidence-gates.json",
            "decision": "decision-report.json",
            "rewrites": "rewrite-suggestions.json",
            "rewrite_what_if": "rewrite-what-if.json",
            "rewrite_plan": "rewrite-plan.json",
            "rewrite_work_order": "rewrite-work-order.json",
            "interview_drill": "interview-drill.json",
            "review": "review-report.json",
            "adapters": "adapter-registry.json",
        }
        artifact_files = {key: filename for key, filename in artifact_files.items() if key in artifacts}
        for key, filename in artifact_files.items():
            (package_dir / filename).write_text(json.dumps(artifacts[key], indent=2, sort_keys=True) + "\n")
        (package_dir / "review-report.md").write_text(artifacts["review"]["markdown"])
        archive_path = package_dir / archive_filename
        archive_path.write_bytes(archive_bytes)
        metadata = {
            "package_id": package_id,
            "model_id": model_id,
            "archive_filename": archive_filename,
            "archive_path": str(archive_path),
            "package_dir": str(package_dir),
            "artifacts": artifact_files | {"review_markdown": "review-report.md"},
        }
        if existing_imports:
            metadata["imported_evidence"] = existing_imports
        if existing_adapter_runs:
            metadata["adapter_runs"] = existing_adapter_runs
        (package_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        return metadata

    def get_package_metadata(self, package_id):
        metadata_path = self.packages / Path(package_id).name / "metadata.json"
        if not metadata_path.exists():
            return None
        return json.loads(metadata_path.read_text())

    def list_packages(self):
        packages = []
        for metadata_path in sorted(self.packages.glob("*/metadata.json")):
            metadata = json.loads(metadata_path.read_text())
            package = self.get_package_artifact(metadata["package_id"], "package")
            packages.append(
                {
                    "package_id": metadata["package_id"],
                    "model_id": metadata["model_id"],
                    "archive_filename": metadata["archive_filename"],
                    "readiness_stage": package.get("readiness_stage") if package else None,
                    "claim_level": package.get("claim_level") if package else None,
                    "package_dir": metadata["package_dir"],
                }
            )
        return packages

    def get_package_artifact(self, package_id, artifact_key):
        metadata = self.get_package_metadata(package_id)
        if not metadata:
            return None
        filename = metadata["artifacts"].get(artifact_key)
        if not filename:
            return None
        path = Path(metadata["package_dir"]) / filename
        if not path.exists():
            return None
        if path.suffix == ".md":
            return path.read_text()
        return json.loads(path.read_text())

    def save_imported_evidence(self, package_id, import_record):
        metadata = self.get_package_metadata(package_id)
        if not metadata:
            return None
        evidence_dir = Path(metadata["package_dir"]) / "imported-evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        safe_source = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in import_record["source_id"])
        filename = f"{safe_source}-{import_record['import_id']}.json"
        path = evidence_dir / filename
        path.write_text(json.dumps(import_record, indent=2, sort_keys=True) + "\n")
        imports = metadata.get("imported_evidence", [])
        imports.append(
            {
                "import_id": import_record["import_id"],
                "source_id": import_record["source_id"],
                "artifact_name": import_record["artifact_name"],
                "created_at": import_record["created_at"],
                "path": str(path),
                "package_id": package_id,
                "run_id": import_record.get("run_id"),
            }
        )
        metadata["imported_evidence"] = imports
        (Path(metadata["package_dir"]) / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        return import_record

    def list_imported_evidence(self, package_id):
        metadata = self.get_package_metadata(package_id)
        if not metadata:
            return None
        records = []
        for item in metadata.get("imported_evidence", []):
            path = Path(item["path"])
            if path.exists():
                records.append(json.loads(path.read_text()))
        return records

    def save_adapter_run(self, package_id, adapter_run):
        metadata = self.get_package_metadata(package_id)
        if not metadata:
            return None
        run_dir = Path(metadata["package_dir"]) / "adapter-runs"
        run_dir.mkdir(parents=True, exist_ok=True)
        safe_adapter = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in adapter_run.get("adapter_id", "adapter"))
        run_id = adapter_run.get("run_id") or str(uuid4())
        filename = f"{safe_adapter}-{run_id}.json"
        path = run_dir / filename
        record = {
            **adapter_run,
            "package_id": package_id,
            "path": str(path),
            "audit_rule": "Adapter run records are audit trail only. They do not change claim readiness unless a normalized evidence payload is validated and imported.",
        }
        path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        runs = [item for item in metadata.get("adapter_runs", []) if item.get("run_id") != run_id]
        artifacts = adapter_run.get("artifacts") or []
        runs.append(
            {
                "run_id": run_id,
                "adapter_id": adapter_run.get("adapter_id"),
                "status": adapter_run.get("status"),
                "created_at": adapter_run.get("created_at"),
                "provenance": adapter_run.get("provenance"),
                "confidence": adapter_run.get("confidence"),
                "path": str(path),
                "artifact_count": len(artifacts),
                "artifact_names": [artifact.get("name") for artifact in artifacts],
                "has_normalized_evidence": bool(adapter_run.get("normalized_evidence_payload")),
            }
        )
        metadata["adapter_runs"] = runs[-50:]
        (Path(metadata["package_dir"]) / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        return record

    def list_adapter_runs(self, package_id):
        metadata = self.get_package_metadata(package_id)
        if not metadata:
            return None
        records = []
        for item in metadata.get("adapter_runs", []):
            path = Path(item["path"])
            if path.exists():
                records.append(json.loads(path.read_text()))
        return records

    def delete_imported_evidence(self, package_id, import_ids):
        metadata = self.get_package_metadata(package_id)
        if not metadata:
            return 0
        remove_ids = set(import_ids or [])
        if not remove_ids:
            return 0
        kept = []
        deleted = 0
        for item in metadata.get("imported_evidence", []):
            if item.get("import_id") in remove_ids:
                path = Path(item["path"])
                if path.exists():
                    path.unlink()
                deleted += 1
            else:
                kept.append(item)
        metadata["imported_evidence"] = kept
        (Path(metadata["package_dir"]) / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
        return deleted

    def get_package_artifacts(self, package_id):
        metadata = self.get_package_metadata(package_id)
        if not metadata:
            return None
        artifacts = {}
        for key in ["analysis", "quantization", "runtime", "baseline", "package", "evidence", "review", "adapters"]:
            artifact = self.get_package_artifact(package_id, key)
            if artifact is None:
                return None
            artifacts[key] = artifact
        workload_fit = self.get_package_artifact(package_id, "workload_fit")
        if workload_fit is not None:
            artifacts["workload_fit"] = workload_fit
        system_boundary = self.get_package_artifact(package_id, "system_boundary")
        if system_boundary is not None:
            artifacts["system_boundary"] = system_boundary
        research = self.get_package_artifact(package_id, "research")
        if research is not None:
            artifacts["research"] = research
        glossary = self.get_package_artifact(package_id, "glossary")
        if glossary is not None:
            artifacts["glossary"] = glossary
        measurement = self.get_package_artifact(package_id, "measurement")
        if measurement is not None:
            artifacts["measurement"] = measurement
        toolchain = self.get_package_artifact(package_id, "toolchain")
        if toolchain is not None:
            artifacts["toolchain"] = toolchain
        decision = self.get_package_artifact(package_id, "decision")
        if decision is not None:
            artifacts["decision"] = decision
        rewrites = self.get_package_artifact(package_id, "rewrites")
        if rewrites is not None:
            artifacts["rewrites"] = rewrites
        rewrite_what_if = self.get_package_artifact(package_id, "rewrite_what_if")
        if rewrite_what_if is not None:
            artifacts["rewrite_what_if"] = rewrite_what_if
        rewrite_plan = self.get_package_artifact(package_id, "rewrite_plan")
        if rewrite_plan is not None:
            artifacts["rewrite_plan"] = rewrite_plan
        rewrite_work_order = self.get_package_artifact(package_id, "rewrite_work_order")
        if rewrite_work_order is not None:
            artifacts["rewrite_work_order"] = rewrite_work_order
        connection_playbook = self.get_package_artifact(package_id, "connection_playbook")
        if connection_playbook is not None:
            artifacts["connection_playbook"] = connection_playbook
        adapter_execution_plan = self.get_package_artifact(package_id, "adapter_execution_plan")
        if adapter_execution_plan is not None:
            artifacts["adapter_execution_plan"] = adapter_execution_plan
        adapter_connection_kit = self.get_package_artifact(package_id, "adapter_connection_kit")
        if adapter_connection_kit is not None:
            artifacts["adapter_connection_kit"] = adapter_connection_kit
        adapter_evidence_templates = self.get_package_artifact(package_id, "adapter_evidence_templates")
        if adapter_evidence_templates is not None:
            artifacts["adapter_evidence_templates"] = adapter_evidence_templates
        adapter_connection_self_test = self.get_package_artifact(package_id, "adapter_connection_self_test")
        if adapter_connection_self_test is not None:
            artifacts["adapter_connection_self_test"] = adapter_connection_self_test
        adapter_integration_readiness = self.get_package_artifact(package_id, "adapter_integration_readiness")
        if adapter_integration_readiness is not None:
            artifacts["adapter_integration_readiness"] = adapter_integration_readiness
        external_connector_contract = self.get_package_artifact(package_id, "external_connector_contract")
        if external_connector_contract is not None:
            artifacts["external_connector_contract"] = external_connector_contract
        connector_implementation_guide = self.get_package_artifact(package_id, "connector_implementation_guide")
        if connector_implementation_guide is not None:
            artifacts["connector_implementation_guide"] = connector_implementation_guide
        connector_test_harness = self.get_package_artifact(package_id, "connector_test_harness")
        if connector_test_harness is not None:
            artifacts["connector_test_harness"] = connector_test_harness
        connector_acceptance_drills = self.get_package_artifact(package_id, "connector_acceptance_drills")
        if connector_acceptance_drills is not None:
            artifacts["connector_acceptance_drills"] = connector_acceptance_drills
        connector_acceptance_report = self.get_package_artifact(package_id, "connector_acceptance_report")
        if connector_acceptance_report is not None:
            artifacts["connector_acceptance_report"] = connector_acceptance_report
        connector_backlog = self.get_package_artifact(package_id, "connector_backlog")
        if connector_backlog is not None:
            artifacts["connector_backlog"] = connector_backlog
        connector_delivery_plan = self.get_package_artifact(package_id, "connector_delivery_plan")
        if connector_delivery_plan is not None:
            artifacts["connector_delivery_plan"] = connector_delivery_plan
        connector_risk_register = self.get_package_artifact(package_id, "connector_risk_register")
        if connector_risk_register is not None:
            artifacts["connector_risk_register"] = connector_risk_register
        interview_drill = self.get_package_artifact(package_id, "interview_drill")
        if interview_drill is not None:
            artifacts["interview_drill"] = interview_drill
        return {
            "package_id": package_id,
            "model_id": metadata["model_id"],
            "archive_filename": metadata["archive_filename"],
            "artifacts": artifacts,
            "saved_artifacts": artifacts["package"].get("saved_artifacts", {}),
        }

    def get_package_archive(self, package_id):
        metadata = self.get_package_metadata(package_id)
        if not metadata:
            return None
        archive_path = Path(metadata["archive_path"])
        if not archive_path.exists():
            return None
        return metadata, archive_path.read_bytes()
