# Discord-OTP-Forcer
This is a Selenium based Discord TOTP forcer. 

# Why did I make this?
In December 2021, I lost access to my passwords and OTP list due to a file syncing issue. I was able to recover most of the credentials, except for my Discord Alt. When I contacted Discord Support, they informed me that due to their security policy, they could not disable 2FA for that account, which while it is understandable, is unfortunate. As a proof-of-concept program, I hacked together this crude script which simply brute forces randomly generated 6 digit numbers to the Discord login's TOTP field.

# Features
- Ratelimit avoidance (Cooldown between every code attempt)
- Color coded print logging
- Waits for you to complete the hCaptcha
- Automatically closes when the hCaptcha ticket expires, and prints useful info (e.g No. of attempted codes, time taken, no. of ratelimits)
- Blocks analytics URLs such as Cloudflare logging, Discord Science, and Sentry.io
- User friendly
- Allows to use environment variables for user-supplied e-mail and password.

# Known Issues
- Attempted code is displayed with a delay
- Depends on HTML element class names/english localized strings in order to detect failure/success

# Credits
- TheGamer456YT for their [frick-discord-2fa](https://github.com/TheGamer456YT/frick-discord-2fa) script, which gave me the base for the codegen.py and textcolor.py libraries. 

# Disclaimer
`THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.` 

Tldr; I am not responsible for anything you do with this script, and I do not condone (but cannot prevent) the usage of this script to hack into accounts which you do not properly own. Read the [License](https://github.com/hydino2085143/Discord-OTP-Forcer/blob/main/LICENSE) for full information on your rights and responsibilities which pertain to this program. 
