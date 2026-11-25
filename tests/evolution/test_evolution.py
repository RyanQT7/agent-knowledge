from __future__ import annotations

import difflib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.evolution.audit import audit, markdown_links
from scripts.evolution.common import normalize_arxiv, normalize_doi, normalize_repo_url
from scripts.evolution.discovery import _base_record, _cursor_key, _is_relevant, _query_string, discover, load_config
from scripts.evolution.proposals import apply_proposal, check_proposal, create_proposal, patch_paths, validate_proposal

ROOT = Path(__file__).resolve().parents[2]


class NormalizationTests(unittest.TestCase):
    def test_stable_identifiers(self) -> None:
        self.assertEqual(normalize_doi("https://doi.org/10.1145/123.456"), "10.1145/123.456")
        self.assertEqual(normalize_arxiv("https://arxiv.org/abs/2510.12345v3"), ("2510.12345", "v3"))
        self.assertEqual(normalize_repo_url("https://github.com/Owner/Repo.git?tab=readme"), "https://github.com/Owner/Repo")

    def test_metadata_relevance_rejects_broad_noise(self) -> None:
        config = load_config(ROOT / "evolution/config/watchlist.yaml")
        topics = {item["id"]: item for item in config["topics"]}
        leto = {"title": "Leto: Utility-Centric Agent Memory", "abstract": "Agent memory improves future responses."}
        unrelated = {"title": "The Practice of Interpretation in International Law", "abstract": "A historical analysis."}
        self.assertTrue(_is_relevant(leto, topics["agent-memory"]))
        self.assertFalse(_is_relevant(unrelated, topics["agent-memory"]))
        self.assertIn("belief state agent", _query_string({"keywords": ["a", "b", "c", "d", "belief state agent"]}))


class DiscoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "evolution/config").mkdir(parents=True)
        for name in ("watchlist.yaml", "limits.yaml"):
            (self.root / "evolution/config" / name).write_bytes((ROOT / "evolution/config" / name).read_bytes())
        (self.root / "papers").mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def paper_record(topic: dict, query: str, version: str = "v1") -> dict:
        return _base_record(
            topic, "arxiv", query,
            title="A Test Paper on Agent Memory", authors=["A. Researcher"],
            publication_date="2026-10-10", publication_status="preprint",
            arxiv_id="2510.12345" + version, source_version=version,
            source_url="https://arxiv.org/abs/2510.12345" + version,
            source_record_id="2510.12345", abstract="Agent memory and belief-state updates.",
        )

    def test_duplicate_import_is_idempotent(self) -> None:
        def provider(topic, query, since, limits):
            return [self.paper_record(topic, query)]

        first = discover(self.root, topic_ids=["agent-memory"], source_filter={"arxiv"}, provider_overrides={"arxiv": provider}, run_id="dedup-1")
        second = discover(self.root, topic_ids=["agent-memory"], source_filter={"arxiv"}, provider_overrides={"arxiv": provider}, run_id="dedup-2")
        rows = (self.root / "evolution/inbox/candidates.jsonl").read_text().splitlines()
        self.assertEqual(len(rows), 1)
        self.assertEqual(first["candidates_added"], 1)
        self.assertEqual(second["candidates_added"], 0)
        row = json.loads(rows[0])
        self.assertTrue(row["novelty_reason"])
        self.assertTrue(row["relevance_reason"])
        self.assertTrue(row["related_questions"])

    def test_new_arxiv_version_is_an_update_event(self) -> None:
        paper_dir = self.root / "papers" / "test-paper"
        paper_dir.mkdir()
        (paper_dir / "notes.md").write_text(
            "# A Test Paper on Agent Memory\n\n- Authors: A. Researcher\n- arXiv: https://arxiv.org/abs/2510.12345v1\n",
            encoding="utf-8",
        )

        def provider(topic, query, since, limits):
            return [self.paper_record(topic, query, "v2")]

        result = discover(self.root, topic_ids=["agent-memory"], source_filter={"arxiv"}, provider_overrides={"arxiv": provider}, run_id="version-1")
        row = json.loads((self.root / "evolution/inbox/candidates.jsonl").read_text().splitlines()[0])
        self.assertEqual(result["candidate_version_updates"], 1)
        self.assertEqual(row["event_type"], "version_update")
        self.assertEqual(row["previous_version"], "2510.12345v1")

    def test_failed_query_does_not_advance_cursor(self) -> None:
        config = load_config(self.root / "evolution/config/watchlist.yaml")
        topic = next(item for item in config["topics"] if item["id"] == "agent-memory")
        query = '"agent memory" OR "long term memory agent" OR "memory evolution agent"'
        key = _cursor_key(topic["id"], "arxiv", query)
        old_cursor = {"query": query, "topic_id": topic["id"], "source": "arxiv", "last_successful_at": "2026-11-10T00:00:00Z", "since": "2026-11-03"}
        (self.root / "evolution/state").mkdir(parents=True)
        (self.root / "evolution/state/discovery.json").write_text(json.dumps({"version": 1, "cursors": {key: old_cursor}, "topic_last_queried_at": {}}), encoding="utf-8")

        def fail(topic, query, since, limits):
            raise RuntimeError("simulated source outage")

        result = discover(self.root, topic_ids=["agent-memory"], source_filter={"arxiv"}, provider_overrides={"arxiv": fail}, run_id="failed-1")
        state = json.loads((self.root / "evolution/state/discovery.json").read_text())
        self.assertEqual(result["status"], "failed")
        self.assertEqual(state["cursors"][key], old_cursor)


