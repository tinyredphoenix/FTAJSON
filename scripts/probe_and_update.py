import json
import urllib.request
import concurrent.futures
import os
import sys

def check_channel(ch):
    url = ch['url']
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            if res.status == 200:
                chunk = res.read(500).decode('utf-8', errors='ignore')
                if '#EXTM3U' in chunk:
                    return (True, ch)
    except Exception as e:
        print(f"[FAIL] {ch['name']}: {e}")
    return (False, ch)

def main():
    json_path = os.path.join(os.path.dirname(__file__), '..', 'fta_channels.json')
    m3u_path = os.path.join(os.path.dirname(__file__), '..', 'playlist.m3u')

    with open(json_path, 'r', encoding='utf-8') as f:
        channels = json.load(f)

    print(f"Probing {len(channels)} channels...")
    verified = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(check_channel, ch) for ch in channels]
        for f in concurrent.futures.as_completed(futures):
            ok, ch = f.result()
            if ok:
                verified.append(ch)

    print(f"\nVerification Results: {len(verified)} / {len(channels)} active.")

    if len(verified) < (len(channels) * 0.7):
        print("Warning: More than 30% of channels failed. Skipping auto-commit to prevent accidental catalog wipe.")
        sys.exit(0)

    # Sort channels by original order
    order_map = {ch['name']: i for i, ch in enumerate(channels)}
    verified.sort(key=lambda x: order_map.get(x['name'], 999))

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(verified, f, indent=2, ensure_ascii=False)

    m3u_lines = ["#EXTM3U\n"]
    for ch in verified:
        m3u_lines.append(f'#EXTINF:-1 tvg-name="{ch["name"]}" tvg-logo="{ch["logo"]}" group-title="{ch["group"]}",{ch["name"]}\n')
        m3u_lines.append(f'{ch["url"]}\n')

    with open(m3u_path, 'w', encoding='utf-8') as f:
        f.writelines(m3u_lines)

    print("Updated fta_channels.json and playlist.m3u successfully.")

if __name__ == '__main__':
    main()
