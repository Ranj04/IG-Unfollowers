#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

# Python 3.8 compatibility
try:
    from typing import List, Set, Dict, Any, Union, Optional
    # Use modern type hints for Python 3.9+
    if sys.version_info >= (3, 9):
        List = list
        Set = set
        Dict = dict
        Any = any
        Union = Union
        Optional = Optional
except ImportError:
    pass

# Optional BeautifulSoup import for better HTML parsing
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

# Paths like these are NOT usernames
RESERVED_FIRST_SEGMENTS = {
    "p", "reel", "reels", "stories", "explore", "accounts", "directory",
    "about", "privacy", "terms", "api", "graphql", "web", "emails",
    "oauth", "sessions", "challenge", "tv"
}

USERNAME_RE = re.compile(r"^[a-z0-9._]{1,30}$", re.I)
URL_IN_HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.I)
ANY_IG_URL_RE = re.compile(r'https?://(?:www\.)?instagram\.com/[^ \t\r\n"\'<>]+', re.I)

def _parse_username_from_url(url: str) -> str:
    """
    Extract the first path segment after instagram.com/ if it looks like a username,
    or return the string if it's already a valid username.
    """
    url = url.strip().strip('\'"')
    
    # If it's an Instagram URL, extract the username
    m = re.search(r'https?://(?:www\.)?instagram\.com/([^/?#]+)', url, re.I)
    if m:
        first = m.group(1).strip("/").lower().lstrip("@")
        if not first or first in RESERVED_FIRST_SEGMENTS:
            return ""
        if not USERNAME_RE.match(first):
            return ""
        return first
    
    # If it's not a URL, check if it's a valid username directly
    username = url.lower().lstrip("@")
    if USERNAME_RE.match(username):
        return username
    
    return ""

