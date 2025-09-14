<h1 align="center">
Troubleshooting
</h1>

<p align="center">
<b>This part of the wiki should hopefully help you when something isn't working right.</b>
</p>

---

| Issue | Possible solution |
|     :---:      |     :---:     |
| `'pip' is not recognized as an internal or external command` | [https://stackoverflow.com/a/56678271/19195633](https://stackoverflow.com/a/56678271/19195633)    |
| `The script is installed in directory, which is not PATH` | [https://superuser.com/questions/1372793/the-script-is-installed-in-directory-which-is-not-path](https://superuser.com/questions/1372793/the-script-is-installed-in-directory-which-is-not-path)

## Error when running the program in the temp directory
Extract the files from the .zip file which you downloaded. This program cannot run from a .zip file

## My config file isn't working!
If you're trying to upgrade your program while using an old config file, first `cd` to the root directory of this folder, i.e you should be in Discord-OTP-Forcer. Then, run:

```
python3 tools/convert-config.py
```

This should create two files `account.yml` and `program.yml` in a folder called `config`.

## The browser is frozen/not moving past the password reset screen. Pressing the password reset button does nothing, when the program is in `reset` programMode.
Re-do the password reset steps. https://github.com/Derpitron/Discord-OTP-Forcer/wiki/How-to-setup-and-use#how-to-get-your-token

## I'm using my system/browser in a language other than English (USA), and the program isn't working for me
To fix this, change your system/browser language to English (US).

### Linux
One user says this worked, when he was using Chromium in GNU/Linux:
> I solved it executing my desktop env in LANG=en_US.UTF-8, maybe this can be fixed opening chromium with english LANG in env (tried that with chromium.desktop, but when it opens the chromium window, it opens with the default LANG and not the chromium.desktop I choose)
I.e, open Chrome/Chromium after setting the environment variable LANG/LOCALE to English. (how to do this depends on your os and browser individually, I don't know how it works)

Basically, this program works by detecting strings on the pages only in the English (US) version of the Discord website. Thus if your system or browser uses another language such as Spanish, French, German, etc the program won't detect it and hence won't be able to work.