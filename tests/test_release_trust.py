import hashlib
import re
from importlib.resources import as_file, files
from pathlib import Path
from unittest.mock import Mock

import pytest
import yaml
from sigstore.models import Bundle, TrustedRoot
from sigstore.verify import Verifier
from sigstore.verify.policy import Identity

from nanobot import release_trust
from nanobot.releases import ReleaseArtifact, ReleaseManifest, release_filenames
from scripts.verify_release_approval import verify_manifest


@pytest.fixture
def crypto_verifier(monkeypatch):
    # Deterministic offline test root from the pinned upstream distribution.
    # Production must refresh its TUF trust root, not read a caller-selected root.
    resource = files("sigstore._store").joinpath("https%3A%2F%2Ftuf-repo-cdn.sigstage.dev/trusted_root.json")
    with as_file(resource) as path:
        verifier = Verifier(trusted_root=TrustedRoot.from_file(str(path)))
    monkeypatch.setattr(Verifier, "production", lambda: verifier)
    return verifier


def test_real_signature_is_valid_but_not_an_official_release_approval(crypto_verifier):
    fixtures = Path(__file__).parent / "fixtures/sigstore"
    payload = (fixtures / "bundle_v3.txt").read_bytes()
    proof = (fixtures / "bundle_v3.txt.sigstore").read_bytes()
    bundle = Bundle.from_json(proof)
    identity = Identity(identity="william@yossarian.net", issuer="https://github.com/login/oauth")
    crypto_verifier.verify_artifact(payload, bundle, identity)
    with pytest.raises(Exception):
        crypto_verifier.verify_artifact(payload + b"modified", bundle, identity)
    with pytest.raises(ValueError, match="official release approval"):
        release_trust.verify_release_approval(payload, proof)


def test_policy_is_fixed_to_manual_official_main_workflow(monkeypatch):
    from datetime import datetime, timedelta, timezone

    from cryptography import x509
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.x509.oid import NameOID, ObjectIdentifier

    seen = []
    class Capture:
        def verify_artifact(self, payload, bundle, policy):
            seen.append(policy)
    monkeypatch.setattr(Verifier, "production", lambda: Capture())
    monkeypatch.setattr(Bundle, "from_json", lambda _: object())
    release_trust.verify_release_approval(b"manifest", b"proof")
    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "policy-only fixture")])
    def certificate(identity, issuer, trigger):
        builder = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
                   .public_key(key.public_key()).serial_number(1)
                   .not_valid_before(datetime.now(timezone.utc) - timedelta(minutes=1))
                   .not_valid_after(datetime.now(timezone.utc) + timedelta(minutes=1))
                   .add_extension(x509.SubjectAlternativeName([x509.UniformResourceIdentifier(identity)]), False))
        for oid, value in (("1", issuer), ("2", trigger)):
            builder = builder.add_extension(x509.UnrecognizedExtension(
                ObjectIdentifier("1.3.6.1.4.1.57264.1." + oid), value.encode()), False)
        return builder.sign(key, hashes.SHA256())
    expected = (release_trust.RELEASE_IDENTITY, release_trust.RELEASE_ISSUER, "workflow_dispatch")
    seen[0].verify(certificate(*expected))
    for changed in (
        (expected[0].replace("HKUDS", "attacker"), expected[1], expected[2]),
        (expected[0].replace("refs/heads/main", "refs/pull/1/merge"), expected[1], expected[2]),
        (expected[0], "https://example.com", expected[2]),
        (expected[0], expected[1], "pull_request_target"),
    ):
        with pytest.raises(Exception):
            seen[0].verify(certificate(*changed))


@pytest.mark.parametrize("failure", ["malformed", "unavailable", "oversized"])
def test_failed_verification_has_no_checksum_only_fallback(monkeypatch, failure):
    unavailable = Mock(side_effect=OSError("trust service unavailable"))
    monkeypatch.setattr(Verifier, "production", unavailable)
    proof = b"x" * (256 * 1024 + 1) if failure == "oversized" else b"invalid"
    if failure == "unavailable":
        proof = (Path(__file__).parent / "fixtures/sigstore/bundle_v3.txt.sigstore").read_bytes()
    with pytest.raises(ValueError):
        release_trust.verify_release_approval(b"manifest", proof)
    assert unavailable.call_count == (1 if failure == "unavailable" else 0)


def test_malformed_approval_is_rejected_without_contacting_trust_service(monkeypatch):
    verifier = Mock()
    monkeypatch.setattr(Verifier, "production", verifier)
    with pytest.raises(ValueError, match="official release approval"):
        release_trust.verify_release_approval(b"manifest", b"not a bundle")
    verifier.assert_not_called()


def test_signing_handoff_requires_independently_approved_identity_and_digest(tmp_path):
    version = "0.3.7.dev1"
    manifest = ReleaseManifest(
        version=version,
        source_commit="a" * 40,
        candidate_commit="b" * 40,
        requires_python=">=3.11",
        artifacts=[
            ReleaseArtifact(filename=name, size=123, sha256="c" * 64)
            for name in sorted(release_filenames(version))
        ],
    )
    path = tmp_path / "release-manifest.json"
    path.write_text(manifest.model_dump_json())
    approved = dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(), version=manifest.version,
                    source_commit=manifest.source_commit, candidate_commit=manifest.candidate_commit)
    assert verify_manifest(path, **approved) == manifest
    for field in approved:
        with pytest.raises(ValueError):
            verify_manifest(path, **(approved | {field: "wrong"}))


def test_approval_workflow_is_manual_gated_and_has_no_publication_permission():
    workflow = Path(__file__).parents[1] / ".github/workflows/release-approve.yml"
    definition = yaml.load(workflow.read_text(), Loader=yaml.BaseLoader)
    assert set(definition["on"]) == {"workflow_dispatch"}
    assert definition["permissions"] == {}
    job = definition["jobs"]["approve"]
    assert job["environment"] == "release-approval"
    assert job["permissions"] == {"contents": "read", "id-token": "write"}
    assert "github.ref == 'refs/heads/main'" in job["if"]
    assert "vars.NANOBOT_RELEASE_SIGNING_ENABLED == 'true'" in job["if"]
    for step in job["steps"]:
        if "uses" in step:
            assert re.fullmatch(r"[\w-]+/[\w-]+@[0-9a-f]{40}", step["uses"])
