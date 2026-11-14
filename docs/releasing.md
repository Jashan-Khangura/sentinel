# Release checklist

Use this checklist to prepare releases. Preparation does not authorize publication. Pushing tags, publishing GitHub Releases, uploading to PyPI and deploying documentation are separate operations.

## Release cadence

The application does not check for, download or install releases. Stable and Preview describe publication tracks for maintainers; users update through the package manager or deployment that owns their installation. See [Manual Updates and Data Migrations](./updating.md) for user instructions.

| Release | Trigger | Public destination | Documentation |
| --- | --- | --- | --- |
| Stable feature release | Manual, when needed | Final GitHub Release and PyPI; update the release catalogue | Full version documentation and any planned announcement |
| Stable patch | Manual, when a reviewed fix is ready; do not wait for a feature milestone | Same stable destinations and checks | Generated change notes and necessary upgrade instructions; update only affected documentation |
| Preview / dev | Daily workflow, after maintainers enable it | GitHub prerelease and protected `release-index` catalogue; not PyPI | Generated change notes; no new documentation edition for each build |

These are three publication lines, not three build systems. Feature and patch releases both use the stable track; dev uses the preview track. A patch does not require a Preview first or a complete wiki and promotional refresh. Preserve necessary tests and release checks, and reuse unaffected evidence under the [verification guidance](../.agent/workflow.md).

Implementation status: **Verify Release Candidate** supports manual preparation and opt-in daily Preview preparation. It generates draft notes and reuses the same five-platform build and acceptance jobs. It does not publish. Automatic prerelease upload, signing handoff and catalogue advancement are not connected yet; PyPI publication requires a separate manual workflow after its trusted publisher is configured. Daily preparation is disabled by default. Do not describe this first step as an available daily public release channel.

Record the requested track, exact source and candidate identity. Unchanged source, failed checks, missing assets, incomplete acceptance or absent approval leaves the last verified release in place. Scheduled execution can be delayed; there is no promise of a new release every day.

### Shared preparation entry

Run **Verify Release Candidate** at the chosen source ref with the existing `next_stable`, `channel` and optional `retain_installable` inputs. Both Stable release sizes use the same entry. The workflow generates `release-notes.md` from commit subjects and includes it in candidate reports and an explicitly retained installable handoff. Review necessary upgrade instructions and security wording before publication. These notes are local artifacts, not a GitHub Release, including a draft Release.

Stable notes start at the preceding final release on the selected source line, ignoring Preview tags. Preview notes can start at the preceding Preview's source. Neither uses an unrelated branch's newest tag. The planned source is the event SHA throughout the run; preparation does not follow a moving branch.

For daily preparation, maintainers can later set `NANOBOT_PREVIEW_BASE` to the next unreleased final version and explicitly enable `NANOBOT_DAILY_CANDIDATES_ENABLED=true`. The schedule is currently 00:17 UTC. Only the official repository's `main` can use it. It requires successful latest push CI for that exact SHA and skips a source/base already accepted by this workflow. Failed candidates can run again; manual dispatch remains available to retain a new handoff. Both paths share the existing workflow run number for `.devN`. Update the base after its final release; an already tagged base is refused.

Daily runs retain small reports only, not the optional installable handoff. They still use the existing five native runners and temporary wheel transfers, so review the runner and storage cost before enabling the variable. This is a preparation switch, not permission to sign or publish. No repository variable or protection setting is changed by adding this workflow code.

### Stable patch procedure

1. Select the supported stable baseline and reviewed fixes. If `main` contains unfinished features, branch from that baseline and backport only the required fixes. Do not relabel an unverified Preview as stable.
2. Allocate an unused final version, update both version declarations, and follow **Prepare a candidate**. Patches require the same packaging, platform-install and data-preservation gates as feature releases.
3. Publish approved immutable files in order: GitHub, PyPI, public-download checks, then the catalogue's `stable` pointer. Preserve `preview` and withdrawal history. A stable patch older than an installed Preview must not be offered as a downgrade.
4. Publish concise fix notes and required operator actions. Users install each release through the package manager or deployment that owns their installation.

### Preview procedure

