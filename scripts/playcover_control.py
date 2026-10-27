"""System mouse/keyboard driver with logical-coordinate screenshots and action log.
Run with a local Python environment containing PyAutoGUI, Pillow and PyObjC.
"""
import argparse
from datetime import datetime
import json
from pathlib import Path
import subprocess
import time
import pyautogui as gui
import Quartz
import AppKit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'runs/20261027-first-login'
OUT.mkdir(parents=True, exist_ok=True)
gui.FAILSAFE = True


def foreground():
    app = AppKit.NSWorkspace.sharedWorkspace().frontmostApplication()
    return {'name': str(app.localizedName()), 'bundle': str(app.bundleIdentifier()), 'pid': app.processIdentifier()}


def windows():
    values = []
    for w in Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID):
        owner = str(w.get('kCGWindowOwnerName', ''))
        title = str(w.get('kCGWindowName', ''))
        if '梦幻' in title or owner in ('Game', 'PlayCover', '梦幻西游', '梦幻西游2', '梦幻西游3'):
            entry = {k: w.get(k) for k in ('kCGWindowNumber', 'kCGWindowOwnerPID', 'kCGWindowOwnerName', 'kCGWindowName', 'kCGWindowLayer')}
            entry['kCGWindowBounds'] = dict(w.get('kCGWindowBounds', {}))
            values.append(entry)
    return values


def record(action, details):
    data = {'time': datetime.now().astimezone().isoformat(), 'action': action, 'details': details, 'foreground': foreground()}
    with (OUT / 'actions.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')
    print(json.dumps(data, ensure_ascii=False), flush=True)


def snapshot(label):
    size = tuple(gui.size())
    image = gui.screenshot()
    path = OUT / f'{datetime.now():%H%M%S}-{label}.png'
    # One output pixel equals one mouse point, independent of Retina backing scale.
    image.resize(size).save(path)
    record('snapshot', {'path': str(path), 'logical_size': size, 'raw_size': image.size, 'windows': windows()})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['snapshot', 'open-playcover', 'activate', 'click', 'doubleclick', 'key', 'paste'])
    parser.add_argument('values', nargs='*')
    parser.add_argument('--expected', help='Required foreground bundle before input')
    parser.add_argument('--label', default='state')
    parser.add_argument('--hold', type=float, default=0.2, help='Mouse press duration in seconds; PlayCover requires a sustained touch')
    args = parser.parse_args()
    if args.expected and foreground()['bundle'] != args.expected:
        raise SystemExit(f'Foreground guard rejected: {foreground()}')
    if args.action == 'open-playcover':
        subprocess.run(['open', '-a', 'PlayCover'], check=True)
        time.sleep(1)
    elif args.action == 'activate':
        apps = [a for a in AppKit.NSWorkspace.sharedWorkspace().runningApplications() if str(a.bundleIdentifier()) == args.values[0]]
        if len(apps) != 1:
            raise SystemExit(f'Expected one running app: {args.values[0]}, found {len(apps)}')
        apps[0].activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
        time.sleep(0.5)
    elif args.action in ('click', 'doubleclick'):
        x, y = map(float, args.values)
        gui.moveTo(x, y, duration=0.25)
        if not 0.05 <= args.hold <= 2:
            raise SystemExit('--hold must be between 0.05 and 2 seconds')
        for _ in range(2 if args.action == 'doubleclick' else 1):
            gui.mouseDown()
            try:
                time.sleep(args.hold)
            finally:
                gui.mouseUp()
            time.sleep(0.15)
        time.sleep(0.7)
    elif args.action == 'key':
        gui.hotkey(*args.values)
        time.sleep(0.5)
    elif args.action == 'paste':
        text = ' '.join(args.values)
        board = AppKit.NSPasteboard.generalPasteboard()
        board.clearContents()
        board.setString_forType_(text, AppKit.NSPasteboardTypeString)
        gui.hotkey('command', 'v')
        time.sleep(0.5)
    record(args.action, {'values': args.values})
    snapshot(args.label)


if __name__ == '__main__':
    main()
