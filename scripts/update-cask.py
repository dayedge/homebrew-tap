#!/usr/bin/env python3
"""Update DayEdge's cask from a published release, verifying both ZIP checksums."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "dayedge/dayedge"
VERSION = re.compile(r"v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)\Z")
ARCHITECTURES = {"arm": "arm64", "intel": "x86_64"}


def request(url, api=False):
    headers = {"User-Agent": "DayEdge-tap-updater"}
    if api:
        headers.update({"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2026-03-10"})
        if token := os.environ.get("GH_TOKEN"):
            headers["Authorization"] = f"Bearer {token}"
    return urlopen(Request(url, headers=headers), timeout=60)


def release_version(release):
    tag = release.get("tag_name", "")
    if release.get("draft") or release.get("prerelease") or not release.get("published_at"):
        raise ValueError("Only published stable releases can update the cask")
    if not VERSION.fullmatch(tag):
        raise ValueError(f"Expected a stable version tag, got {tag!r}")
    return tag.removeprefix("v")


def checksum(text, filename):
    match = re.fullmatch(r"([0-9a-fA-F]{64})[ \t]+\*?([^\r\n]+)\s*", text.strip())
    if not match or match[2] != filename:
        raise ValueError(f"Invalid checksum file for {filename}")
    return match[1].lower()


def verified_checksums(release, version):
    assets = {asset["name"]: asset for asset in release["assets"]}
    expected = {}
    # Validate both architectures before downloading or changing the cask.
    for key, architecture in ARCHITECTURES.items():
        name = f"DayEdge-{version}-{architecture}.zip"
        for filename in (name, name + ".sha256"):
            if filename not in assets or assets[filename].get("state") != "uploaded":
                raise ValueError(f"Published release is missing {filename}")
        expected[key] = name
    checksums = {}
    for key, name in expected.items():
        base = f"https://github.com/{REPOSITORY}/releases/download/v{version}/{name}"
        with request(base + ".sha256") as response:
            digest = checksum(response.read().decode("utf-8"), name)
        with request(base) as response:
            hasher = hashlib.sha256()
            while chunk := response.read(1024 * 1024):
                hasher.update(chunk)
            actual = hasher.hexdigest()
        if actual != digest:
            raise ValueError(f"ZIP checksum does not match {name}.sha256")
        checksums[key] = digest
        print(f"Verified {name}: {digest}")
    return checksums


def update_text(original, version, checksums):
    if set(checksums) != set(ARCHITECTURES):
        raise ValueError("Both architecture checksums are required")
    current = re.search(r'^  version "([^"]+)"$', original, re.MULTILINE)
    if current is None or VERSION.fullmatch(current[1]) is None:
        raise ValueError("Expected one stable cask version")
    if tuple(map(int, version.split("."))) < tuple(map(int, current[1].split("."))):
        raise ValueError("Refusing to downgrade the cask")
    updated, count = re.subn(r'^  version "[^"]+"$', f'  version "{version}"', original, flags=re.MULTILINE)
    if count != 1:
        raise ValueError("Expected one cask version stanza")
    for key, digest in checksums.items():
        if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise ValueError(f"Invalid {key} digest")
        pattern = rf'(\b{key}:\s+")[0-9a-f]{{64}}(")'
        updated, count = re.subn(pattern, lambda match: match[1] + digest + match[2], updated)
        if count != 1:
            raise ValueError(f"Expected one {key} checksum")
    return updated


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", help="Published version (e.g. 1.0.1); defaults to GitHub's latest stable release")
    parser.add_argument("--check", action="store_true", help="Verify release ZIPs and report stale cask without writing")
    args = parser.parse_args()
    if args.version and not VERSION.fullmatch(args.version):
        parser.error("--version must be a stable version such as 1.0.1")
    endpoint = "tags/v" + args.version.removeprefix("v") if args.version else "latest"
    try:
        with request(f"https://api.github.com/repos/{REPOSITORY}/releases/{endpoint}", api=True) as response:
            release = json.load(response)
        version = release_version(release)
        cask = ROOT / "Casks/dayedge.rb"
        original = cask.read_text()
        hashes = verified_checksums(release, version)
        updated = update_text(original, version, hashes)
        if updated == original:
            print(f"DayEdge {version}: cask already current.")
            return
        if args.check:
            parser.exit(1, f"Cask is stale; run this command without --check to update to {version}.\n")
        temporary = cask.with_suffix(".rb.tmp")
        temporary.write_text(updated)
        temporary.replace(cask)
        print(f"Updated Casks/dayedge.rb to {version}. Review, commit, and push to publish the tap update.")
    except (URLError, TimeoutError, ValueError, OSError, KeyError) as error:
        parser.exit(1, f"Cask update failed: {error}\n")


if __name__ == "__main__":
    main()
