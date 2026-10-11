cask "dayedge" do
  arch arm: "arm64", intel: "x86_64"

  version "1.0.1"
  sha256 arm:   "cc4e3095a196e831c2499d8a2dbce550a61d889a991189677beaa3a7393c3fca",
         intel: "f7cca53a511c18dbb7c2346d6975d62d41e67123d3f717cf042a90c5cc114e95"

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
