# IG-Unfollowers

Short one-liner about the project.

## Table of Contents
- [Overview](#overview)
- [Getting Your Instagram Files](#getting-your-instagram-files)
- [Requirements](#requirements)
- [Usage](#usage)
- [Examples](#examples)
- [Ignore List](#ignore-list)
- [Output](#output)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---
## TLDR: 
How It Works (Brief)

Extracts usernames from profile links and text in HTML or JSON.

Normalizes to lowercase; strips @ and trailing /.

Accepts usernames matching ^[a-zA-Z0-9._]{1,30}$.

Ignores non-profile paths like /p/, /reel/, /stories/, /explore/, etc.

Computes set diffs:

unfollowers = following − followers

fans = followers − following

mutuals = followers ∩ following


## Overview
What the tool does and what it does **not** do.

## Getting Your Instagram Files
Step-by-step to download Followers & Following export.
Profile menu → More → Your activity → Download your information

You’ll be taken to Accounts Center → Download or transfer information

Select your account → Some of your information

Choose Followers & Following → Download to device

Pick a date range (e.g., All time) and submit

When your ZIP arrives, unzip it and locate the Followers and Following files (often HTML; sometimes JSON). Put them next to foll.py and name them:

following.html or following.json (people you follow)

followers.html or followers.json (people who follow you)

Tip: If you’re unsure which is which, open the file in a browser and skim the headings — Instagram labels them clearly.

## Requirements
- Python 3.9+
- (Optional) `bs4` for stronger HTML parsing

## Usage
```bash
python3 foll.py -i following.html -e followers.html \
  [--csv results.csv] [--json results.json] \
  [--print all|unfollowers|fans|mutuals|summary] [--sort] [--ignore ignore.txt]
```

## Flags

-i, --following …

-e, --followers …

--csv, --json, --print, --sort, --ignore

## Examples
python3 foll.py -i following.html -e followers.html
python3 foll.py -i following.html -e followers.html --print all --sort --ignore ignore.txt

## Note: # Use py on Windows if python3 isn't found
py foll.py -i following.html -e followers.html


Ignore List

One username per line (case/@ ignored).
Create a simple text file (e.g., ignore.txt) with one username per line.
@ and case don’t matter — everything is normalized.

@brand_account
Famous.Person
some_celeb

Run with:

python3 foll.py -i following.html -e followers.html --ignore ignore.txt

## Output

Show a small sample of the “Summary” and lists.
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

## Troubleshooting

Common issues and fixes:

“Extracted 0 usernames”

Verify you’re using the export files, not a web page you saved manually.

If you received JSON, use the JSON files.

Try --print all to see more.

Still stuck? Share a minimal, redacted snippet in an issue.


## Windows: python3 not found

Use py instead: py foll.py -i following.html -e followers.html.

Encoding errors

Files are opened as UTF-8 with error-ignore; this usually avoids crashes. If you hit issues, report the filename and a tiny snippet.


## FAQ

Q: Why not just use the Instagram API?
A: The official API requires app approval and user auth for this data, and often doesn’t cover follower lists at the needed scope. This tool works from your official export, fully offline.

Q: Will this ban my account?
A: No. It doesn’t log in or automate anything. It only reads files you download from Instagram.

Q: My export is JSON. Is that okay?
A: Yes. Pass the JSON files to -i and -e. The tool auto-detects formats.

Q: Some accounts are missing or look wrong.
A: Make sure you pointed to the correct files. If Instagram changed the export layout, open an issue with a tiny (redacted) snippet and we’ll update the parser.

Q: Can I check only unfollowers?
A: Use --print unfollowers. For everything, use --print all.

## Contributing

PRs welcome. If IG changes export format, open an issue with a tiny redacted snippet.