1. Select an exact reviewed `main` commit with passing required CI; skip it if its source SHA matches the last accepted candidate. Record the next unreleased stable base and an unused increasing Preview sequence.
2. Use **Verify Release Candidate** for that ref and base, manually or through enabled daily preparation. It prepares a version-only candidate, builds the WebUI and five platform wheels once, and runs macOS arm64/x64, Linux arm64/x64 and Windows x64 clean-install acceptance against the exact manifest-bound wheels without publication. Ordinary PR CI keeps its Linux x64/Windows x64 matrix; candidate preparation uses all five runners. Require the **Candidate required** check to pass; build-only reports are insufficient.
3. Select `retain_installable` and preserve the accepted `installable-candidate` handoff before expiry. Temporary `candidate-native` inputs and `prepared-candidate` artifacts are not accepted handoffs. Complete native installation and runtime checks against those exact bytes; automated fixtures do not establish interactive desktop behavior. Keep candidate SHA, manifest hash, coverage and known issues together; CI reports alone are neither installable artifacts nor publication consent.
4. With separate approval, publish immutable `v<version>` at the **candidate** commit and a GitHub prerelease, never the latest stable release. Upload the complete verified set, manifest and notes; make the pinned installer source publicly reachable.
5. Verify all public sizes/hashes and clean public installation acceptance before advancing `preview` with a new catalogue generation. Validate against the latest catalogue, preserve `stable` and withdrawals, and serialize stable, Preview and withdrawal writes. A stale publisher must reread and revalidate.
6. After partial upload, leave the feed unchanged and resume only from the original verified files. Lost or changed bytes require a new version and repeated acceptance. Withdraw unsafe candidates with a reason and offer a newer fix; never rewind the feed or restore user data.

Use Python version ordering: `0.3.6.dev42 < 0.3.6.dev43 < 0.3.6 < 0.3.7.dev1` (illustrative versions). Once a final base ships, previews need a later base; allocate it after accounting for stable patches. The workflow uses `github.run_number` for `N` in `X.Y.Z.devN`; do not reset the sequence without checking published versions. Reruns cannot replace published bytes. Rebuild and test final releases under their final identity; never rename `.devN` wheels.

### Launch gates and automation boundary

Before publishing Preview, obtain approval for index ownership/protection, publication credentials, source retention and exact packaged/public-download acceptance. Candidate preparation does not activate a public channel, schedule, protected publisher or PyPI upload. Preserve approved release bytes and source outside expiring CI storage for their required lifetime.

Stable releases remain manual. Daily Preview preparation requires the explicit opt-in above; automatic publication needs a separate reviewed implementation and activation. Keep builds read-only and publication permissions in the protected stage. Keep one serialized catalogue writer.

## Prepare a candidate

1. Choose the previous release and exact candidate commit. Use a clean worktree without local configuration, sessions, credentials or unrelated changes.
2. Update `project.version` in `pyproject.toml` and the final source-only fallback in `nanobot/__init__.py`.
3. Review the generated change notes and add required upgrade/rollback instructions. Feature releases can add highlights and acknowledgements; ordinary patches do not need a full announcement. Verify counts: commits are not merged PRs. Coordinate security disclosures separately.
4. Run Python, WebUI and Discord CI checks against the final commit, not an earlier PR head. Review installation, configuration, session and API changes.
5. Run `uv build --out-dir <artifact-directory>` in a clean output directory without `NANOBOT_SKIP_WEBUI_BUILD`. The build hook bundles WebUI in sdist and wheel; the wheel is built from the sdist.
6. Run `twine check` on intermediates, inspect contents and record SHA-256 hashes. Test installation in an isolated environment outside the checkout and upgrade from previous stable with disposable configuration/sessions, never a maintainer's live workspace.
7. For feature releases, prepare the version documentation in `Re-bin/nanobot-web` under its `MAINTAINING.md`. For patches, update only affected instructions and translations; do not require a new complete manual or promotional page when the existing documentation still applies. Preserve existing URLs and previous versions, and verify affected site routes. Pin source references where applicable and never advertise an unpublished package. Preview notes cover development changes without creating a documentation edition each day.
8. Build the Python distributions, check them with `twine check`, validate wheel RECORDs/tags/permissions, and test installation on all five supported platforms.
9. Merge release preparation only after current checks/reviews pass. Compare the merged source tree with the tested candidate; rebuild/recheck changes. Reconcile changelog and documentation links, then tag the verified commit, not an unchecked later `main` tip.

