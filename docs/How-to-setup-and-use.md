### Requirements
- Python (https://www.python.org/downloads)
- Google Chrome (https://www.google.com/chrome) or Chromium (get it from chromium.org or your package manager)
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
3. The requisite dependencies with install then the `user/cfg.yml` file will open, fill out the necessary credentials then save and close notepad. 
4. Run `scripts/Windows/start.bat`, Follow the instructions in the command prompt. 
5. An automated Google Chrome window will open. When the hCaptcha appears, complete it as normal.
6. Wait for either a successful login, or a closed browser window (Failure to brute force codes)
---
### Mac OS, Linux, other Non Windows based OS
1. Clone/download the repository, and `cd` to it
```
git clone https://github.com/Derpitron/Discord-OTP-Forcer.git
```
```
cd Discord-OTP-Forcer
```
2. Install the requisite dependencies.
```
pip install -r requirements.txt
```
3. Fill in the files in the `config` folder as shown below:
4. Fill out the necessary credentials in the `config/account.yml` file.
5. Fill out the necessary program configuration options in `config/program.yml` file.
6. Run the `main.py` file.
```
python main.py
```
7. An automated Google Chrome window will open. When the hCaptcha appears, complete it as normal.
8. Wait for either a successful login, or a closed browser window (Failure to brute force codes)
---
### Filling out the program.yml file
The program has two modes `reset` and `login` we'll need to set `programMode` to one of these.
 * `programMode:"reset"` Will set the program to password reset mode.
 * `programMode:"login"` Will set the program to login mode.

After you've set the mode you'll need to chose what type of code you want the program to use, The program currently has 3 modes to choose from.
 * `codeMode:"normal"` Generates a 6-digit numeric 'normal' code.
 * `codeMode:"backup"` Generates an 8-digit alphanumeric 'backup' code.
 * `codeMode:"both"` Generates a code with a random possibility of being 'normal' or 'backup' type.
 
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

_**You only need the part after `https://discord.com/reset#token=` the program will not work if you put the entire URL.**_