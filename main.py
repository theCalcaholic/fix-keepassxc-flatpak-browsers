#!/usr/bin/env python

import sys
import os
from pathlib import Path
import json
import shutil
import subprocess
import urllib.request

def apply_zen_workaround():
    subprocess.run(
        ["flatpak", "override", "app.zen_browser.zen", "--persist=.mozilla"],
        check=True
    )
    moz_path = Path.home() / '.var/app/app.zen_browser.zen/.mozilla'
    moz_path.mkdir(parents=True, exist_ok=True)
    (moz_path / 'native-messaging-hosts').symlink_to(Path('../.zen/native-messaging-hosts'))


quirks = {
    "app.zen_browser.zen": apply_zen_workaround
}

class BrowserConfig:
    def __init__(self, browser_name, flatpak_id, config_dir, browser_type):
        self.name = browser_name
        self.flatpak_id = flatpak_id
        self._config_dir = config_dir
        self.browser_type = browser_type

    @property
    def nmh_dirname(self) -> str:
        if self.browser_type == "firefox":
            return "native-messaging-hosts"
        else:
            return "NativeMessagingHosts"

    @property
    def nmh_path(self) -> Path:
        return Path.home() / ".var/app" / self.flatpak_id / self._config_dir / self.nmh_dirname
    @property
    def nmh_kpxc_path(self) -> Path:
        return self.nmh_path / kpxc_nmh_config_filename

    @property
    def config_path(self) -> Path:
        return Path.home() / ".var/app" / self.flatpak_id / self._config_dir


kpxc_nmh_config_filename = "org.keepassxc.keepassxc_browser.json"

target_browsers = [
    BrowserConfig("Firefox", "org.mozilla.firefox", ".mozilla", "firefox"),
    BrowserConfig("Librewolf", "io.gitlab.librewolf-community", ".librewolf", "firefox"),
    BrowserConfig("Zen Browser", "app.zen_browser.zen", ".zen", "firefox"),
    # Disabled because this might be a bad idea :)
    #BrowserConfig("Mullvad Browser", "net.mullvad.MullvadBrowser", ".mullvad", "firefox"),
    BrowserConfig("Chromium", "org.chromium.Chromium", "config/chromium", "chromium"),
    BrowserConfig("Google Chrome", "com.google.Chrome", "config/google-chrome", "chromium"),
    BrowserConfig("Brave Browser", "com.brave.Browser", "config/BraveSoftware/Brave-Browser", "chromium"),
    BrowserConfig("Floorp", "one.ablaze.floorp", ".floorp", "firefox"),
    BrowserConfig("Ungoogled Chromium", "io.github.ungoogled_software.ungoogled_chromium", "config/chromium", "chromium"),
    BrowserConfig("Waterfox", "net.waterfox.waterfox", ".mozilla", "firefox"),
    BrowserConfig("Vivaldi", "com.vivaldi.Vivaldi", "config/vivaldi", "chromium"),

]

flatpak_prefix_path = Path.home() / ".var/app"
firefox_host_cfg_dir = Path.home() / ".mozilla"
firefox_host_nmh_kpcx_config = firefox_host_cfg_dir / "native-messaging-hosts" / kpxc_nmh_config_filename
chromium_host_cfg_dir = Path.home() / ".config/chromium"
chromium_host_nmh_kpxc_config = chromium_host_cfg_dir / "NativeMessagingHosts" / kpxc_nmh_config_filename



firefox_host_nmh_kpcx_config.parent.mkdir(parents=True, exist_ok=True)
chromium_host_nmh_kpxc_config.parent.mkdir(parents=True, exist_ok=True)

with firefox_host_nmh_kpcx_config.open(mode="r", encoding="utf-8") as f:
    firefox_kpxc_nmh_config_data = json.load(f)
with chromium_host_nmh_kpxc_config.open(mode="r", encoding="utf-8") as f:
    chromium_kpxc_nmh_config_data = json.load(f)

container_cmd: str | None = None
if shutil.which("podman") is not None:
    container_cmd = "podman"
elif shutil.which("docker") is not None:
    res0 = subprocess.run(["docker", "-v"])
    if res0.returncode == 0:
        container_cmd = "docker"

if container_cmd is None:
    urllib.request.urlretrieve("https://github.com/theCalcaholic/fix-keepassxc-flatpak-browsers/releases/latest/download/keepassxc-proxy", firefox_host_nmh_kpcx_config.parent / 'keepassxc-proxy')
    os.chmod(firefox_host_nmh_kpcx_config.parent / 'keepassxc-proxy', 0o750)
else:
    res1 = subprocess.run([
        container_cmd, "run", "--rm",
        "-v", str(firefox_host_nmh_kpcx_config.parent) + ":/nmh:z",
        "docker.io/rust:alpine",
        "sh", "-c",
        "apk add git && "
        "git clone https://github.com/varjolintu/keepassxc-proxy-rust.git && cd keepassxc-proxy-rust &&"
        "RUSTFLAGS='-C link-arg=-s -Clink-self-contained=y -Clinker=rust-lld' cargo build --release --target x86_64-unknown-linux-musl && "
        "cp target/x86_64-unknown-linux-musl/release/keepassxc-proxy /nmh/"
    ])
    if res1.returncode != 0:
        print(f"WARN: Retrieving keepassxc-proxy failed with exit code {res1.returncode}: '{res1.stderr}'")
        sys.exit(1)

shutil.copy(firefox_host_nmh_kpcx_config.parent / "keepassxc-proxy", chromium_host_nmh_kpxc_config.parent / "keepassxc-proxy")

flatpaks = os.listdir(Path.home() / ".var/app")

for browser in target_browsers:
    if not browser.flatpak_id in flatpaks:
        continue
    print(f"=> Setting up {browser.name}")
    res2 = subprocess.run([
        "flatpak", "override",
        "--user", 
        "--filesystem=xdg-run/app/org.keepassxc.KeePassXC:ro", 
        browser.flatpak_id
    ])
    if res2.returncode != 0:
        print(f"WARN: Setting flatpak permissions for {browser.flatpak_id} failed with exit code {res2.returncode}: '{res2.stderr}'")
  
    if not browser.nmh_path.exists():
        browser.nmh_path.mkdir(parents=True)
    binary_path = browser.nmh_path / "keepassxc-proxy"
    if browser.browser_type == "firefox":
        shutil.copy(firefox_host_nmh_kpcx_config.parent / "keepassxc-proxy", binary_path)
    else:
        shutil.copy(chromium_host_nmh_kpxc_config.parent / "keepassxc-proxy", binary_path)

    kpxc_cfg_data = json.loads(json.dumps(
        firefox_kpxc_nmh_config_data if browser.browser_type == "firefox"
        else chromium_kpxc_nmh_config_data
    ))
    kpxc_cfg_data["path"] = str(binary_path)

    with browser.nmh_kpxc_path.open(mode="w", encoding="utf-8") as f:
        json.dump(kpxc_cfg_data, f)

    if browser.flatpak_id in quirks:
        quirks[browser.flatpak_id]()

    print("<= done.")