### Legacy history and proxy compatibility window

Retain legacy model JSONL, WebUI JSONL / segments and per-feature proxy migration throughout **0.4.x**. Removing them before the next minor release would prevent older installations from migrating through a 0.4.x patch release.

**TODO(0.5.0):** Remove the legacy importers, proxy conversion, startup hooks and migration-specific tests; update upgrade fixtures and current documentation for SQLite history and `network.proxy` / `useProxy` only. Preserve SQLite schema upgrades and current-format behavior. The OpenAI API selector has its own compatibility window below.

### OpenAI API selector compatibility window

v0.4.0 and v0.4.1 included automatic conversion of `providers.openai.apiType` / `api_type`. The first release without conversion must note in its release notes that users can save old configuration with v0.4.1 and must update launcher environment variables separately.

### Assemble release artifacts

After `uv build`, from the exact release checkout:

```bash
uv run python -m scripts.release_candidate assemble --source-commit <full-source-commit> \
  --wheel <intermediates>/nanobot_ai-X.Y.Z-py3-none-any.whl \
  --sdist <intermediates>/nanobot_ai-X.Y.Z.tar.gz \
  --output <new-artifact-directory>
```

Assembly creates the five platform-tagged wheels from the universal wheel and the matching sdist, regenerating each wheel's `RECORD`. It verifies candidate version/commit identity, WebUI assets, metadata, source payloads, and application bytes across the distributions before writing the manifest. It refuses existing output directories.

PyPI receives **five platform wheels and one sdist**. Record source commit, version, files, hashes, checks and remaining gates; source changes require rebuilding and rechecking.

Final releases also require `release-manifest.json` for `stable`. Run `scripts.release_candidate assemble` from the clean final-version checkout, using that final commit as `--source-commit` without Preview preparation. GitHub receives the same wheels/sdist and manifest; PyPI receives only wheels/sdist. Verify final source and public bytes before catalogue advancement.

For same-build candidate acceptance on all five native targets, run **Verify Release Candidate** at the exact final-version ref with `channel=stable`, `next_stable` equal to that declared version and `retain_installable=true`. Stable preparation copies the exact commit without changing version declarations or creating a Preview commit; it rejects mismatched versions and existing stable tags. The default `channel=preview` retains the version-only Preview preparation. Both modes are read-only preparation, require **Candidate required** and retain accepted files for one day; neither publishes a tag, release, PyPI package or feed. Download and independently preserve the accepted handoff before expiry, then complete manual installation checks against that same manifest.

## Publish, with maintainer approval

### Release approval proof

The official installer's exact-version handoff requires `release-manifest.json.sigstore.json` beside the manifest on the exact GitHub release. The installer verifies Sigstore's production certificate chain/transparency proof and accepts only `HKUDS/nanobot`'s manual `release-approve.yml` on `main`. The signed manifest must match version, wheel size/digest and, for Preview, catalogue commit/manifest binding. Verification runs before package installation. The application does not discover releases or update running gateways; unsigned releases cannot use this verified installer handoff.

Before setting the repository variable `NANOBOT_RELEASE_SIGNING_ENABLED=true`, an administrator must protect `main` and the `release-approval` environment: require independent review, prevent self-review, allow deployment only from `main`, and restrict bypass and changes to the workflow/signing requirements. Signing is disabled without that variable. No long-lived signing key or Apple Developer ID is required.

After candidate tests and dependency review, take version, manifest SHA-256, source SHA and candidate SHA from retained acceptance evidence, not public downloads. Upload the proposed manifest through the separately authorized release handoff, then manually run **Approve Exact Release** from `main` with those values and obtain environment review. The hash-locked job checks/signs the exact manifest without installing candidate code or writing releases, PyPI or the catalogue. Separately authorize attaching its proof, verify the public proof before advancing either channel, and preserve it with candidate evidence before its three-day CI expiry.

Regenerate the signing lock only in a reviewed dependency update:

```bash
uv pip compile .github/release-signing-requirements.in --python-version 3.11 \
  --python-platform x86_64-manylinux_2_17 --generate-hashes --no-header \
  --output-file .github/release-signing-requirements.txt
```

