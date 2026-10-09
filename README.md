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

Publish the app release first. Update `version` and both architecture-specific `sha256` values in `Casks/dayedge.rb` using the release ZIPs and their checksum files. Keep the release URLs, app name, and minimum macOS version aligned with the app.
