# Holloway v0.1 – DietPi writerDeck (Cage + Alacritty)
Holloway is a writerDeck designed for total focus. This first iteration was built with a lot of hardware that I had on hand as a proof of concept. 
## Requirements
### Hardware
- Computer: Raspberry Pi 4 Model B (aarch64)
- Monitor: Acer KB272 EBI 27" IPS Full HD (1920 x 1080)
- Keyboard: Keychron K3 Version 2, 75% Layout 84 Keys Ultra-Slim

> [!TIP]
> This was the only monitor I had available. I would **highly** recommend a monitor that is much smaller. My ideal size would be around 10.1 inches.
### System
- DietPi v9.19.2
- `cage` Wayland kiosk compositor
- `wlr-randr`: screen rotation utility (for vertical monitor support)
- `alacritty`: terminal emulator for a more modern _feel_
- `neovim`: text editor of choice

> [!NOTE]
> This is the set up I followed. I planned on starting with DietPi _only_ before I switched to wanting a more "modern" CLI-like experience. You can probably just use the Raspberry Pi OS as a base, but don't take my word for it!
## Installation
### DietPi
Flash the DietPi image to your microSD card and insert it into the device. Connect your keyboard and monitor, then power on. Follow the initial DietPi setup steps:
- Change Passwords: Set the root password and the "Global Software Password."
- DietPi-Config: Set your timezone, keyboard layout, and Wi-Fi credentials (if not using Ethernet).
- DietPi-Software: When the software list appears, select OpenSSH Client and OpenSSH Server (optional, but helpful for setup).
- Install: Select "Install" to download the base system updates and apply changes. The system will reboot.

### Core packages
Install `cage`, `alacritty`, and `wlr-randr` (optional). Log in as `root` and update the package repositories:
```bash
apt update
```

Install the compositor, terminal, and text editor:
```bash
sudo apt install cage alacritty neovim
```

Create a dedicated non-root user for the writing environment:
```bash
adduser your_username
```

Add this user to the necessary groups:
```bash
usermod -aG video,input,render writer
```
## Configuration
### Alacritty
Switch to the new user to manage configuration files:
```bash
su - your_username
```

Create the configuration directory and the YAML configuration file:
```bash
mkdir -p ~/.config/alacritty
nvim ~/.config/alacritty/alacritty.yml
```

> [!NOTE]
> Since I am using DietPi, I am creating a YAML configuration file for Alacritty instead of a TOML file.
Define the window, font, and color settings in `alacritty.yml`. The following is what I am using at the moment, but feel free to tweak this to your heart's content:

```yml
window:
  decorations: none
  startup_mode: Maximized
  dynamic_title: false

  padding:
    x: 25
    y: 25

mouse:
  hide_when_typing: true

font:
  normal:
    family: "FiraCode Nerd Font Mono"
    style: regular
  size: 13.0

colors:
  primary:
    background: '#1e1e2e'
    foreground: '#cdd6f4'
  normal:
    black:   '#45475a'
    red:     '#f38ba8'
    green:   '#a6e3a1'
    yellow:  '#f9e2af'
    blue:    '#89b4fa'
    magenta: '#f5c2e7'
    cyan:    '#94e2d5'
    white:   '#bac2de'
  bright:
    black:   '#585b70'
    red:     '#f38ba8'
    green:   '#a6e3a1'
    yellow:  '#f9e2af'
    blue:    '#89b4fa'
    magenta: '#f5c2e7'
```
### Auto-launch

> [!NOTE]
> There is a simple option within the  `dietpi-config` settings to set up a custom script with autologin. While this was quick and easy, I much preferred being asked to log in on boot and the ability to "logout" whenever I wanted to step away from my machine. To handle this, I updated my user `~/.profile` and created a shell script called `~/start_deck.sh`.
> You will also notice a file named `~/display_transform.sh` within the start deck script. This is optional. I have a monitor that is rotated vertically and so I needed to add a script to handle this transformation.

- `~/display_transform.sh` will handle the rotation of alacritty for setups that have a vertical monitor
- `~/start_deck.sh` will handle loading `cage`, display rotation via `~/display_transform.sh`, as well as providing a "kill switch" mechanism for logging out
- `~/.profile` will handle the running of `~/start_deck.sh` upon logging in to the physical device (not SSH)

**OPTIONAL**: Create a sell script in your home folder to rotate the screen and launch Alacritty (this is called by Cage). My file is called `display_transform.sh`:

```bash
nvim ~/display_transform.sh
```

The DietPi uses `HDMI-A-1` as the default port and I need a rotation of `90` degrees:

```bash
#!/bin/bash

# rotate the screen (targeting default Pi HDMI port)
wlr-randr --output HDMI-A-1 --transform 90

# launch alacritty
exec alacritty
```
Create a shell script in your home folder to automatically load up Alacritty after log-in.
```bash
#!/bin/bash
# prevent screen blanking
setterm -blank 0 -powerdown 0

# set wayland env var
export MOZ_ENABLE_WAYLAND=1

# infinite loop with a 'kill_switch' mechanism
while [ ! -f /tmp/kill_switch ]; do
        cage -s -- /home/paul/display_transform.sh
        sleep 1
done

# clean up the 'kill_switch' file
rm -f /tmp/kill_switch
```

The `/tmp/kill_switch` is a security measure to ensure I don't accidentally hit the `exit` command for Alacritty without meaning to. This ensures that the Alacritty loop will remain until I create a temporary file named `kill_switch`:

```bash
touch /tmp/kill_switch
```

Once that temporary file has been created, the system will then accept the `exit` commandL

```bash
exit
```

At this point, Alacritty will close and the system will automatically logout.


Modify your user profile to automatically trigger the deck setup when logging into the main physical screen (TTY1). For me, this was located at `~/.profile` but it could be listed as `~/.bash_profile`:

```bash
nvim ~/.profile
```

Append the following to the end of that file:

```bash
# deck auto-launch on TTY1 but not SSH
if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    ~/start_deck.sh
    
    # logout immediately when Alacritty is closed (via 'exit')
    logout
fi
```



Make `start_deck.sh` executable:

```bash
chmod +x ~/start_deck.sh
```

Make `display_transform.sh` executable:

```bash
chmod +x ~/display_transform.sh
```