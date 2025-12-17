# Holloway v0.1 – DietPi writerDeck (Cage + Alacritty)
Holloway is a writerDeck designed for total focus. This first iteration was built with a lot of hardware that I had on hand as a proof of concept. This is a summary of that journey and this code base. I was "bad" and didn't document this as I was doing it, so I am doing my best here to remember all the nuance and roadblocks I hit along the way.

> [!WARNING]
> This document is a work in progress and will be updated as I can get to it. The latest update was made on `2025-12-05 10:00 CDT`.

## Requirements
### Hardware
- Computer: Raspberry Pi 4 Model B (aarch64)
- Monitor: Acer KB272 EBI 27" IPS Full HD (1920 x 1080)
- Keyboard: Keychron K3 Version 2, 75% Layout 84 Keys Ultra-Slim

> [!TIP]
> A 27" monitor is too big for a writerDeck, but it's what I had available. I would recommend something significantly smaller, like 10.1".

### System
- DietPi v9.19.2
- `cage` Wayland kiosk compositor
- `wlr-randr`: screen rotation utility (for vertical monitor support)
- `alacritty`: terminal emulator for a more modern _feel_
- `neovim`: text editor of choice

> [!NOTE]
> DietPi is what I happened to be using, and you may be able to do all of this with minimal changes using the Raspberry Pi OS, but please note that this document will not cover that.

## Installation
### DietPi
[How to install DietPi](https://dietpi.com/docs/install/)

### Core packages
Update package repositories and install `cage`, `alacritty`, and `wlr-randr` (optional):
```bash
sudo apt update
sudo apt install cage alacritty neovim
```

If you haven't already, create a dedicated non-root user for the writing environment, and add this user to the necessary groups:
```bash
adduser your_username
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
> Since I am using DietPi, I am creating a YAML configuration file for Alacritty instead of a TOML file (which I believe is what is "preferred" these days).

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
> There is a simple option within the  `dietpi-config` settings to set up a custom script with autologin. While this was quick and easy, I much prefer manual login and the ability to "logout" whenever I want.

- `~/start_deck.sh` will load `cage` with `alacritty`, run `~/display_transform.sh` if it exists, and provide a "kill switch" mechanism for logging out
- `~/display_transform.sh` will handle the rotation of the alacritty UI for setups that have a vertical monitor
- `~/.profile` will handle the running of `~/start_deck.sh` upon logging in to the physical device (not SSH)

1. Start deck script

Create a shell script in your home folder to automatically load up Alacritty after log-in.
```bash
#!/bin/bash
# prevent screen blanking
setterm -blank 0 -powerdown 0

# set wayland env var
export MOZ_ENABLE_WAYLAND=1

# infinite loop with a 'kill_switch' mechanism
while [ ! -f /tmp/kill_switch ]; do
    # run display transform if script exists
    if [ -x ~/display_transform.sh ]; then
        ~/display_transform.sh
    fi

    # launch cage with alacritty
    cage -s -- alacritty
    sleep 1
done

# clean up the 'kill_switch' file
rm -f /tmp/kill_switch
```

2. Update user profile

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
3. Display transform (optional)
Create a sell script in your home folder to rotate the alacritty UI. Feel free to name this whatever you like, but make sure the `~/start_deck.sh` references that same filename:

```bash
nvim ~/display_transform.sh
```

The DietPi uses `HDMI-A-1` as the default port and I need a rotation of `90` degrees:

```bash
#!/bin/bash

# rotate the screen (targeting default Pi HDMI port)
wlr-randr --output HDMI-A-1 --transform 90
```
4. Make scripts executable:

```bash
chmod +x ~/start_deck.sh
# optional: only if you created this file
chmod +x ~/display_transform.sh
```

## Reboot and test

Now comes the fun part! Once this is complete, you will want to reboot your machine:

```bash
sudo reboot
```
If all went well, you should see your DietPi login prompt as before, but when you login `alacritty` should launch as a fullscreen "application." To logout, simply create the "kill switch" temporary file and then enter the exit command:

```bash
touch /tmp/kill_switch
```
The `/tmp/kill_switch` is a security measure to ensure I don't accidentally hit the `exit` command for Alacritty without meaning to. This ensures that the Alacritty loop will remain until this file is created. Once that temporary file has been created, the system will then accept the `exit` commandL

```bash
exit
```

At this point, Alacritty will close and the system will automatically logout.