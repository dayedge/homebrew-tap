cask "dayedge" do
  arch arm: "arm64", intel: "x86_64"

  version "1.0.0"
  sha256 arm:   "0d727abeec52b27dca622687ab97abf5c5757ba924f5689296f4e34799d51292",
         intel: "1a462c92b6b64de74fc3a930ef1d1b88ebeaf7429694c3ed1783ae5950de8751"

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
