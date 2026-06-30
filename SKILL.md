---
name: synology-photos-face-index
description: Export original-photo path index files from Synology Photos face/person albums by reusing Synology Photos database metadata. Use when the user asks to batch extract photos for a named person/face tag from a Synology NAS, generate txt/csv indexes under /volume1/web, avoid copying photos, inspect synofoto PostgreSQL tables, or replace slow filesystem/photo rescans with Synology Photos face-recognition results.
---

# Synology Photos Face Index

## Purpose

Use Synology Photos' own face-recognition database to produce path-only photo index files such as `YYYY-MM-DD|/volume1/photo/...`. The workflow avoids re-scanning 100k+ files and does not copy photos.

## Workflow

1. Confirm the user can SSH to the NAS and can run `sudo -u postgres psql`. If not, guide them through enabling SSH and testing `ssh -p <port> <user>@<nas-ip>`.
2. Discover the database name, normally `synofoto`:

```bash
sudo -u postgres psql -Atc "select datname from pg_database order by datname;"
```

3. Inspect the key tables only if the schema is unknown. Read `references/synofoto-schema.md` for the expected Synology Photos 1.8 style schema and fallback probes.
4. Verify a named person and a small sample before exporting everything:

```bash
sudo -u postgres psql -d synofoto -P pager=off -F $'\t' -Atc "
select p.id, p.name, count(*)
from person p
join person_timeline_view pt on p.id = any(pt.id_person)
where p.name = '<PERSON_NAME>'
group by p.id, p.name;
"
```

5. Export with `scripts/export_face_index.py` when possible. It prints the exact psql command or can run it locally on the NAS.

## Recommended Export

For a Synology Photos shared-space root at `/volume1/photo`, a named person such as `小乔`, and the legacy index format used by existing frame scripts:

```bash
python3 scripts/export_face_index.py --person '小乔' --output /volume1/web/xiaoqiao_all.txt --photo-root /volume1/photo
```

If the script is not available on the NAS, paste this SQL form into the NAS terminal:

```bash
sudo -u postgres psql -d synofoto -P pager=off -Atc "
select distinct
  to_char(to_timestamp(pt.takentime), 'YYYY-MM-DD') || '|' ||
  '/volume1/photo' || f.name || '/' || u.filename
from person p
join person_timeline_view pt on p.id = any(pt.id_person)
join unit u on u.id = pt.id_unit
join folder f on f.id = u.id_folder
where p.name = '小乔'
  and lower(u.filename) ~ '\.(jpg|jpeg|png|heic|webp)$'
order by 1 desc;
" > /volume1/web/xiaoqiao_all.txt
```

Validate output:

```bash
awk 'END{print NR}' /volume1/web/xiaoqiao_all.txt
head -5 /volume1/web/xiaoqiao_all.txt
```

## Important Details

- Keep queries read-only. Do not update Synology Photos tables.
- Use `-P pager=off` to avoid `--More--` blocking copy/paste.
- `folder.name` may already contain a slash-prefixed relative folder path, for example `/Pocket4` or `/oppo/DCIM/Camera/2026/04`; verify before adding recursive folder logic.
- Verify the photo root with `ls -l` on a known exported path. In the original case it was `/volume1/photo`, not `/volume2/photo`.
- `person_timeline_view.id_person` is an array, so join with `p.id = any(pt.id_person)`.
- The legacy frame script accepts lines where the date appears before the `/volume1` path. `YYYY-MM-DD|/volume1/photo/file.jpg` is valid.
- If the user wants multiple people, export separate indexes first, then combine with `sort -u` only after confirming duplicates are acceptable.

## Resources

- `scripts/export_face_index.py`: Generates or runs the read-only psql export command.
- `references/synofoto-schema.md`: Expected tables, probes, and troubleshooting notes.
