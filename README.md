# Fix for the communication between flatpak browsers and KeepassXC

This repository provides a script which automatically configures detected firefox and chromium based browsers that are installed as flatpaks to communicate with (the flatpak version of) KeepassXC.
During my usage, the result has been stable for months without having to refresh the setup, however, it's not impossible for this to break eventually (at which point you will likely just have to rerun the script).

## Supported Browsers

- Firefox <sup>confirmed</sup>
- Librewolf <sup>confirmed</sup>
- Zen Browser <sup>confirmed</sup>
- Chromium <sup>in testing</sup>
- Google Chrome <sup>in testing</sup>
- Brave <sup>in testing</sup>
- Floorp <sup>in testing</sup>
- Ungoogled Chromium <sup>in testing</sup>
- Waterfox <sup>in testing</sup>
- Vivaldi <sup>in testing</sup>

## Requirements

- Only works on x86_64 architectures at the moment

## Usage

1. Install all the flatpak browsers you want, as well as the flatpak version of keepassxc, e.g.:
   ```bash
   flatpak install org.keepassxc.KeePassXC org.mozilla.firefox org.chromium.Chromium io.gitlab.librewolf-community
   ```
2. Make sure, none of the affected browsers is running and run the script:
   ```bash
   python3 <(wget -O - https://github.com/theCalcaholic/fix-keepassxc-flatpak-browsers/releases/latest/download/fix-keepassxc-flatpak-browsers.py)
   ```
3. Restart KeePassXC and your browsers

## Credits

This project is based of other peoples' work, namely:

- [KeePassXC](https://keepassxc.org)
- [keepassxc-proxy-rust](https://github.com/varjolintu/keepassxc-proxy-rust)

Inspiration has been taken from a number of articles across the web, notably:

- https://discourse.flathub.org/t/how-to-run-firefox-and-keepassxc-in-a-flatpak-and-get-the-keepassxc-browser-add-on-to-work/437
- https://www.snamellit.com/posts/keepassxc-and-flatpak/
