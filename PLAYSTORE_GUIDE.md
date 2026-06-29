# GetGrowline — Play Store Publishing Guide

The app is now a **PWA** wrapped into an Android app as a **Trusted Web Activity (TWA)**.
This produces a real `.aab` you upload to the Play Console — no rewrite, the Android app just loads the live site full-screen.

## What's already done (in this repo)
- `static/manifest.webmanifest` — installable manifest (name, icons, theme, standalone)
- `static/icon-192/512.png` + `maskable-192/512.png` — app icons
- `static/sw.js` + `/offline` page — service worker (Play TWA requirement)
- PWA meta tags + SW registration in `templates/index.html`
- Routes for `/sw.js`, `/offline`, `/.well-known/assetlinks.json`

## Step 1 — Host the app on HTTPS
TWA requires a public HTTPS domain (TWAs can't load `127.0.0.1`).
Deploy the Flask app (Render, Railway, Fly.io, or a VPS) and point a domain at it,
e.g. `https://app.getgrowline.com`. Keep `YOUTUBE_API_KEY` set in the host's env.

## Step 2 — Build the Android app (Bubblewrap)
```bash
npm i -g @bubblewrap/cli
bubblewrap init --manifest https://app.getgrowline.com/static/manifest.webmanifest
# package id: com.growlinelabs.getgrowline
bubblewrap build
```
This outputs `app-release-bundle.aab` (upload) and a signing keystore.

## Step 3 — Digital Asset Links (removes URL bar)
Get your signing key SHA-256:
```bash
keytool -list -v -keystore android.keystore -alias android | grep SHA256
```
Put it in `static/assetlinks.json` (replace the placeholder fingerprint), redeploy.
Verify: `https://app.getgrowline.com/.well-known/assetlinks.json` returns it.

## Step 4 — Play Console
1. Create app at https://play.google.com/console ($25 one-time).
2. Upload the `.aab`. Use Play App Signing.
3. Store listing: icon `static/icon-512.png`, 2+ phone screenshots, 1024×500 feature graphic.
4. Privacy policy URL (required), data-safety form, content rating.
5. Submit for review.

## Notes
- Bump `CACHE` in `static/sw.js` when you ship updates so clients refresh.
- `start_url`/`scope` are `/` — site loads full-screen, splash uses theme color.
