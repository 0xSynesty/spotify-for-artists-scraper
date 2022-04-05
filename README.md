# Spotify For Artists Scraper

## ! This code is obsolete and needs to be re-adapted !

This bot uses a single Spotify For Artists account withs login, password and artist ID located in <code>logs.txt</code> and scrapes other artists daily statistics by running continuously.

Spotify statistics are updated once a day at a relatively random time so the bot constantly checks if they were updated.

Once it finishes getting daily streaming statistics for all Artists specified in <code>artists.txt</code>, it sends them to the discord server which hook is specified in <code>discord_hook.txt</code>.


***You will need the chromedriver.exe corresponding to your version of Google Chrome in order to make the bot work, the driver is available here : https://chromedriver.chromium.org/downloads***
