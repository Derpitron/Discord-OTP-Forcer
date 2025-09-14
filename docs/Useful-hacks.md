# Change the ratelimit/delay duration
Modify `src/backend.py` at the following lines:
[L225](https://github.com/Derpitron/Discord-OTP-Forcer/blob/1885d829b739e2c9a0b2a3a7debb4483059deef6/src/backend.py#L225) [L252](https://github.com/Derpitron/Discord-OTP-Forcer/blob/1885d829b739e2c9a0b2a3a7debb4483059deef6/src/backend.py#L252)

Change the values in the `secrets.choice(range(x, y))` calls to modify the range. E.g if it says `secrets.choice(range(2, 6))`, then the program will sleep for anywhere from 2 to 5 seconds (doesn't include the last value in the range). Read the `range()` docs here https://docs.python.org/3/library/stdtypes.html#range if you want to make custom ranges with weird timings

# Use the program in headless mode (console/terminal-only mode)
Edit `src/backend.py` at the lines L40, 41, to uncomment the two `add_argument()` lines below. "headless" means "make the program run only on terminal, without any other GUI/window popup".
```
# If you want to run the program without the browser opening then remove the # from the options below 
#options.add_argument('--headless')
#options.add_argument('--log-level=1')
```

No GUI will show up, no annoying browser window. Usable in Linux TTY/any environment without an X server

! You probably don't want to do this. If you do this, and the program manages to actually log in, then you won't have a valid browser window with which to navigate the logged in Discord.com and reset your password, meaning you'll have to re-do the entire process again just to get access, and you may have wasted a valid backup code (if you're in codeMode='backup')

Errors may show up and be invisible because you're not able to see the browser window to notice what went wrong. I tried to implement logs in the program to detect these but they don't work reliably. In any case, use this mode only if you're sure your configuration and tokens are working and up to date. AFAIK nothing will go horribly wrong even if you get an error, it'll just get stuck and you may not know why.

If you do wanna use this but have a window-view anyway whenever you want (but not by default), Look into enabling remote-debugging in the script and then checking it from your own browser using this method: https://stackoverflow.com/a/58045991