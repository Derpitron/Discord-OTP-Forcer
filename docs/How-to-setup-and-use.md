### Requirements
- Python >= 3.13 (https://www.python.org/downloads)
- Google Chrome (https://www.google.com/chrome)
---
### Windows

1. Clone/download the repository.
    - Download repository (https://github.com/Derpitron/Discord-OTP-Forcer/archive/refs/heads/main.zip)

    *Or,*
    
    - Clone with Git
    ```
      git clone https://github.com/Derpitron/Discord-OTP-Forcer.git
      ```
2. Go to the location you installed the repository and run `scripts/Windows/setup.bat`.
3. The requisite dependencies with install then the `config/account.yml` and `config/program.yml` files will open, fill out the necessary credentials then save and close notepad. 
4. Run `scripts/Windows/start.bat`, Follow the instructions in the command prompt. 
5. An automated Google Chrome window will open. When the hCaptcha appears, complete it as normal.
6. Wait for either a successful login, or a closed browser window (Failure to brute force codes). Go to the "Running the program" section for the main instructions.
---
### Mac OS, Linux, other Non Windows based OS
1. Clone/download the repository, and `cd` to it
```
git clone https://github.com/Derpitron/Discord-OTP-Forcer.git
cd Discord-OTP-Forcer
python -m venv .venv
# Replace the below step with however you activate a virtualenv in your OS: https://docs.python.org/3/library/venv.html#creating-virtual-environments
source .venv/bin/activate
```
2. Install the requisite dependencies.
```
pip install -r requirements.txt
```
3. Fill in the files in the `config` folder as shown below:
4. Fill out the necessary credentials in the `config/account.yml` file.
5. Fill out the necessary program configuration options in `config/program.yml` file.

# Running the program
6. Run the `main.py` file.
```
python main.py
```
7. An automated Google Chrome window will open. When the hCaptcha appears, complete it as normal.
8. **Wait for either a successful login**, or a closed browser window (Failure to brute force codes)
9. If it succeeds, **The program will PRINT YOUR ACCOUNT TOKEN TO CONSOLE**. Be warned and don't run this where someone else could access the log. **It will also save it to a file in `secret/token.txt`**.
10. **Do not log out of discord.com on that browser window at all**. Even if the browser closes, that's fine. just **do NOT log out** under any circumstances or the token will be regenerated, making your currently obtained token invalid and the whole effort is lost.
11. **You can LOG IN to your account using that token** with this script: https://github.com/JHVIW/Discord-Token-Login-Script. Go to `discord.com/login`, open browser console, paste the script, fill in your account token where it says to, and wait for it to log-in.
12. As soon as it logs in, **go to User Settings > My Account > Authenticator App > View Backup Codes**. Click it and enter your password, or your newPassword if you were in Reset mode.
13. It may ask you for an email verification code. Check your account's registered mail for this and enter it.
14. **You'll see your account's backup codes. SAVE THEM.** SCREENSHOT THIS 15 TIMES AND SAVE 3 COPIES OF IT ON GOOGLE DRIVE, AND YOUR HARD DRIVE, YOUR PHONE, WRITTEN ON A PIECE OF PAPER, ETC.
15. After having saved one of these backup codes, **click Remove Authenticator App** above and enter one of the backup codes you just obtained above.
16. Now your account is liberated. Feel free to do whatever you want with it but remember to **save all details** you change.

---
### Filling out the program.yml file
The program has two modes `Reset` and `Login` we'll need to set `programMode` to one of these.
 * `programMode: Reset` Will set the program to password reset mode. It'll log in to your account using the password reset token `resetToken`, enter your desired `newPassword`, and then Force codes.
 * `programMode: Login` Will set the program to login mode. This is a normal email+password login which will then (usually) ask you for a Captcha, then start Forcing codes.

After you've set the program's mode you'll need to chose what type of code you want the program to use, The program currently has 3 modes to choose from.
 * `codeMode: Normal` Generates a 6-digit numeric 'normal' code.
 * `codeMode: Backup` Generates an 8-digit alphanumeric 'backup' code.
 * `codeMode: "aqzi[a-z0-9]{2}(p|q)[3-5]"` This is the special regex mode, that gets filled into Backup codes. This generates a backup code conforming to your given regex template. In this case, it would possibly generate ANY of the following codes: `aqzi03p4`, `aqzi8jq5`, and even more! You can fill in any template you want, provided it fits within the Discord backup code format, which is `[a-z0-9]{8}`. Just type in the parts of the code you do remember, and fill in what you don't remember with some regex you think it adheres to (for a single character. 
 
 https://regex101.com/ This is a good website to check and test out regex patterns. Make sure to use the Python regex mode

There are a few other options in the program.yml file that control the program's timing and logging settings. They have default values and you may want to change them for your needs.
### Filling out the account.yml file
Fill in your account's email ID, password in the `email` and `password` fields. Remember to put them in quotes.
If you plan on using the `Reset` mode you'll need to fill out the `newPassword` and `resetToken` fields

---
### How to get your token
1. Go to https://discord.com/login and enter the email for the account and click forgot password.

![plot](https://github.com/Derpitron/Discord-OTP-Forcer/blob/main/docs/assets/passreset-token-instructions/readme(1).png)

2. Find the password reset email and click reset password.

![plot](https://github.com/Derpitron/Discord-OTP-Forcer/blob/main/docs/assets/passreset-token-instructions/readme(2).png)

3. Your token will be in the URL for the password reset page.

![plot](https://github.com/Derpitron/Discord-OTP-Forcer/blob/main/docs/assets/passreset-token-instructions/readme(3).png)

_**You only need the part after `https://discord.com/reset#token=` the program will not work if you put the entire URL.**