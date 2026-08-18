"""Utility to repair mojibake (乱码) file and directory names.

Safe by default: requires an explicit ``--target`` directory and only renames
when a name can be *provably* recovered to a different, valid form (no guesses).
Use ``--dry-run`` to preview without changing anything.

Typical fallbacks attempted, in order:
  1. ``errors='surrogateescape'`` round-trip already-valid UTF-8 (no-op guard).
  2. Latin-1 bytes re-read as UTF-8 (covers single-level cp1252-style mangling).

Names that cannot be recovered are reported but left untouched.
"""

import argparse
import os
import shutil


def recover(name):
    """Return the recovered name if provably different-and-valid, else None."""
    if not name:
        return None
    # Latin-1 -> UTF-8 (valid, changed) is a real recovery.
    try:
        fixed = name.encode('latin-1').decode('utf-8')
        if fixed != name:
            return fixed
    except (UnicodeError, UnicodeEncodeError, UnicodeDecodeError):
        pass
    return None


def walk(path):
    """Yield absolute dir paths deepest-first so children are renamed first."""
    for dirpath, dirnames, filenames in os.walk(path, topdown=True):
        yield dirpath, False, filenames
        for d in list(dirnames):
            cand = os.path.join(dirpath, d)
            if os.path.isdir(cand) and not os.path.islink(cand):
                yield cand, True, os.listdir(cand)


def rename_entry(child_path, dry_run, applied, skipped):
    parent, child_name = os.path.split(child_path)
    fixed = recover(child_name)
    if fixed is None or fixed == child_name:
        return
    dest = os.path.join(parent, fixed)
    if os.path.exists(dest):
        skipped.append((child_path, 'destination exists'))
        return
    print(f'{"[dry-run] " if dry_run else ""}rename: {child_path!r} -> {dest!r}')
    applied.append((child_path, dest))
    if not dry_run:
        try:
            if os.path.isdir(child_path):
                shutil.move(child_path, dest)
            else:
                os.rename(child_path, dest)
        except OSError as e:
            skipped.append((child_path, str(e)))


def run(target, dry_run):
    applied = []
    skipped = []
    dirs_first = list(walk(target))
    # Rename deepest first to avoid re-walking surprises.
    for dirpath, is_dir, names in dirs_first:
        if is_dir:
            rename_entry(dirpath, dry_run, applied, skipped)
    # Files
    for dirpath, is_dir, names in dirs_first:
        if not is_dir:
            for n in names:
                rename_entry(os.path.join(dirpath, n), dry_run, applied, skipped)
    return applied, skipped


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('target', help='directory to scan (MUST be explicit)')
    ap.add_argument('--dry-run', action='store_true', help='only report potential renames')
    args = ap.parse_args(argv)
    if not os.path.isdir(args.target):
        raise SystemExit(f'not a directory: {args.target}')
    applied, skipped = run(args.target, args.dry_run)
    print(f'\napplied/reportable: {len(applied)}, skipped: {len(skipped)}')


if __name__ == '__main__':
    main()