class AuditTests(unittest.TestCase):
    def test_markdown_link_checker_ignores_code_examples(self) -> None:
        text = """A [real](../ok.md) link.\n\n```markdown\n[template](../missing.md)\n```\n\nInline `[example](missing.md)` text.\n"""
        self.assertEqual(markdown_links(text), ["../ok.md"])

    def test_thirteen_isolated_audit_cases(self) -> None:
        fixture_path = ROOT / "tests/evolution/fixtures/audit-cases.jsonl"
        cases = [json.loads(line) for line in fixture_path.read_text().splitlines() if line.strip()]
        self.assertGreaterEqual(len(cases), 10)
        self.assertTrue(all(case["synthetic"] is True for case in cases))

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for directory in ("concepts", "papers/a", "papers/b", "notes", "code", "evolution/claims", "evolution/inbox", "evolution/state", "evolution/audits"):
                (root / directory).mkdir(parents=True, exist_ok=True)
            (root / "INDEX.md").write_text("# Index\n\n- [A](papers/a/notes.md)\n- [B](papers/b/notes.md)\n- [Concepts](concepts/README.md)\n", encoding="utf-8")
            (root / "papers/a/notes.md").write_text("# Same Paper\n\n- arXiv: https://arxiv.org/abs/2510.12345v1\n\nFull note evidence.\n", encoding="utf-8")
            (root / "papers/b/notes.md").write_text("# Same Paper\n\n- arXiv: https://arxiv.org/abs/2510.12345v1\n\nFull note evidence.\n", encoding="utf-8")
            (root / "concepts/README.md").write_text("# Concepts\n", encoding="utf-8")
            (root / "concepts/orphan.md").write_text("# Orphan\n\nNo links point here.\n", encoding="utf-8")
            (root / "notes/broken.md").write_text("[missing](../missing.md)\n", encoding="utf-8")
            (root / "notes/nested.md").write_text("[valid relative link](../concepts/README.md)\n", encoding="utf-8")
            (root / "notes/questions.md").write_text("| Q | Open | Still unresolved |\n", encoding="utf-8")
            (root / "evolution/inbox/candidates.jsonl").write_text(
                json.dumps({"candidate_id": "dup-candidate", "status": "discovered", "title": "One"}) + "\n" + json.dumps({"candidate_id": "dup-candidate", "status": "discovered", "title": "One"}) + "\n" + json.dumps({"candidate_id": "new-version", "status": "discovered", "title": "Same Paper", "arxiv_id": "2510.12345v2", "event_type": "version_update"}) + "\n",
                encoding="utf-8",
            )
            claims = [
                {"claim_id": "missing-source", "statement": "active with no evidence", "claim_type": "paper_fact", "scope": "test", "status": "active", "evidence": [], "related_claims": [], "supersedes": [], "last_reviewed_at": "2026-11-25"},
                {"claim_id": "true-conflict", "statement": "claim with contradicting evidence", "claim_type": "cross_source_synthesis", "scope": "test", "status": "active", "evidence": [{"source_id": "src-conflict", "source_version": "v1", "source_uri": "https://example.org/a", "locator": "Sec. 1", "relation": "contradicts", "accessed_at": "2026-11-25"}], "related_claims": [], "supersedes": [], "last_reviewed_at": "2026-11-25"},
                {"claim_id": "scope-qualification", "statement": "claim narrowed by scope", "claim_type": "cross_source_synthesis", "scope": "benchmark only", "status": "active", "evidence": [{"source_id": "src-scope", "source_version": "v1", "source_uri": "https://example.org/scope", "locator": "Sec. 2", "relation": "qualifies", "accessed_at": "2026-11-25"}], "related_claims": [], "supersedes": [], "last_reviewed_at": "2026-11-25"},
                {"claim_id": "stale-version", "statement": "old version claim", "claim_type": "paper_fact", "scope": "test", "status": "active", "evidence": [{"source_id": "arxiv:2510.12345", "source_version": "2510.12345v1", "source_uri": "https://arxiv.org/abs/2510.12345v1", "locator": "Sec. 1", "relation": "supports", "accessed_at": "2026-11-25"}], "related_claims": [], "supersedes": [], "last_reviewed_at": "2026-11-25"},
                {"claim_id": "no-update", "statement": "grounded stable claim", "claim_type": "paper_fact", "scope": "test", "status": "active", "evidence": [{"source_id": "stable", "source_version": "v1", "source_uri": "https://example.org/stable", "locator": "Sec. 1", "relation": "supports", "accessed_at": "2026-11-25"}], "related_claims": [], "supersedes": [], "last_reviewed_at": "2026-11-25"},
                {"claim_id": "contested-no-evidence", "statement": "contested claim with no evidence", "claim_type": "paper_fact", "scope": "test", "status": "contested", "evidence": [], "related_claims": [], "supersedes": [], "last_reviewed_at": "2026-11-25"},
                {"claim_id": "same-source", "statement": "source identity alias", "claim_type": "paper_fact", "scope": "test", "status": "active", "evidence": [{"source_id": "stable", "source_version": "v1", "source_uri": "https://different.example/stable", "locator": "Sec. 1", "relation": "supports", "accessed_at": "2026-11-25"}], "related_claims": [], "supersedes": [], "last_reviewed_at": "2026-11-25"},
            ]
            (root / "evolution/claims/claims.jsonl").write_text("".join(json.dumps(claim) + "\n" for claim in claims), encoding="utf-8")
            report = audit(root, run_id="audit-fixture")
            issue_types = {item["issue_type"] for item in report["findings"]}
            self.assertIn("duplicate_paper_identity", issue_types)
            self.assertIn("broken_internal_link", issue_types)
            self.assertIn("invalid_claim_schema", issue_types)
            self.assertIn("unresolved_claim_conflict", issue_types)
            self.assertIn("scope_qualification", issue_types)
            self.assertIn("stale_source_version", issue_types)
            self.assertIn("open_research_questions", issue_types)
            self.assertIn("orphan_concept", issue_types)
            self.assertIn("source_id_uri_mismatch", issue_types)
            self.assertIn("duplicate_candidate_id", issue_types)
            self.assertIn("invalid_candidate_schema", issue_types)
            invalid_claim_ids = {item["affected_claim"] for item in report["findings"] if item["issue_type"] == "invalid_claim_schema"}
            self.assertIn("missing-source", invalid_claim_ids)
            self.assertIn("contested-no-evidence", invalid_claim_ids)
            self.assertNotIn("no-update", invalid_claim_ids)
            self.assertNotIn("scope-qualification", {item["affected_claim"] for item in report["findings"] if item["issue_type"] == "unresolved_claim_conflict"})
            self.assertNotIn("notes/nested.md", {item["affected_file"] for item in report["findings"] if item["issue_type"] == "broken_internal_link"})


