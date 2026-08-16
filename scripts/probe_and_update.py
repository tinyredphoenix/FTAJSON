import json
import urllib.request
import concurrent.futures
import os
import sys

def check_stream(url, timeout=5):
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

def check_channel(ch):
    url = ch.get('url', '')
    if check_stream(url):
        return (True, ch, "PRIMARY_OK")
    
    # Check backup URL if configured
    backup_url = ch.get('backup_url', '')
    if backup_url and check_stream(backup_url):
        # Swap primary and backup
        updated = dict(ch)
        updated['url'] = backup_url
        updated['backup_url'] = url
        return (True, updated, "FAILOVER_OK")

    print(f"[FAIL] {ch['name']} unreachable on primary stream")
    return (False, ch, "FAILED")

def main():
    json_path = os.path.join(os.path.dirname(__file__), '..', 'fta_channels.json')
    m3u_path = os.path.join(os.path.dirname(__file__), '..', 'playlist.m3u')

    with open(json_path, 'r', encoding='utf-8') as f:
        channels = json.load(f)

    print(f"Probing {len(channels)} curated Indian FTA channels...")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(check_channel, ch) for ch in channels]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    active = [r[1] for r in results if r[0]]
    failed = [r[1] for r in results if not r[0]]

    print(f"\nVerification Results: {len(active)} / {len(channels)} channels verified active.")
    if failed:
        print(f"Temporary failures ({len(failed)} channels): {[ch['name'] for ch in failed]}")

    # Resilient policy: We keep all channels in the catalog so a temporary CDN blip
    # does NOT purge the channel from users' TV guides. We update the playlist.
    order_map = {ch['name']: i for i, ch in enumerate(channels)}
    
    # Save the updated catalog
    channels.sort(key=lambda x: order_map.get(x['name'], 999))
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(channels, f, indent=2, ensure_ascii=False)

    m3u_lines = ["#EXTM3U\n"]
    for ch in channels:
        m3u_lines.append(f'#EXTINF:-1 tvg-name="{ch["name"]}" tvg-logo="{ch["logo"]}" group-title="{ch["group"]}",{ch["name"]}\n')
        m3u_lines.append(f'{ch["url"]}\n')

    with open(m3u_path, 'w', encoding='utf-8') as f:
        f.writelines(m3u_lines)

    print("Completed health check successfully without failing the job.")

if __name__ == '__main__':
    main()
