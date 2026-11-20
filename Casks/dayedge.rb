cask "dayedge" do
  arch arm: "arm64", intel: "x86_64"

  version "1.2.1"
  sha256 arm:   "ac4b267c57647615fd68ee5f075a7a5305db579e0a64c99f18377e60dd2b131e",
         intel: "7063f522d093b39b53f63df441101ef83a2490c07b3e56e35c383bc2f9c1774a"

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