class ProposalTests(unittest.TestCase):
    def test_proposal_path_limit_and_stale_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "concepts/memory.md"
            target.parent.mkdir()
            before = "# Memory\n\nCurrent line.\n"
            after = "# Memory\n\nCurrent line.\nNew evidence-backed line.\n"
            target.write_text(before, encoding="utf-8")
            patch = "\n".join(difflib.unified_diff(before.splitlines(), after.splitlines(), fromfile="a/concepts/memory.md", tofile="b/concepts/memory.md", lineterm="")) + "\n"
            patch_file = root / "change.patch"
            patch_file.write_text(patch, encoding="utf-8")
            evidence = [{"source_id": "arxiv:2510.12345", "source_version": "2510.12345v1", "source_uri": "https://arxiv.org/abs/2510.12345", "locator": "Sec. 3", "relation": "qualifies", "accessed_at": "2026-11-25"}]
            proposal_path = create_proposal(proposal_id="p-test", title="Test update", run_id="test-run", research_focus="Agent Memory", files=["concepts/memory.md"], patch_file=patch_file, evidence=evidence, root=root)
            proposal = json.loads(proposal_path.read_text())
            self.assertEqual(patch_paths(proposal["patch"]), {"concepts/memory.md"})
            self.assertEqual(validate_proposal(proposal, root), [])
            self.assertEqual(proposal["base_revision"], "unavailable")
            proposal["files"] = ["../../outside.md"]
            self.assertTrue(any("invalid proposal path" in error for error in validate_proposal(proposal, root)))
            proposal = json.loads(proposal_path.read_text())
            target.write_text(before + "intervening change\n", encoding="utf-8")
            self.assertTrue(any("base hash changed" in error for error in validate_proposal(proposal, root)))

    def test_application_requires_explicit_approval_and_clean_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(["git", "init", "-q", "-b", "candidate/test"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Evolution Test"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "evolution-test@example.invalid"], cwd=root, check=True)
            target = root / "concepts/memory.md"
            target.parent.mkdir()
            before = "# Memory\n\nOld, grounded line.\n"
            after = "# Memory\n\nUpdated, grounded line.\n"
            target.write_text(before, encoding="utf-8")
            subprocess.run(["git", "add", "concepts/memory.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            patch = "\n".join(difflib.unified_diff(before.splitlines(), after.splitlines(), fromfile="a/concepts/memory.md", tofile="b/concepts/memory.md", lineterm="")) + "\n"
            patch_file = root / "candidate.patch"
            patch_file.write_text(patch, encoding="utf-8")
            evidence = [{"source_id": "arxiv:2510.12345", "source_version": "2510.12345v1", "source_uri": "https://arxiv.org/abs/2510.12345", "locator": "Sec. 3", "relation": "supports", "accessed_at": "2026-11-25"}]
            proposal = create_proposal(proposal_id="p-approved", title="Approved update", run_id="test-run", research_focus="Agent Memory", files=["concepts/memory.md"], patch_file=patch_file, evidence=evidence, root=root)
            self.assertEqual(len(json.loads(proposal.read_text())["base_revision"]), 40)
            self.assertEqual(check_proposal(json.loads(proposal.read_text()), root), [])
            with self.assertRaisesRegex(ValueError, "explicit human approval"):
                apply_proposal(proposal, "", "", root)
            self.assertEqual(target.read_text(), before)
            result = apply_proposal(proposal, "researcher", "Approve only this one-file patch", root)
            self.assertEqual(result["status"], "applied")
            self.assertEqual(target.read_text(), after)
            self.assertFalse(subprocess.run(["git", "log", "-1", "--format=%s"], cwd=root, check=True, capture_output=True, text=True).stdout.strip() == "Approved update")

    def test_proposal_can_add_a_new_paper_note_only_after_explicit_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(["git", "init", "-q", "-b", "candidate/test"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Evolution Test"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "evolution-test@example.invalid"], cwd=root, check=True)
            (root / "INDEX.md").write_text("# Index\n", encoding="utf-8")
            subprocess.run(["git", "add", "INDEX.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
            patch = (
                "diff --git a/papers/leto/notes.md b/papers/leto/notes.md\n"
                "new file mode 100644\n"
                "--- /dev/null\n"
                "+++ b/papers/leto/notes.md\n"
                "@@ -0,0 +1,2 @@\n"
                "+# Leto: Utility-Centric Agent Memory\n"
                "+\n"
            )
            patch_file = root / "new-note.patch"
            patch_file.write_text(patch, encoding="utf-8")
            evidence = [{"source_id": "arxiv:2611.33005", "source_version": "2611.33005v1", "source_uri": "https://arxiv.org/html/2611.33005v1", "locator": "Sec. 3, Eq. 1", "relation": "supports", "accessed_at": "2026-11-25"}]
            proposal_path = create_proposal(proposal_id="p-new-paper", title="Add Leto paper note", run_id="test-run", research_focus="Agent Memory", files=["papers/leto/notes.md"], patch_file=patch_file, evidence=evidence, root=root)
            proposal = json.loads(proposal_path.read_text())
            self.assertEqual(proposal["base_hashes"]["papers/leto/notes.md"], "ABSENT")
            self.assertEqual(validate_proposal(proposal, root), [])
            self.assertFalse((root / "papers/leto/notes.md").exists())

            before_index = "# Index\n"
            after_index = "# Index\n\n- [Leto](papers/leto/notes.md)\n"
            index_patch = "\n".join(difflib.unified_diff(before_index.splitlines(), after_index.splitlines(), fromfile="a/INDEX.md", tofile="b/INDEX.md", lineterm="")) + "\n"
            index_patch_file = root / "index.patch"
            index_patch_file.write_text(index_patch, encoding="utf-8")
            dependent_proposal = create_proposal(proposal_id="p-index-link", title="Index Leto note", run_id="test-run", research_focus="Agent Memory", files=["INDEX.md"], patch_file=index_patch_file, evidence=evidence, depends_on=["p-new-paper"], root=root)
            same_proposal = create_proposal(proposal_id="p-index-link", title="Index Leto note", run_id="test-run", research_focus="Agent Memory", files=["INDEX.md"], patch_file=index_patch_file, evidence=evidence, depends_on=["p-new-paper"], root=root)
            self.assertEqual(same_proposal, dependent_proposal)
            with self.assertRaisesRegex(FileExistsError, "different content"):
                create_proposal(proposal_id="p-index-link", title="Index Leto note", run_id="test-run", research_focus="Agent Memory", files=["INDEX.md"], patch_file=index_patch_file, evidence=evidence, depends_on=[], root=root)
            with self.assertRaisesRegex(ValueError, "dependency is not applied"):
                apply_proposal(dependent_proposal, "researcher", "Apply after note", root)
            self.assertEqual((root / "INDEX.md").read_text(), before_index)

            result = apply_proposal(proposal_path, "researcher", "Approve this isolated candidate only", root)
            self.assertEqual(result["status"], "applied")
            self.assertEqual((root / "papers/leto/notes.md").read_text(), "# Leto: Utility-Centric Agent Memory\n\n")
            linked = apply_proposal(dependent_proposal, "researcher", "Apply the dependent index link", root)
            self.assertEqual(linked["status"], "applied")
            self.assertEqual((root / "INDEX.md").read_text(), after_index)


if __name__ == "__main__":
    unittest.main()