Review resolved dependencies; hashes are not malware review. Before the first release, verify a clean signed installation with the official installer and an owner-managed package upgrade. Private fixtures are not signature evidence.

The proof authenticates release approval, not reproducible builds or harmless code. Compromised authorized workflows/reviewers, malicious source that passes review and compromised runtime dependencies remain risks. The signing lock does not lock runtime resolution, which retains the installation owner's policy. A reviewed runtime dependency inventory, public signed upgrade continuity and verified repository protection settings remain security-release gates; do not claim comprehensive supply-chain protection without them. The first installer and checksum source also need a trusted distribution channel.

1. Complete pre-tag gates, then create and push exactly `vX.Y.Z`; never move or reuse a published tag.
2. Create the matching GitHub Release as a draft. A tag push alone does not publish the package to PyPI.
3. Attach the five platform wheels, sdist, `release-manifest.json` and its approval proof. Confirm tag sources match the manifest and uploaded hashes match preflight.
4. Click **Publish release** only after the complete signed artifact set is attached. A final `vX.Y.Z` release starts **Validate published release for PyPI**; its successful completion triggers the protected **Publish approved release to PyPI** workflow on `main`. A prerelease or tag push does not start publication.
5. A different maintainer must approve the `pypi` environment; check both Actions runs for success. The publisher verifies the signed manifest, tag identity and all public release files, then uploads only the matching sdist and five wheels. It does not build packages. If the trigger did not run, including when a release was created using `GITHUB_TOKEN`, or the release actor was a bot, a human maintainer must manually run **Publish approved release to PyPI** from `main` with the version and `pypi` destination. Until signing is enabled, an authorized maintainer can use the existing manual upload route for the same checked files; unsigned releases cannot use the verified installer handoff.
6. Verify clean PyPI installation and the bundled WebUI. After all public GitHub/PyPI files pass, advance the stable catalogue entry and preserve Preview/withdrawal history. The application does not notify users about new releases; they update through their installation owner. Only then merge the wiki PR: its `main` deploys automatically. Confirm all localized `/docs/latest/` routes select the new version and old-version links still work.
7. Add the dated [Release Archive](./release-archive.md) entry and record publication links/status. Feature releases can include a separate announcement; ordinary patches can use the generated notes with necessary additions. Complete any coordinated advisory and reporter notifications separately.

### Configure trusted publishing

An administrator must protect the `pypi` GitHub environment so only `main` can deploy. Require a second maintainer, prevent self-review, and disable administrator bypass. Protect changes to `main` and both publication workflows. Keep independent review on the separate release-approval workflow. The publisher checks the original Release actor from GitHub's workflow event; an approval by that actor is rejected. In the `nanobot-ai` PyPI project's **Publishing** settings, add a GitHub trusted publisher for owner `HKUDS`, repository `nanobot`, workflow `publish-pypi.yml` and environment `pypi`. These names must match exactly. No long-lived PyPI token is needed by the workflow. Before using the production workflow, test the default `testpypi` destination with a separately registered `nanobot-ai` TestPyPI project and its own trusted publisher using environment `testpypi`; protect that environment in GitHub too. TestPyPI registration does not grant production access. The test still requires a complete signed public release of an unused TestPyPI version.

If an upload only partially succeeds, preserve the original approved bytes. Choose **Run workflow** from `main` with the same version and destination to start a new run. Do not use **Re-run jobs**: GitHub can reuse outputs from an earlier attempt, and review history is scoped to the whole run. The new run compares existing index files with the signed release and uploads only missing files. A production run that uploads files needs a new independent approval. A mismatch, yanked file, unexpected file or unavailable index stops the run for investigation. Published versions cannot be replaced; do not rebuild or upload a different file under the same version. The approval proof and verification cannot establish manual installation or interactive acceptance, which remain separate release gates.

## If a gate fails

Do not publish to PyPI with missing artifacts or verification. Keep public documentation's `latest` on the usable stable version. Correct published packages with a new version, never replacement code behind an existing tag. Before downgrading a migrated installation, stop all old processes and follow the documented session rollback procedure.

## Installer identity checks

