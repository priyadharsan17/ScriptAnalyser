"""Utility: poll Telegram getUpdates and print the first chat_id seen.

Usage:
  python scripts/get_chat_id.py --token <BOT_TOKEN>

The script polls Telegram's `getUpdates` until it sees a message (send one in your group
after adding the bot). It prints the `chat.id` and a JSON dump of the chat object.
"""
import argparse
import json
import time
from typing import Any, Dict, List

import requests


def get_updates(token: str, offset: int = None) -> List[Dict[str, Any]]:
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {}
    if offset is not None:
        params['offset'] = offset
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json().get('result', [])


def main():
    parser = argparse.ArgumentParser(description="Poll Telegram getUpdates and print chat_id")
    parser.add_argument('--token', '-t', required=True, help='Telegram bot token')
    parser.add_argument('--poll-interval', type=float, default=1.0, help='Seconds between polls')
    parser.add_argument('--clear-offset', action='store_true', help='Start from latest update (ignore old ones)')
    args = parser.parse_args()

    token = args.token
    seen_update_ids = set()
    last_offset = None

    if args.clear_offset:
        try:
            updates = get_updates(token)
            if updates:
                # set offset to last update_id + 1 to ignore older updates
                last_offset = max(u.get('update_id', 0) for u in updates) + 1
                print(f"Clearing old updates; starting from offset {last_offset}")
        except Exception as e:
            print(f"Warning: could not clear offset: {e}")

    print("Waiting for a new message in the group (send one now)...")
    try:
        while True:
            try:
                updates = get_updates(token, offset=last_offset)
            except Exception as e:
                print(f"Error fetching updates: {e}")
                time.sleep(args.poll_interval)
                continue

            for u in updates:
                uid = u.get('update_id')
                if uid in seen_update_ids:
                    continue
                seen_update_ids.add(uid)

                # If we used offset, advance it so Telegram doesn't keep returning same updates
                if last_offset is None or uid >= (last_offset or 0):
                    last_offset = uid + 1

                msg = u.get('message') or u.get('edited_message') or u.get('channel_post') or u.get('edited_channel_post')
                if not msg:
                    continue
                chat = msg.get('chat', {})
                print('\nFound chat id:', chat.get('id'))
                print('Chat object:')
                print(json.dumps(chat, indent=2))
                return

            time.sleep(args.poll_interval)
    except KeyboardInterrupt:
        print('\nInterrupted by user')


if __name__ == '__main__':
    main()
