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
