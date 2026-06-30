# Synology Photos Face Index Skill

A Codex skill for exporting path-only photo indexes from Synology Photos face/person albums.

It reuses Synology Photos' existing face-recognition database metadata, so it avoids rescanning large photo libraries and does not copy original photos.

## What It Does

- Finds photos for a named Synology Photos person, such as `小乔`.
- Exports original NAS paths in the format `YYYY-MM-DD|/volume1/photo/...`.
- Writes text indexes suitable for photo-frame or fridge-magnet push scripts.
- Includes schema probes for the `synofoto` PostgreSQL database.
- Keeps all database operations read-only.

## Files

- `SKILL.md`: Codex skill instructions.
- `agents/openai.yaml`: Skill display metadata.
- `references/synofoto-schema.md`: Synology Photos table and query notes.
- `scripts/export_face_index.py`: Helper script for generating or running the export command.

## Example

```bash
python3 scripts/export_face_index.py --person '小乔' --output /volume1/web/xiaoqiao_all.txt --photo-root /volume1/photo
