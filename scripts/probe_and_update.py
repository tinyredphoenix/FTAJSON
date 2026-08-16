import json
import urllib.request
import re
import concurrent.futures
import os
import sys

UPSTREAM_FEEDS = [
    "https://iptv-org.github.io/iptv/countries/in.m3u",
    "https://iptv-org.github.io/iptv/languages/hin.m3u"
]

def check_stream(url, timeout=4):
    if not url:
        return False
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            if res.status == 200:
                chunk = res.read(500).decode('utf-8', errors='ignore')
                if '#EXTM3U' in chunk or '#EXT-X-STREAM-INF' in chunk:
                    return True
    except Exception:
        pass
    return False

def fetch_upstream_candidates():
    """Scrapes latest upstream IPTV databases to build candidate pool for auto-healing."""
    print("Fetching upstream IPTV feeds for auto-repair pool...")
    candidates = []
    for feed_url in UPSTREAM_FEEDS:
        try:
            req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8) as res:
                content = res.read().decode('utf-8', errors='ignore')
                lines = content.split('\n')
                curr_name = ""
                for line in lines:
                    line = line.strip()
                    if line.startswith('#EXTINF:'):
                        m = re.search(r',(.+)$', line)
                        curr_name = m.group(1).strip() if m else ""
                    elif line.startswith('http') and curr_name:
                        candidates.append({'name': curr_name, 'url': line})
                        curr_name = ""
        except Exception as e:
            print(f"Warning: Failed to fetch upstream feed {feed_url}: {e}")
    print(f"Loaded {len(candidates)} candidate streams from upstream databases.")
    return candidates

def clean_name(n):
    return re.sub(r'[^a-z0-9]', '', n.lower().replace('hd', '').replace('tv', '').replace('digital', ''))

def search_upstream_replacement(ch_name, candidates):
    """Searches upstream candidates for a working replacement stream."""
    target_clean = clean_name(ch_name)
    matched_urls = []
    for cand in candidates:
        cand_clean = clean_name(cand['name'])
        if target_clean in cand_clean or cand_clean in target_clean:
            matched_urls.append(cand['url'])

    for url in matched_urls:
        if check_stream(url, timeout=3):
            return url
    return None

def main():
    json_path = os.path.join(os.path.dirname(__file__), '..', 'fta_channels.json')
    m3u_path = os.path.join(os.path.dirname(__file__), '..', 'playlist.m3u')

    with open(json_path, 'r', encoding='utf-8') as f:
        channels = json.load(f)

    print(f"Probing {len(channels)} curated Indian FTA channels...")
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        future_map = {executor.submit(check_stream, ch['url']): ch for ch in channels}
        for f in concurrent.futures.as_completed(future_map):
            ch = future_map[f]
            results[ch['name']] = f.result()

    failed_channels = [ch for ch in channels if not results.get(ch['name'], False)]
    print(f"\nInitial Probe: {len(channels) - len(failed_channels)} / {len(channels)} active.")

    if failed_channels:
        print(f"\n⚡ Attempting Auto-Healing for {len(failed_channels)} unreachable channels via upstream scraper...")
        upstream_pool = fetch_upstream_candidates()
        healed_count = 0
        for ch in failed_channels:
            print(f"Searching replacement for: {ch['name']}...")
            replacement_url = search_upstream_replacement(ch['name'], upstream_pool)
            if replacement_url:
                print(f" [AUTO-HEALED ✓] {ch['name']}: {ch['url']} -> {replacement_url}")
                ch['url'] = replacement_url
                healed_count += 1
            else:
                print(f" [NO REPLACEMENT] {ch['name']} kept last known URL")
        print(f"Auto-Healing complete: {healed_count} streams repaired from upstream scraper.")

    # Write updated fta_channels.json
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(channels, f, indent=2, ensure_ascii=False)

    # Write updated playlist.m3u
    m3u_lines = ["#EXTM3U\n"]
    for ch in channels:
        m3u_lines.append(f'#EXTINF:-1 tvg-name="{ch["name"]}" tvg-logo="{ch["logo"]}" group-title="{ch["group"]}",{ch["name"]}\n')
        m3u_lines.append(f'{ch["url"]}\n')

    with open(m3u_path, 'w', encoding='utf-8') as f:
        f.writelines(m3u_lines)

    print("Catalog & playlist synchronized successfully.")

if __name__ == '__main__':
    main()
