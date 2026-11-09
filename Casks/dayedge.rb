cask "dayedge" do
  arch arm: "arm64", intel: "x86_64"

  version "1.2.0"
  sha256 arm:   "2a4e69cb483ec66692581e6dbe43718fbc9e43c0b823f8e8618eb02a3e186e88",
         intel: "116ae72e7e6cb70153fdf0a392286c88011af77dcd5f35477e35fa03a741cb90"

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
