cask "dayedge" do
  arch arm: "arm64", intel: "x86_64"

  version "1.1.0"
  sha256 arm:   "9469f6215655b0a2293356e9a04d7b77ca890685107a2a217f261c184aad0192",
         intel: "4ed2cf029b85d15df06ba00e57711a2d9b42cf0a7e093d367adf182bc5cbece1"

  url "https://github.com/dayedge/dayedge/releases/download/v#{version}/DayEdge-#{version}-#{arch}.zip"
  name "DayEdge"
  desc "Menu-bar calendar, reminders, and meeting alerts"
  homepage "https://github.com/dayedge/dayedge"

  depends_on macos: :sequoia

  app "DayEdge.app"

  # Self-signed releases need app-specific quarantine removal on install and upgrade.
  postflight_steps do
    run "/usr/bin/xattr", args: ["-dr", "com.apple.quarantine", "{{appdir}}/DayEdge.app"]
  end

  uninstall quit: "com.dayedge.app"

  caveats <<~EOS
    DayEdge is self-signed and not notarized by Apple.
    This cask removes download quarantine from DayEdge.app only.
  EOS
end
