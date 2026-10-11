# DayEdge Homebrew tap

Install DayEdge on macOS 15 or later:

```sh
brew install --cask dayedge/tap/dayedge
```

Homebrew selects the Apple Silicon or Intel archive and verifies its SHA-256 checksum.
Use a current version of Homebrew (`brew update`).

## Updates

```sh
brew update
brew upgrade --cask dayedge/tap/dayedge
```

## Signing

DayEdge is self-signed and not notarized by Apple. This cask removes the download quarantine attribute from the installed `DayEdge.app` after installation and upgrades, so it can open without a separate Terminal command. It does not change global macOS security settings.

## Maintaining the cask

Publish the app release first, then run one command from this repository (Python 3.9+, no dependencies):

```sh
python3 scripts/update-cask.py
```

The script selects GitHub's latest published stable release, downloads both Apple Silicon and Intel ZIPs,
and verifies each archive against its published `.sha256` file before updating the version and both hashes
in `Casks/dayedge.rb`. It refuses drafts, prereleases, downgrades, missing assets, and checksum mismatches.
Failures leave the cask unchanged. Release URLs already interpolate the version and architecture.

To select a particular published version, or verify the current cask without writing:

```sh
python3 scripts/update-cask.py --version 1.0.1
python3 scripts/update-cask.py --check
```

`GH_TOKEN` is optional for the GitHub API; ZIP downloads use public URLs without sending the token.
Review and commit the resulting diff, then push it or open a PR to publish the tap update.
The script does not install or upgrade the app on this Mac.

Validate changes with:

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
ruby -c Casks/dayedge.rb
```

Keep the app name and minimum macOS version aligned with the app.
