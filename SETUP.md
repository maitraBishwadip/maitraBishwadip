# Setup Guide — Bishwadip's GitHub Profile

## What's in this folder

```
github-profile/
├── README.md                        ← your profile page (copy to repo root)
├── .github/
│   └── workflows/
│       ├── snake.yml                ← generates the animated contribution snake
│       └── profile-3d.yml           ← generates the 3D contribution chart
└── SETUP.md                         ← this file
```

## Install (5 minutes)

1. Copy **everything** in this folder into your profile repo
   `maitraBishwadip/maitraBishwadip` (the repo whose README shows on your
   profile). Keep the `.github/workflows/` path exactly as is.
2. Commit and push to `main`.
3. Go to the repo → **Actions** tab → enable workflows if prompted, then:
   - Run **"Generate contribution snake"** → *Run workflow* (takes ~30 s).
   - Run **"Generate 3D contribution chart"** → *Run workflow* (takes ~1 min).
4. Refresh your profile. The snake and 3D chart images will now render.
   Both regenerate automatically every day.

## How the dark / light "toggle" works

GitHub strips all JavaScript and CSS from READMEs, so an in-page toggle button
is impossible — **every** profile you've seen switching themes uses this same
mechanism: the `<picture>` tag with `prefers-color-scheme`, which follows the
viewer's own GitHub theme.

- **Toggle it**: GitHub → your avatar → *Settings* → *Appearance* → Day / Night
  (or "Sync with system", which follows the OS toggle).
- **Dark mode** = Deep Space: cyan `#38BDF8` on `#0d1117`.
- **Light mode** = Moonlight: silver-indigo `#6E7FDB` / lavender `#9D7BEA`
  on pale moonlit blue `#f2f5fc`, with silvery capsule waves.

Every themed element swaps automatically: header/footer waves, typing text,
skill icons, all stat cards, streak, trophies, activity graph, snake, and the
3D chart.

## If the 3D chart shows a broken image

The action commits SVGs into a `profile-3d-contrib/` folder on `main`. The
README references `profile-night-rainbow.svg` (dark) and
`profile-season-animate.svg` (light). After the first run, open that folder in
your repo and confirm those filenames exist — if the action version generated
different names, update the two URLs in the "Contributions in 3D" section.

## SEO checklist (outside the README)

These matter more for search ranking than the README itself:

1. **Profile bio** (Settings → Public profile):
   `AI Native Microservices Engineer | Air Quality Researcher @ UW-BUET | Spring Boot · Spring AI · PyTorch`
   — the bio becomes the meta description of your profile page.
2. **Location field** — set it; recruiters filter by location.
3. **Pin 6 repos**, each with a one-line keyword-rich description.
4. **Profile repo description** — on `maitraBishwadip/maitraBishwadip`, set:
   "Bishwadip Maitra — AI engineer & air quality researcher".

## Notes

- **BUET logo** is hotlinked from Wikipedia
  (`upload.wikimedia.org/wikipedia/en/d/da/BUET_LOGO.svg`, verified working).
  It is a fair-use university emblem — standard for indicating affiliation.
  If UW-BUET gives you an official program logo, swap that URL in.
- **Streak stats** uses `streak-stats.demolab.com` (the old `herokuapp.com`
  instance in your previous README is deprecated and often dead).
- All GIF/asset URLs were verified returning HTTP 200 on 2026-07-09.
- Paper 2 author "Subhojit Mandai" was corrected to "Mandal" — double-check
  against the IEEE page.
