# Developer Guide (`mac_time_announcer`)

This document provides developer guidelines and instructions for testing, debugging, and deploying changes to the macOS Time Announcer utility.

---

## 1. Architecture Overview

```
                      ┌──────────────────────────────────────────┐
                      │ macOS launchd Background Agent           │
                      │ (~/Library/LaunchAgents/*.plist)         │
                      └────────────────────┬─────────────────────┘
                                           │ Fires every minute at :00
                                           ▼
┌─────────────────────────────────┐   ┌──────────────────────────┐
│ CLI Control (saytime)           │   │ Core Engine              │
│ - Modifies config               │   │ (~/Scripts/announcer.py) │
│ - Reloads daemon                │   └────────────┬─────────────┘
└───────────────┬─────────────────┘                │ Reads
                │ Writes                           │
                ▼                                  ▼
      ┌────────────────────────────────────────────────────────┐
      │ Configuration Store (~/.config/time_announcer.json)    │
      └────────────────────────────────────────────────────────┘
```

- **`Scripts/announcer.py`**: The execution script triggered by `launchd` every minute at second `:00`. Checks config filters and runs speech synthesis.
- **`Scripts/saytime`**: Command-line dashboard for users to adjust intervals, modes (`only` vs `avoid`), time ranges, and enable/disable states.
- **`LaunchAgents/com.user.timeannouncer.plist`**: macOS launch daemon profile that schedules execution at second `:00` across all hours.
- **`~/.config/time_announcer.json`**: Runtime state and user preferences.

---

## 2. When Do You Need to Redeploy?

- **Changing Schedule / Settings via `saytime`?**
  - **No deployment needed.** Changes written to `~/.config/time_announcer.json` are read fresh on the next minute tick.
- **Modifying Python Source Code or Plist?**
  - **Deployment required.** You must sync modified files to `~/Scripts/` and/or reload `launchd`.

---

## 3. Step-by-Step: Making Code Changes

### Step 1: Verify Syntax and Linting
Before copying files, ensure there are no syntax errors:
```bash
python3 -m py_compile Scripts/announcer.py Scripts/saytime
```

### Step 2: Test the Scripts Directly
Run the announcer manually from the terminal to verify logic and speech output:
```bash
# Test announcer execution
python3 Scripts/announcer.py

# Test CLI tool commands
python3 Scripts/saytime help
python3 Scripts/saytime status
```

### Step 3: Deploy Modified Scripts Locally
Copy the updated scripts to your local executable directory and set executable permissions:
```bash
cp Scripts/announcer.py Scripts/saytime ~/Scripts/
chmod +x ~/Scripts/announcer.py ~/Scripts/saytime
```

If you changed `Scripts/_saytime` (the zsh tab-completion file), redeploy it too:
```bash
cp Scripts/_saytime ~/.zsh/completions/
exec zsh   # reload shell so compinit picks up the new file
```

### Step 4: Deploy Plist Changes (if Plist Modified)
If you modified `LaunchAgents/com.user.timeannouncer.plist`:
```bash
# Validate plist XML format
plutil -lint LaunchAgents/com.user.timeannouncer.plist

# Copy to LaunchAgents directory
cp LaunchAgents/com.user.timeannouncer.plist ~/Library/LaunchAgents/

# Reload daemon
launchctl unload ~/Library/LaunchAgents/com.user.timeannouncer.plist 2>/dev/null
launchctl load ~/Library/LaunchAgents/com.user.timeannouncer.plist
```

---

## 4. Debugging & Verification

### Check Daemon Status
Check if `launchd` is running the daemon properly:
```bash
launchctl list | grep timeannouncer
```
- **Exit Code `0`**: Healthy and running normally.
- **Exit Code `2`**: File not found (check script path or permissions).
- **Exit Code non-zero**: Script crashed or threw an uncaught error.

### Inspect Logs
Enable debug logging via CLI:
```bash
saytime debug on
```
Debug logs are created daily in `~/.config/time_announcer_logs/YYYY-MM-DD.log`. When more than 3 daily log files exist, the oldest files are automatically pruned so only the 3 most recent days are retained:
```bash
# View today's debug log
cat ~/.config/time_announcer_logs/$(date +%Y-%m-%d).log

# Disable debug logging when finished
saytime debug off
```

---

## 5. Development Best Practices & Constraints

1. **Dynamic Paths Only**:
   - Never hardcode usernames or static paths like `/Users/yourname/` in `.plist` files.
   - Always use dynamic `$HOME` resolution (e.g. `/bin/zsh -c 'python3 "$HOME/Scripts/announcer.py"'`).

2. **Native Speech Synthesis**:
   - Use `subprocess.run(["say", ...])` directly.
   - Avoid `osascript` string interpolation to prevent shell quote escaping syntax errors.

3. **Time Window Modes**:
   - Standard mode values are `"only"` (announce only in window) and `"avoid"` (silence in window).

4. **License & Copyright Attribution**:
   - Maintain the MIT License and copyright headers at the top of all script files.