Fresh base-package installs use the official installer's dedicated venv regardless of optional managers on PATH. `nanobot-install.json` is written before venv/download work so failed first installs retain their owner; it is not readiness proof. Existing venv/uv/pipx installations are not adopted or moved. The receipt records extras and opts `webui` into persistent background launch; unrecorded installs retain their lifecycle. Include this distinction and the instance-specific stop command in release notes.

Linux/Windows CI builds a platform wheel and runs the public installer in a private home without Bun/Node/Git on PATH, then checks the managed receipt, installed WebUI and gateway. Python/WebUI changes also require these jobs. CI retains small reports, not candidate binaries. Startup probes and offline installer fixtures do not replace package-install or public-download acceptance.

Run `pytest tests/test_install_scripts.py` with `uv` and `pipx` available. It uses private homes, offline fixture wheels and real managers, without a gateway or real application install: `install.sh` on Unix and Windows PowerShell with `install.ps1` on Windows. CI provisions pipx outside application dependencies. Verify these owner-preservation requirements:

- Launch the selected persistent environment's isolated Python, not `pipx run`, disposable tools or an arbitrary PATH executable. Existing recognized installations take priority over newly available managers; multiple recognized installs require explicit choice. An ordinary active venv is explicit; uv/pipx environments must use their manager.
- Preserve uv constraints. Generic pipx upgrades can drop constraints/options; the installer must refuse pipx records with those settings, lock workflows or unconfirmed sources. The owner must review and preserve them. Exact wheels may replace a wheel source, not registry constraints/options; pipx upgrades must retain requested extras and refuse wheels missing recorded extras.
- A failed selected manager must not fall through to another installation, even on first install. Verify the exact persistent package version before onboarding: a successful pinned/locked skip is not target installation. Restarted gateway identity is a separate check.

Verify the exact-handoff options against the pinned installer, not an older script: `install.sh --wheel <path> --sha256 <published-hash>` / `install.ps1 -Wheel <path> -Sha256 <published-hash>`, or `install.sh --release <version> --manifest-sha256 <trusted-manifest-hash>` / `install.ps1 -Release <version> -ManifestSha256 <trusted-manifest-hash>`. Wheel mode verifies checksum/package/version; release mode selects the matching platform tag and verifies size/hash/identity before invoking the original owner. No frontend toolchain or extra selector package is installed; the manager still checks Python/dependencies. Hashes must come from trusted metadata, not an unknown publisher.

Release downloads use official GitHub HTTPS hosts and configured HTTPS proxy; retain wheel sources at their recorded paths, including `~/.nanobot/downloads/releases` or `NANOBOT_RELEASE_CACHE`. Failed partial downloads are removed. Wheel-mode `--dry-run` / `-DryRun` verifies without installation/setup; release-mode dry-run checks only the manifest, creating no wheel/cache/environment/setup and proving neither wheel bytes nor dependency resolution.

These exact-version installer commands do not update a running gateway or back up its data. Stop writers and back up first. Review extras and recorded options for plain pip, suffixed/custom installs and external owners; see the [manual update guide](./updating.md). Installer fixtures alone do not establish live maintenance, backup or restart safety.

## Non-publishing preview preflight

**Verify Release Candidate** is read-only preparation, either manually requested or explicitly enabled for daily Preview: no tags/releases, PyPI or catalogue writes. It builds and checks five platform wheels and the sdist. Cross-compilation is neither native execution nor release approval.

Default retention is small identity/manifest/probe reports and installation guide for **three days**, without installable binaries. `retain_installable` preserves those exact checked artifacts plus a self-contained shallow Git repository for **one day** (about 400 MB). Keep this storage exception off for routine preflight or schedules; assess storage and call it out explicitly in workflow-change PRs before merge. Preserve approved handoffs before expiry; rebuilding expired files cannot reuse their verification. The source contains only candidate/source-parent history, not configuration or untracked files. `handoff.json` is written only after copied artifacts verify; interruption is not an accepted handoff.

