# macOS Customizable Time Announcer

A lightweight tool that speaks the current time aloud on your Mac, with more control than macOS gives you out of the box.

## Why This Exists
macOS has a built-in **"Announce the time"** feature (System Settings → Control Center/Dock & Menu Bar → Clock Options). It is handy, but limited:

| | macOS built-in | This tool |
|---|---|---|
| Interval | Only every hour, half hour or quarter hour | Any number of minutes (e.g., 10, 20, 45) |
| Quiet hours / active hours | Not available | Announce only inside a time range, or stay silent during one |
| Quick control | Click through System Settings each time | One-line commands from the Terminal (`saytime stop`, `saytime start`, ...) |
| Fixed clock times vs. "every N minutes from now" | Clock times only | Either |
| Room to grow | None | Open source, so you can add your own features |


## Features
- **Flexible Trigger Modes:** Announce on clock-face intervals (e.g., exactly on the 15th, 30th, 45th minute) or on relative intervals (e.g., every 15 minutes from the last announcement).
- **Time Windows:** Only announce (`only`) or stay silent (`avoid`) during a chosen time range (e.g., only from 6:00 PM to 10:30 AM).
- **Control CLI (`saytime`):** Start, stop, check status, or change settings from the command line. No manual editing of config files is needed.

## Requirements
- A Mac running macOS
- `python3` available in your shell. If it is missing, run `xcode-select --install` or install Python from [python.org](https://www.python.org/downloads/) or Homebrew.
- `git` (to clone the repository)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/TheKSoni/mac_time_announcer.git
   cd mac_time_announcer
   ```

2. **Copy the scripts to your home folder:**
   ```bash
   mkdir -p ~/Scripts
   cp Scripts/announcer.py Scripts/saytime ~/Scripts/
   chmod +x ~/Scripts/announcer.py ~/Scripts/saytime
   ```

3. **Make the `saytime` command available globally:**
   ```bash
   sudo mkdir -p /usr/local/bin
   sudo ln -sf ~/Scripts/saytime /usr/local/bin/saytime
   ```

4. **Install and start the background agent:**
   ```bash
   mkdir -p ~/Library/LaunchAgents
   cp LaunchAgents/com.user.timeannouncer.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.user.timeannouncer.plist
   ```
   The plist resolves `$HOME` dynamically, so it works for any user without edits.

5. **Verify the installation:**
   ```bash
   launchctl list | grep timeannouncer   # the agent should be listed
   saytime status                       # shows the current settings
   python3 ~/Scripts/announcer.py        # runs once; speaks only if the schedule and time window allow
   ```

> **Note:** The default settings announce every 15 minutes (clock-face) **only between 18:00 and 10:30**. To change this, see [Usage](#usage-controls-via-saytime) below, for example `saytime range avoid 22:00 07:00`.

## Usage Controls via `saytime`
| Command | Description |
|---|---|
| `saytime help` | Show the usage menu. |
| `saytime status` | Show the current settings (JSON). |
| `saytime start` | Enable announcements. |
| `saytime stop` | Disable announcements globally. |
| `saytime interval 30` | Announce every 30 minutes (e.g., 15, 30, 60). |
| `saytime type clock` | Align to clock-face minutes (e.g., :00, :15, :30, :45). |
| `saytime type relative` | Announce every N minutes, counted from the moment you run the command. |
| `saytime type relative --use_last_run` | Same, but keep counting from the last announcement instead of restarting. Also works with `saytime interval`. |
| `saytime range only 18:00 10:30` | Announce only between 6:00 PM and 10:30 AM. |
| `saytime range avoid 22:00 07:00` | Stay silent overnight. |
| `saytime debug on` / `off` | Toggle debug logging to `~/.config/time_announcer_logs/` (the latest 3 daily files are kept). |

Settings are stored in `~/.config/time_announcer.json`. The file is created automatically on first run, and changes take effect on the next minute tick.

## Uninstallation
```bash
launchctl unload ~/Library/LaunchAgents/com.user.timeannouncer.plist
rm ~/Library/LaunchAgents/com.user.timeannouncer.plist
sudo rm /usr/local/bin/saytime
rm ~/Scripts/announcer.py ~/Scripts/saytime
rm -rf ~/.config/time_announcer.json ~/.config/time_announcer_logs   # optional: remove settings and logs
```

## Development
For architecture, testing, debugging, and deploying code changes, see [DEVELOPMENT.md](DEVELOPMENT.md).

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author
Created by **Kunal Soni ([@theksoni](https://github.com/theksoni))**.
