# Synology Photos synofoto Schema Notes

Observed on Synology Photos 1.8.x. Table and column names may vary by version; probe before assuming.

## Key Tables and Views

- `person`: `id`, `id_user`, `name`, `hidden`, `cover`, `created_time`
- `person_timeline_view`: `id_item`, `id_user`, `item_type`, `unit_type`, `id_unit`, `id_person` array, `takentime`
- `unit`: `id`, `filename`, `takentime`, `id_item`, `id_folder`, `is_major`, `type`, `item_type`
- `folder`: `id`, `name`, `parent`, `shared`, `permission`
- `many_unit_has_many_person`: `id_unit`, `id_person`, `id_user`
- `face`: face-level rows with bounding boxes and `id_person`

The fastest export path is usually:

`person.name -> person.id -> person_timeline_view.id_person -> unit.id -> folder.id`

## Discovery Commands

List relevant tables:

```bash
sudo -u postgres psql -d synofoto -P pager=off -Atc "
select table_name
from information_schema.tables
where table_schema='public'
  and (table_name ilike '%person%' or table_name ilike '%face%' or table_name ilike '%item%' or table_name ilike '%unit%' or table_name ilike '%folder%')
order by table_name;
"
```

List columns for expected tables:

```bash
sudo -u postgres psql -d synofoto -P pager=off -Atc "
select table_name || ' | ' || string_agg(column_name || ':' || data_type, ', ' order by ordinal_position)
from information_schema.columns
where table_schema='public'
  and table_name in ('person','person_timeline_view','unit','folder','many_unit_has_many_person','face')
group by table_name
order by table_name;
"
```

## Folder Path Handling

Some Synology Photos installs store `folder.name` as a full slash-prefixed relative path. Verify with:

```bash
sudo -u postgres psql -d synofoto -P pager=off -F $'\t' -Atc "
select u.id, u.filename, u.id_folder, f.name, f.parent
from unit u left join folder f on f.id = u.id_folder
where u.id in (<KNOWN_UNIT_IDS>);
"
```

If `folder.name` is only a leaf name, build a recursive path from `folder.parent`. If no root rows have `parent is null or parent <= 0`, inspect known folders first and adapt the root condition.

## Common Pitfalls

- `wc -l` can report 99 for a 100-row file if the final line has no newline. Use `awk 'END{print NR}' file`.
- Browser thumbnail URLs expose `unit_id`, but Synology Photos web API may not allow direct metadata export with only `SynoToken`. Database export is more reliable.
- The query returns database-indexed paths. Always verify at least two real paths with `ls -l` before replacing a production index.
