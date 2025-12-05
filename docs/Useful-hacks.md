# Change the ratelimit/delay duration
Modify the `config/program.yml` file, and find the `AttemptDelay` variables. Change their values as you want, to adjust the delays of the program between codes.

# Use the program in headless mode (console/terminal-only mode)
Modify the `config.program.yml` file and set `headless` to `True`.

No GUI will show up, no annoying browser window. Usable in Linux TTY/any environment without an X server

! You probably don't want to do this. If you do this, and the program manages to actually log in, then you won't have a valid browser window with which to navigate the logged in Discord.com and reset your password, meaning you'll have to re-do the entire process again just to get access, and you may have wasted a valid backup code (if you're in codeMode='backup')

Errors may show up and be invisible because you're not able to see the browser window to notice what went wrong. I tried to implement logs in the program to detect these but they don't work reliably. In any case, use this mode only if you're sure your configuration and tokens are working and up to date. AFAIK nothing will go horribly wrong even if you get an error, it'll just get stuck and you may not know why.

If you do wanna use this but have a window-view anyway whenever you want (but not by default), Look into enabling remote-debugging in the script and then checking it from your own browser using this method: https://stackoverflow.com/a/58045991