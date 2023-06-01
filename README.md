# Discord-OTP-Forcer
This is a Selenium and Python based Discord TOTP forcer. It attempts to brute force randomly generated 6 or 8 digit codes with a random delay between each attempt.

# Features
- Brute forces 6 digit TOTP codes (1 million possible codes)
- Brute forces 8 digit Backup codes (2.82 trillion possible codes)
- Ratelimit avoidance (Cooldown between every code attempt)
- Color coded print logging
- Can brute force password reset's TOTP codes.
- Waits for you to complete the hCaptcha
- Automatically closes when the hCaptcha ticket expires, and prints useful info (e.g No. of attempted codes, time taken, no. of ratelimits)
- Blocks analytics URLs such as Cloudflare logging, Discord Science, and Sentry.io
- User friendly
- Allows to use environment variables for user-supplied e-mail and password.

# Requirements
- Python (https://www.python.org/downloads)
- Google Chrome (https://www.google.com/chrome)

# How to setup and use (Windows)
1. Clone/download the repository.
    - Download repository (https://github.com/Derpitron/Discord-OTP-Forcer/archive/refs/heads/main.zip)

    *Or,*
    
    - Clone with Git
    ```
      git clone https://github.com/Derpitron/Discord-OTP-Forcer.git
      ```
2. Go to the location you installed the repository and run `scripts/Windows/setup.bat`.
3. The requisite dependencies with install then the `user/cfg.yml` file will open, fill out the necessary credentials then save and close notepad. 
4. Run `scripts/Windows/start.bat`, Follow the instructions in the command prompt. 
5. An automated Google Chrome window will open. When the hCaptcha appears, complete it as normal.
6. Wait for either a successful login, or a closed browser window (Failure to brute force codes)

## Alternative setup (Mac OS, Linux, other Non Windows based OS)
1. Clone/download the repository, and `cd` to it
```
git clone https://github.com/hydino2085143/Discord-OTP-Forcer.git
```
```
cd Discord-OTP-Forcer
```
2. Install the requisite dependencies.
```
pip install -r requirements.txt
```
3. Fill out the necessary credentials in the `user/cfg.yml` file.
4. Run the `main.py` file.
```
python main.py
```
5. An automated Google Chrome window will open. When the hCaptcha appears, complete it as normal.
6. Wait for either a successful login, or a closed browser window (Failure to brute force codes)

# How to get your token
1. Enter email for the account and click forgot password.

![plot](./docs/assets/passreset-token-instructions/readme(1).png)

2. Find the password reset email and click reset password.

![plot](./docs/assets/passreset-token-instructions/readme(2).png)

3. Your token will be in the URL for the password reset page.

![plot](./docs/assets/passreset-token-instructions/readme(3).png)

# Why did I make this?
In December 2021, I lost access to my passwords and OTP list due to a file syncing issue. I was able to recover most of the credentials, except for my Discord Alt. When I contacted Discord Support, they informed me that due to their security policy, they could not disable 2FA for that account, which while it is understandable, is unfortunate. As a proof-of-concept program, I hacked together this crude script which simply brute forces randomly generated 6 digit numbers to the Discord login's TOTP field.

# Known Issues
- Depends on HTML element class names in order to detect failure/success
- Script relies on the Chrome WebDriver, thus Google Chrome will have to be installed.
- Requires **Python Version >= 3.10** to work. 

# Credits
- [SpaghettDev](https://github.com/SpaghettDev) for their [frick-discord-2fa](https://github.com/SpaghettDev/frick-discord-2fa) script, which gave me the base for the codegen.py and textcolor.py libraries ❤️
- [LuXeZs](https://github.com/LuXeZs) for implementing 8-char Backup OTP code brute-forcing, Password Reset OTP forcing, various bug fixes, and effectively maintaining this program for now ❤️

# Disclaimer
`THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION. ` 

Tldr; I am not responsible for anything you do with this script, and I do not condone (but cannot prevent) the usage of this script to hack into accounts which you do not properly own. The onus is on you to not be evil. Read the [License](https://github.com/Derpitron/Discord-OTP-Forcer/blob/main/LICENSE) for full information on your rights and responsibilities which pertain to this program. 