def _walk_json(obj, acc):
    """
    Walk arbitrary JSON and collect string values; some IG exports put
    useful data under fields like 'value', 'title', 'href', 'username'.
    """
    if obj is None:
        return
    if isinstance(obj, dict):
        for v in obj.values():
            _walk_json(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            _walk_json(v, acc)
    elif isinstance(obj, str):
        acc.append(obj)

def extract_usernames(path: str) -> Set[str]:
    """Extract usernames from HTML or JSON file."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"No such file: {path}")

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        blob = f.read()

    candidates = []

    # If JSON, parse it and harvest all string fields (we'll pick out IG URLs later)
    sniff = blob.lstrip()
    if sniff.startswith("{") or sniff.startswith("["):
        try:
            data = json.loads(blob)
            _walk_json(data, candidates)
        except Exception:
            # Not valid JSON, fall back to HTML scanning
            pass

    # Always scan for hrefs and raw IG URLs too (works for HTML)
    candidates += URL_IN_HREF_RE.findall(blob)
    candidates += ANY_IG_URL_RE.findall(blob)

    usernames: Set[str] = set()
    for item in candidates:
        u = _parse_username_from_url(item)
        if u:
            usernames.add(u)

    if not usernames:
        print(f"⚠️  Extracted 0 usernames from {path}. "
              "If your export format looks different, share a small snippet.",
              file=sys.stderr)
    return usernames

def load_ignore_list(path: Optional[str]) -> Set[str]:
    """Load usernames to ignore from file."""
    if not path:
        return set()
    if not os.path.isfile(path):
        print(f"Ignore file not found: {path}", file=sys.stderr)
        return set()
    out: Set[str] = set()
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            u = line.strip().lstrip("@").lower()
            if USERNAME_RE.match(u):
                out.add(u)
    return out

def write_csv(path: str, results: Dict[str, Any]) -> None:
    """Write results to CSV file."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write("category,username\n")
            
            for username in results['unfollowers']:
                f.write(f"unfollowers,{username}\n")
            
            for username in results['fans']:
                f.write(f"fans,{username}\n")
            
            for username in results['mutuals']:
                f.write(f"mutuals,{username}\n")
                
    except Exception as e:
        print(f"Error writing CSV file '{path}': {e}", file=sys.stderr)
        sys.exit(1)

def write_json(path: str, results: Dict[str, Any]) -> None:
    """Write results to JSON file."""
    try:
        output_data = {
            'unfollowers': results['unfollowers'],
            'fans': results['fans'],
            'mutuals': results['mutuals'],
            'counts': results['counts']
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)
            
    except Exception as e:
        print(f"Error writing JSON file '{path}': {e}", file=sys.stderr)
        sys.exit(1)

def run_selftest() -> int:
    """Run self-test with temporary files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample HTML files
        following_html = temp_path / "following.html"
        following_html.write_text('''<!DOCTYPE html>
<html>
<body>
<a href="https://www.instagram.com/alice/">Alice</a>
<a href="https://www.instagram.com/bob">Bob</a>
<a href="https://www.instagram.com/p/XYZ/">Post</a>
<a href="https://www.instagram.com/reel/ABC/">Reel</a>
</body>
</html>''', encoding='utf-8')
        
        followers_html = temp_path / "followers.html"
        followers_html.write_text('''<!DOCTYPE html>
<html>
<body>
<a href="https://www.instagram.com/bob/">Bob</a>
<a href="https://www.instagram.com/cara">Cara</a>
</body>
</html>''', encoding='utf-8')
        
        # Test HTML parsing
        following_html_set = extract_usernames(str(following_html))
        followers_html_set = extract_usernames(str(followers_html))
        
        # Expected results for HTML
        expected_following_html = {"alice", "bob"}
        expected_followers_html = {"bob", "cara"}
        
        # Verify HTML parsing
        if following_html_set != expected_following_html:
            print(f"SELFTEST FAILED: HTML following mismatch")
            print(f"Expected: {expected_following_html}")
            print(f"Got: {following_html_set}")
            return 1
            
        if followers_html_set != expected_followers_html:
            print(f"SELFTEST FAILED: HTML followers mismatch")
            print(f"Expected: {expected_followers_html}")
            print(f"Got: {followers_html_set}")
            return 1
        
        # Create sample JSON files
        following_json = temp_path / "following.json"
        following_json.write_text('''[
  {"string_list_data": [{"value":"alice","href":"https://www.instagram.com/alice/"}]},
  {"title":"bob"}, 
  {"href":"https://www.instagram.com/p/XYZ/"},
  {"username":"dave"}
]''', encoding='utf-8')
        
        followers_json = temp_path / "followers.json"
        followers_json.write_text('''[
  {"string_list_data": [{"value":"bob","href":"https://www.instagram.com/bob/"}]},
  {"title":"cara"},
  {"href":"https://www.instagram.com/reel/ABC/"},
  {"username":"eve"}
]''', encoding='utf-8')
        
        # Test JSON parsing
        following_json_set = extract_usernames(str(following_json))
        followers_json_set = extract_usernames(str(followers_json))
        
        # Expected results for JSON
        expected_following_json = {"alice", "bob", "dave"}
        expected_followers_json = {"bob", "cara", "eve"}
        
        # Verify JSON parsing
        if following_json_set != expected_following_json:
            print(f"SELFTEST FAILED: JSON following mismatch")
            print(f"Expected: {expected_following_json}")
            print(f"Got: {following_json_set}")
            return 1
            
        if followers_json_set != expected_followers_json:
            print(f"SELFTEST FAILED: JSON followers mismatch")
            print(f"Expected: {expected_followers_json}")
            print(f"Got: {followers_json_set}")
            return 1
        
        # Test diff computation with HTML data
        not_following_back = following_html_set - followers_html_set
        fans = followers_html_set - following_html_set
        mutuals = following_html_set & followers_html_set
        
        expected_unfollowers = {"alice"}
        expected_fans = {"cara"}
        expected_mutuals = {"bob"}
        
        if not_following_back != expected_unfollowers:
            print(f"SELFTEST FAILED: Unfollowers mismatch")
            print(f"Expected: {expected_unfollowers}")
            print(f"Got: {not_following_back}")
            return 1
            
        if fans != expected_fans:
            print(f"SELFTEST FAILED: Fans mismatch")
            print(f"Expected: {expected_fans}")
            print(f"Got: {fans}")
            return 1
            
        if mutuals != expected_mutuals:
            print(f"SELFTEST FAILED: Mutuals mismatch")
            print(f"Expected: {expected_mutuals}")
            print(f"Got: {mutuals}")
            return 1
        
        print("SELFTEST OK")
        return 0

def main(argv: List[str]) -> int:
    """Main function with CLI argument parsing."""
    ap = argparse.ArgumentParser(description="Find accounts not following you back from IG exports")
    ap.add_argument("-i", "--following", help="Path to following export (people YOU follow) — HTML or JSON")
    ap.add_argument("-e", "--followers", help="Path to followers export (people who FOLLOW you) — HTML or JSON")
    ap.add_argument("--csv", help="Optional CSV output with columns category,username")
    ap.add_argument("--json", help="Optional JSON output with keys: unfollowers, fans, mutuals, and counts")
    ap.add_argument("--print", choices=['all', 'unfollowers', 'fans', 'mutuals', 'summary'], 
                   default='summary', help="Control stdout view; default summary")
    ap.add_argument("--ignore", help="Path to newline-delimited usernames to exclude (brands/celebs, etc.)")
    ap.add_argument("--sort", action="store_true", help="Sort output alphabetically")
    ap.add_argument("--selftest", action="store_true", help="Run self-test and exit")
    
    args = ap.parse_args(argv)
    
    # Handle selftest
    if args.selftest:
        return run_selftest()

    # Check required arguments for normal operation
    if not args.following or not args.followers:
        ap.error("the following arguments are required: -i/--following, -e/--followers")

    try:
        followers = extract_usernames(args.followers)
        following = extract_usernames(args.following)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2

    ignore = load_ignore_list(args.ignore)
    if ignore:
        followers -= ignore
        following -= ignore

    not_following_back = following - followers
    fans = followers - following
    mutuals = followers & following

    # Prepare results dictionary
    results = {
        'unfollowers': list(not_following_back),
        'fans': list(fans),
        'mutuals': list(mutuals),
        'counts': {
            'following': len(following),
            'followers': len(followers),
            'mutuals': len(mutuals),
            'unfollowers': len(not_following_back),
            'fans': len(fans)
        }
    }

    # Write output files
    if args.csv:
        write_csv(args.csv, results)
    
    if args.json:
        write_json(args.json, results)

    # Print summary
    if args.print in ['summary', 'all']:
        print("\nSummary:")
        print(f"  Following : {results['counts']['following']}")
        print(f"  Followers : {results['counts']['followers']}")
        print(f"  Mutuals   : {results['counts']['mutuals']}")
        print(f"  Unfollowers (not following back): {results['counts']['unfollowers']}")
        print(f"  Fans (you don't follow back)   : {results['counts']['fans']}")
        print()

    def print_block(title: str, items: List[str]):
        lst = sorted(items) if args.sort else items
        print(f"\n{title} ({len(lst)}):")
        for u in lst:
            print(f"https://instagram.com/{u}")

    # Print detailed lists based on --print mode
    if args.print in ['all', 'unfollowers']:
        print_block("Unfollowers — you follow them, they don't follow back", results['unfollowers'])
    
    if args.print in ['all', 'fans']:
        print_block("Fans — they follow you, you don't follow back", results['fans'])
    
    if args.print in ['all', 'mutuals']:
        print_block("Mutuals — you follow each other", results['mutuals'])

    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))