#!/usr/bin/env python3
import argparse
import shlex
import subprocess
from pathlib import Path

EXT_RE = r"\.(jpg|jpeg|png|heic|webp)$"


def sql(person, photo_root, limit=None, extensions=EXT_RE):
    limit_clause = f"\nlimit {int(limit)}" if limit else ""
    person_lit = person.replace("'", "''")
    root_lit = photo_root.rstrip('/').replace("'", "''")
    ext_lit = extensions.replace("'", "''")
    return f"""
select distinct
  to_char(to_timestamp(pt.takentime), 'YYYY-MM-DD') || '|' ||
  '{root_lit}' || f.name || '/' || u.filename
from person p
join person_timeline_view pt on p.id = any(pt.id_person)
join unit u on u.id = pt.id_unit
join folder f on f.id = u.id_folder
where p.name = '{person_lit}'
  and lower(u.filename) ~ '{ext_lit}'
order by 1 desc{limit_clause};
""".strip()


def psql_command(args):
    query = sql(args.person, args.photo_root, args.limit, args.extensions)
    base = ["sudo", "-u", args.pg_user, "psql", "-d", args.database, "-P", "pager=off", "-Atc", query]
    return base


def main():
    parser = argparse.ArgumentParser(description="Export a Synology Photos face/person album to a path-only txt index.")
    parser.add_argument("--person", required=True, help="Synology Photos person name, e.g. 小乔")
    parser.add_argument("--output", required=True, help="Output txt path, e.g. /volume1/web/xiaoqiao_all.txt")
    parser.add_argument("--photo-root", default="/volume1/photo", help="Filesystem root for shared Photos library")
    parser.add_argument("--database", default="synofoto")
    parser.add_argument("--pg-user", default="postgres")
    parser.add_argument("--limit", type=int, help="Optional row limit for testing")
    parser.add_argument("--extensions", default=EXT_RE, help="Postgres regex for accepted filenames")
    parser.add_argument("--print-command", action="store_true", help="Print a shell command instead of running psql")
    args = parser.parse_args()

    cmd = psql_command(args)
    if args.print_command:
        print(" ".join(shlex.quote(x) for x in cmd) + " > " + shlex.quote(args.output))
        return 0

    out = subprocess.check_output(cmd, text=True)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(out, encoding="utf-8")
    count = 0 if not out else out.count("\n") + (0 if out.endswith("\n") else 1)
    print(f"wrote {count} rows to {output}")


if __name__ == "__main__":
    raise SystemExit(main())
