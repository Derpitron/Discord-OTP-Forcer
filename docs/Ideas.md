There's a few techniques and  which I'm not sure if they're useful or safe. I don't find them very ethical either, so I will likely not implement these ideas

Testing these would be dangerous to you/Discord's infra, and counterproductive to you; obviously you don't want to lock out of your account permanently, or get your hardware/IP address banned in the course of investigation/testing. You're trying to save your Discord account, not have Discord declare it a hacker-associated superfund site and honeypot/ban/delete it.

and you SHOULD not try them unless you know what you're doing and stay respectful to Discord's ToS/don't accidentally/wantonly DDoS their infrastructure.

I cannot confirm or deny any claims I make here.
Don't be evil.

# Multiple Instances at once on the same computer
I don't know how Selenium/WebDriver handles browser instances as processes. It may or may not work, or may crash one/all the program instances.
Running multiple instances from the same IP address is obviously spamming. Discord will send a ratelimit triggered on one HTTP client to all other clients on the same IP address.

# Running from multiple IP Addresses OR computers at once
I wouldn't be surprised Discord has protections in place to automatically block/disable/lock accounts that recieve multiple concurrent login requests from multiple Sources i.e different computers, clients OR ip addresses.
This could probably be either a celebrity/high profile account protections program from doxxing, impersonation, spamming, phishing,
or anti DDoS protections (duh)