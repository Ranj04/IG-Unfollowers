# IG-Unfollowers

Find out who **doesn’t follow you back**, who your **fans** are (follow you, you don’t follow back), and your **mutuals** — using Instagram’s official data export. No login, no API, no scraping.

---



```bash
python3 foll.py -i following.html -e followers.html --print all --sort
What this does
Parses your Following and Followers export files (HTML or JSON).

# Computes:

Unfollowers — you follow them, they don’t follow you

Fans — they follow you, you don’t follow back

Mutuals — you follow each other

Prints a summary and (optionally) writes CSV/JSON results.

It does not log in, call private APIs, or automate Instagram. It only reads the files you downloaded from Instagram.

# Get your Instagram files
On the Instagram website (desktop is easiest):

Profile menu → More → Your activity → Download your information

You’ll be taken to Accounts Center → Download or transfer information

Select your account → Some of your information

Choose Followers & Following → Download to device

Pick a date range (e.g., All time) and submit

Instagram will email you a ZIP. Unzip it, then locate the Followers and Following files (often HTML; sometimes JSON).
Place them next to foll.py and name them exactly:

following.html (people you follow)

followers.html (people who follow you)

JSON is also supported—use following.json / followers.json if that’s what you receive.

# Requirements:
Python 3.9+ (works on macOS, Linux, Windows with WSL/PowerShell)

No external dependencies required

Optional: if you have bs4 (BeautifulSoup) installed, HTML parsing gets even more robust

# Usage
css
Copy code
python3 foll.py -i following.html -e followers.html \
  [--csv results.csv] \
  [--json results.json] \
  [--print all|unfollowers|fans|mutuals|summary] \
  [--sort] \
  [--ignore ignore.txt]
Flags
-i, --following — path to following export (people you follow), HTML or JSON

-e, --followers — path to followers export (people who follow you), HTML or JSON

--csv — write a CSV with two columns: category,username

--json — write a JSON with keys: unfollowers, fans, mutuals, and counts

--print — control what prints to stdout (summary default)

--sort — sort printed usernames alphabetically

--ignore — newline-delimited file of usernames to exclude (brands/celebs, etc.)

# Examples: 
bash
Copy code
# Basic summary
python3 foll.py -i following.html -e followers.html

# Full lists, sorted, with an ignore file
python3 foll.py -i following.html -e followers.html --print all --sort --ignore ignore.txt

# Save to CSV + JSON as well
python3 foll.py -i following.html -e followers.html --csv results.csv --json results.json --print all --sort
Ignore list format
Create a simple text file (e.g., ignore.txt) with one username per line.
@ and case don’t matter; everything is normalized.

css
Copy code
@brand_account
Famous.Person
some_celeb
Run with:

bash
Copy code
python3 foll.py -i following.html -e followers.html --ignore ignore.txt
Output (sample)
rust
Copy code
Summary:
  Following : 123
  Followers : 110
  Mutuals   : 95
  Unfollowers (not following back): 28
  Fans (you don't follow back)   : 15

Unfollowers — you follow them, they don't follow back (28):
  https://instagram.com/alice
  https://instagram.com/example_user
  ...

Fans — they follow you, you don't follow back (15):
  https://instagram.com/cara
  ...

Mutuals — you follow each other (95):
  https://instagram.com/bob
  ...

# Troubleshooting:
“Extracted 0 usernames”:
Make sure you’re pointing to the correct files (followers.html and following.html) from the official export. If you received JSON, pass the JSON files instead. Still stuck? Share a tiny (redacted) snippet and we can adjust the parser.

Windows:

You can use py instead of python3, e.g. py foll.py -i following.html -e followers.html.

If using PowerShell, ensure your current directory is where foll.py lives.

Keeping data private:
Don’t commit your export files. Add a .gitignore:

markdown
Copy code
followers.*
following.*
*.zip
*export*
__pycache__/
How it works (brief)
Extracts usernames from profile links (and text) in HTML or JSON exports.

Normalizes to lowercase and strips @//.

Ignores non-profile paths like /p/, /reel/, /stories/, /explore/, etc.

Computes set diffs to find unfollowers, fans, and mutuals.

Optional: Self-test
If you enabled the optional --selftest during hardening, you can run:

bash
Copy code
python3 foll.py --selftest
It will generate tiny sample inputs and verify the parser logic. Prints SELFTEST OK on success.

Contributing
PRs and issues welcome! If Instagram changes their export format, open an issue with a minimal (redacted) snippet so we can update the parser quickly.

