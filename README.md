# Discord-OTP-Forcer
This is a Selenium and Python based Discord TOTP forcer. It attempts to brute force randomly generated 6 or 8 digit codes with a random delay between each attempt.
![image](https://github.com/Derpitron/Discord-OTP-Forcer/assets/46134462/761e7da9-8a0e-4684-9bd3-46829efd7ae5)
*Look at him go!*

Instructions on how to setup and use this program can be found on the [wiki](https://github.com/Derpitron/Discord-OTP-Forcer/wiki/How-to-setup-and-use)

# Features
- Brute forces 6 digit TOTP codes (1 million possible codes)
- Brute forces 8 digit Backup codes (2.82 trillion possible codes)
- Ratelimit avoidance (Cooldown between every code attempt)
- Robust easy to read log formatting
- Can brute force Password Reset page's TOTP codes.
- Waits for you to complete the hCaptcha
- Automatically closes when the hCaptcha ticket or browser session expires, and prints useful info (e.g No. of attempted codes, time taken, no. of ratelimits)
- Blocks analytics URLs such as Cloudflare logging, Discord Science, and Sentry.io
- User friendly

# Dependencies
- Google Chrome
- Python >= 3.10

# Why did I make this?
In December 2021, I lost access to my passwords and OTP list due to a file syncing issue. I was able to recover most of the credentials, except for my Discord Alt. When I contacted Discord Support, they informed me that due to their security policy, they could not disable 2FA for that account, which while it is understandable, is unfortunate. As a proof-of-concept program, I hacked together this crude script which simply brute forces randomly generated 6 digit numbers to the Discord login's TOTP field.

# Known Issues
- Depends on HTML element class names in order to detect failure/success
- Script relies on the Chrome WebDriver, thus Google Chrome will have to be installed.
- Requires **Python Version >= 3.10** to work. 

# Credits
- [SpaghettDev](https://github.com/SpaghettDev) for their [frick-discord-2fa](https://github.com/SpaghettDev/frick-discord-2fa) script, which gave me the base for the codegen.py and textcolor.py libraries ❤️
- [LuXeZs](https://github.com/LuXeZs) for implementing 8-char Backup OTP code brute-forcing, Password Reset OTP forcing, various bug fixes, and maintaining this program for now ❤️

---
# Disclaimer
`THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION. ` 

Tldr; I am not responsible for anything you do with this script, and I do not condone (but cannot prevent) the usage of this script to hack into accounts which you do not properly own. The onus is on you to not be evil. Read the [License](https://github.com/Derpitron/Discord-OTP-Forcer/blob/main/LICENSE) for full information on your rights and responsibilities which pertain to this program. 
