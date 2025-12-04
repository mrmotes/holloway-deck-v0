# Holloway Deck
> [!IMPORTANT]
> **Vision**
> A portable, distraction-free "modern typewriter" built inside a rugged case. The machine functions as a single-purpose appliance for longform writing, offering a high-aesthetic CLI environment (Ghostty + Neovim) without the overhead of a desktop OS. "Infrastructure as Code" via NixOS. The entire machine state should be public and replicable, while personal data and secrets are decoupled.

Below is a list of hardware and software that I plan on using the build out the next version of my Holloway Deck. I will add my current architecture at a later point.

## Hardware architecture

| Component | Selection | Status | Specs & Notes |
| :--- | :--- | :--- | :--- |
| **Chassis** | **Pelican 1450** (or Apache 3800) | Decided | **Why:** Internal width (~14.6") fits keyboard perfectly. Deep lid allows vertical screen mounting. |
| **Compute Core** | **Beelink S12 Pro** | Decided | **Specs:** Intel N100, 16GB RAM. <br>**Mod:** Strip plastic shell. Mount motherboard directly to chassis plate. <br>**Power:** Standard 12V DC input. |
| **Display** | **10.1" DIY Kit (1920x1200)** | Decided | **Model:** B101UAN02.1 (Panel + HDMI Controller Board). <br>**Why:** High PPI for crisp text. Zero branding. 1200px width (vertical) allows comfortable split-pane editing. |
| **Input** | **Keychron K3 v2** | Owned | **Usage:** Stored inside case during transport. Removed to type. <br>**Size:** 306mm width fits inside Pelican 1450 (371mm width). |
| **Power Bank** | **Baseus Blade 100W** | Decided | **Specs:** 20,000mAh, PD 3.0. <br>**Form:** Flat "laptop" shape allows mounting behind screen/motherboard. |
| **Cabling** | **USB-C -> DC Trigger** | Decided | **Spec:** USB-C PD to 5.5x2.5mm Barrel Jack (12V). <br>**Function:** Tricks battery into providing clean 12V to the Beelink. |
| **Mounting** | **Custom 3D Print** | Pending | **Plan:** Design a "Deck Plate" to hold Mobo/Battery. Print via service (PCBWay/Craftcloud). |

## Software architecture

| Component | Selection | Status | Implementation Details |
| :--- | :--- | :--- | :--- |
| **OS** | **NixOS** | Designed | **Config:** `flake.nix` based. <br>**Benefit:** If machine dies, re-flashing restores exact state in 10 mins. |
| **UI Mode** | **Cage** (Wayland Kiosk) | Designed | **Behavior:** Boots directly to terminal. No Login Manager. No Desktop Environment. |
| **Terminal** | **Ghostty** | Designed | **Config:** GPU accelerated, Ligatures, Catppuccin Theme. <br>**Role:** Handles Tabs/Splits natively (replaces Window Manager). |
| **Editor** | **LazyVim** | Designed | **Plugins:** Telescope, Treesitter (Markdown), ZenMode. |
| **Connectivity** | **Tailscale** | Designed | **Role:** "Mothership" Link. Allows `git push` / `scp` to home PC from anywhere without opening ports. |
| **User Tools** | **Custom Python Suite** | In Dev | **Details:** Custom scripts (`write`, `scene-compile`) for project management and drafting. <br>**Env:** Ported to `nix-shell` for reproducibility. |