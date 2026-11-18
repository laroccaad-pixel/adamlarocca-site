# adamlarocca.com

Static portfolio site.

- `site/` is the live website. Cloudflare Pages publishes this folder.
- `content/` and `projects.json` hold the project data. `build.py` regenerates `site/` from them.
- To hide a project: set `"visible": false` in `projects.json`, run `python3 build.py`, push.
