import hashlib
import subprocess
import sys

from src.core import knowledge_proof


def test_sha256_file_hashes_exact_bytes(tmp_path):
    payload = tmp_path / "card.json"
    payload.write_bytes(b'{"id":"card-1"}')
    assert knowledge_proof.sha256_file(payload) == hashlib.sha256(payload.read_bytes()).hexdigest()


def test_verify_knowledge_proof_match(monkeypatch, tmp_path):
    payload = tmp_path / "card.json"
    payload.write_bytes(b"canonical bytes")
    expected = "0x" + hashlib.sha256(payload.read_bytes()).hexdigest()
    monkeypatch.setattr(knowledge_proof, "read_knowledge_hash", lambda *args, **kwargs: expected)

    result = knowledge_proof.verify_knowledge_proof(
        payload,
        "0x21787249Df054132093FcF09bB914C0CCC539390",
        expected_hash=expected,
    )

    assert result["status"] == "MATCH"
    assert result["payload_matches_onchain"] is True
    assert result["payload_matches_expected"] is True


def test_verify_knowledge_proof_detects_mismatch(monkeypatch, tmp_path):
    payload = tmp_path / "card.json"
    payload.write_bytes(b"changed bytes")
    monkeypatch.setattr(
        knowledge_proof,
        "read_knowledge_hash",
        lambda *args, **kwargs: "0x" + ("00" * 32),
    )

    result = knowledge_proof.verify_knowledge_proof(
        payload,
        "0x21787249Df054132093FcF09bB914C0CCC539390",
    )

    assert result["status"] == "NO_MATCH"
    assert result["payload_matches_onchain"] is False


def test_committed_proof_v2_payload_digest():
    payload = "proofs/knowledge-card-6abaaefb3a7460c4574a45fd-v1.json"
    assert knowledge_proof.sha256_file(payload) == "6097e05866bafceec24663d2638cb1dae5742ac78284abbfd45cc9c3b0bfb845"


def test_proof_v2_against_sepolia():
    result = knowledge_proof.verify_knowledge_proof(
        "proofs/knowledge-card-6abaaefb3a7460c4574a45fd-v1.json",
        "0x21787249Df054132093FcF09bB914C0CCC539390",
        expected_hash="0x6097e05866bafceec24663d2638cb1dae5742ac78284abbfd45cc9c3b0bfb845",
    )
    assert result["status"] == "MATCH"


def test_visual_verifier_page():
    from src.api.server import app
    client = app.test_client()
    response = client.get("/knowledge-proof-verifier")
    assert response.status_code == 200
    assert b"Knowledge Proof Verifier" in response.data
    assert b"Verifica Proof" in response.data


def test_cli_returns_nonzero_for_changed_payload(monkeypatch, tmp_path):
    from scripts import verify_knowledge_proof as cli
    payload = tmp_path / "changed.json"
    payload.write_bytes(b"changed payload")
    monkeypatch.setattr(
        cli,
        "verify_knowledge_proof",
        lambda *args, **kwargs: {"status": "NO_MATCH"},
    )
    assert cli.main([str(payload), "0x21787249Df054132093FcF09bB914C0CCC539390"]) == 1


def test_cli_returns_nonzero_when_rpc_is_unavailable(monkeypatch, tmp_path):
    import requests
    from scripts import verify_knowledge_proof as cli
    payload = tmp_path / "card.json"
    payload.write_bytes(b"payload")

    def unavailable(*args, **kwargs):
        raise requests.ConnectionError("RPC unavailable")

    monkeypatch.setattr(cli, "verify_knowledge_proof", unavailable)
    assert cli.main([str(payload), "0x21787249Df054132093FcF09bB914C0CCC539390"]) == 2


def test_cli_can_run_directly_from_repo_root():
    result = subprocess.run(
        [sys.executable, "scripts/verify_knowledge_proof.py", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Verify exact Knowledge Card payload bytes against Ethereum Sepolia." in result.stdout
