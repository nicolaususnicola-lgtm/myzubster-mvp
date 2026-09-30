import hashlib

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