After assembly, the workflow transfers all five manifest-bound wheels by immutable artifact ID; each matching runner installs its wheel into a separate venv without Bun/Node/Git on the install PATH. Isolated Python checks version/commit/import identity and all Vite-manifest assets, including lazy chunks, through the installed handler. With `--gateway`, it starts a private foreground CLI gateway with no provider/MCP configuration, disabled heartbeat and two loopback ports, then checks readiness, HTML and process/listener cleanup. Unix shutdown must be graceful; Windows termination is labelled, not graceful-shutdown evidence. No model task or external channel is exercised.

On another supported platform, check a disposable native installation without changing its package:

```bash
<installed-venv-python> -I scripts/verify_installed_release.py \
  --version <candidate-version> --commit <candidate-commit> \
  --gateway --report <new-report-path>
```

Use the candidate commit, not its parent. The probe rejects checkout imports/unisolated invocation and avoids user configuration/credentials. Omit `--gateway` for asset-only checks. Reports identify OS/CPU/probes and are success-only, never overwritten; failure cleans up children and prints a bounded redacted log tail. This is package/startup evidence, not migration, public-download or five-platform E2E acceptance.

For local preparation, use a full source SHA and new output outside the checkout (illustrative base/sequence):

```bash
python -m scripts.release_candidate prepare \
  --source-commit <full-commit-sha> --base 0.3.6 --sequence 42 \
  --output <new-candidate-directory>
```

Preparation leaves the checkout untouched and deterministically creates a version-only commit for identical inputs. Build Python distributions from it, then assemble and verify them from the candidate:

```bash
python -m scripts.release_candidate assemble --source-commit <original-source-sha> \
  --wheel <intermediates>/nanobot_ai-0.3.6.dev42-py3-none-any.whl \
  --sdist <intermediates>/nanobot_ai-0.3.6.dev42.tar.gz \
  --output <new-artifact-directory>
```

Assembly refuses existing output and emits the manifest only after complete-set, version/commit, WebUI, RECORD, source, and permissions checks. It compares sdist sources/resources against tracked candidate files with packaging exclusions, and all wheels' application/WebUI bytes against the sdist. Commit markers and RECORDs alone are insufficient; these comparisons do not prove reproducible frontend compilation. Recheck with `python -m scripts.release_candidate verify --source-commit <original-source-sha> --artifacts <artifact-directory>`; it may reuse an identical manifest, never replace different bytes.

Generate the handoff from the same candidate:

```bash
python -m scripts.release_candidate instructions --source-commit <original-source-sha> \
  --artifacts <artifact-directory> --output <new-install-guide-path.md>
```

The generator rechecks artifacts/manifest and writes a non-overwriting guide outside the immutable upload directory. When both installers match the supported implementation, commands fetch the exact candidate's installer with the retained manifest hash for automatic platform selection; older candidates keep manual commands, never mutable `main` or assumed flags. Publication must make pinned installer source reachable.

The guide records version, source/candidate commits, five hash-bound wheel URLs and separate new/existing base-package commands for uv, pipx and pip venv. Commands verify local size/SHA-256 with the standard library before manager invocation; URL hash fragments alone are insufficient for the tested uv commands. Retain wheel paths recorded by managers. Manual commands move to an advanced section when automatic entry is supported; no new manifest schema or installer executable is introduced.

Before offering the guide, publish/verify exact public files and add release changes, native coverage, migration instructions and stop/backup prerequisites. Review extras and locked/suffixed/external-owner options; independently verify installed version and restarted gateway. Manager fixtures do not prove restart/migration, and the guide is neither publication approval nor channel selection.

The candidate clone borrows source Git objects; preserve its source repository until retained in an approved permanent ref. Partial assembly has no accepted manifest and must not be uploaded. Source-offer commitment, native launch, clean install and publication gates still apply. Missing public assets must be recovered from original verified files, never overwritten by rebuilds.

Retain an exact local handoff outside temporary build storage:

```bash
python -m scripts.release_candidate retain --source-commit <original-source-sha> \
  --artifacts <verified-artifact-directory> --output <new-retained-directory>
```

Only `artifacts/` is the upload set; `source.git/`, `install.md` and `handoff.json` are maintenance evidence, not PyPI packages. Restore with `git clone --no-local <retained>/source.git <new-checkout>`, check HEAD against `handoff.json`, and rerun `release_candidate verify` on retained artifacts before separately approved publication. Keep native reports and release notes alongside them; retention adds no native, migration, interactive UI or public-download evidence.
