# Tubeline — Launch & Publishing Guide

Everything needed to take **Tubeline** (YouTube channel analytics) from this codebase to the
Google Play Store, then later the Apple App Store — plus trademark registration and the paid
**Tubeline AI** ($1) upgrade.

> **Tubeline is not yet a registered product.** See [Registering the "Tubeline" name](#1-registering-the-tubeline-name) below. Until a trademark is filed, treat the name as a working title.

---

## 0. What the app does (store description)

**Short description (≤ 80 chars):**
> Analyze any YouTube channel: views, uploads & engagement over time.

**Full description (Play Store / App Store listing):**

> **Tubeline turns any YouTube channel into a clean, visual analytics dashboard.**
>
> Enter a channel handle, name, or URL and instantly see how it has grown over time — a
> beautiful timeline of uploads, views, likes, comments, and average video length, grouped by
> month and year.
>
> **Features**
> - 📈 Interactive timeline charts — area, line, bar, pie & doughnut, switchable on the fly
> - 🎛️ Smart filters — pick any metric, group by month or year, drill into a single year
> - 🏆 Top videos ranked by views, likes, comments, or duration, with share-of-total %
> - 🧮 Pivot table of activity across every month and year
> - 👥 Audience overview (demographics)*
> - ⬇️ Export what you see — PNG, CSV, Excel, PDF, and Word
> - 🔗 Share to X, Facebook, LinkedIn, WhatsApp, Telegram, Reddit, Pinterest, Tumblr, or email
> - 🌙 Clean, fast, light interface designed for phones and tablets
>
> **Tubeline AI (optional $1 upgrade)** adds growth forecasts, best-time-to-post analysis,
> AI-generated title ideas, content-gap discovery, and an auto-written performance report.
>
> Free to download. No account required to explore public channel data.
>
> *Audience demographics and average view duration require connecting your own channel
> (Google sign-in) and are available only for channels you own/manage. Tubeline is not
> affiliated with or endorsed by YouTube or Google.

**Required disclaimer (keep this in the listing):** Tubeline uses the YouTube Data API and is
not endorsed by or affiliated with YouTube/Google. Avoid leading the **app title** with the
word "YouTube" (trademark policy) — describe it as "for YouTube" in the body instead.

---

## 1. Registering the "Tubeline" name

You have two separate things to secure: the **brand/trademark** and the **app identity** on each store.

### 1a. Trademark (protects the brand)
1. **Clearance search** — check availability before filing:
   - USPTO TESS: https://tmsearch.uspto.gov (US)
   - EUIPO eSearch (EU), or your local IP office
   - Also check domains (tubeline.app / .com) and social handles.
2. **Pick the class** — software/apps are **Nice Class 9** (downloadable software) and often
   **Class 42** (SaaS). Analytics services can also touch **Class 35**.
3. **File the application:**
   - US: USPTO TEAS at https://www.uspto.gov/trademarks (≈ $250–$350 per class).
   - You can file a **"1(b) intent-to-use"** application before launch.
4. Use **™** now (no registration needed); switch to **®** only after registration is granted.
5. Budget ~6–12 months for examination. A trademark attorney is optional but reduces rejections.

> If "Tubeline" is taken in Class 9/42, strong fallbacks: **ChannelGrid**, **Vidline**,
> **Upload Atlas**, **Channelytics**.

### 1b. App identity (per store)
- **Android package name** (permanent, cannot change after publish): `app.tubeline.analytics`
  or `com.<yourdomain>.tubeline`. Pick the reverse-DNS of a domain you control.
- **Apple Bundle ID** (later): `app.tubeline.analytics` to match.
- Register a matching **domain** and **support email** — both stores require a privacy-policy URL
  and contact.

---

## 2. Google Play — publishing checklist

This Flask web app ships to Play as an Android app most efficiently via a **Trusted Web Activity
(TWA)** that loads a hosted version of the site. Native rewrite is optional later.

### 2a. Host the backend
The YouTube API key must stay server-side (never embedded in the app). Deploy `web_app.py` to a
host (Render, Railway, Fly.io, Cloud Run, etc.) with `YOUTUBE_API_KEY` set as an environment
variable, behind HTTPS. The mobile app will point at that URL.

### 2b. Wrap as an Android app (TWA via Bubblewrap)
```bash
npm i -g @bubblewrap/cli
bubblewrap init --manifest https://your-domain/manifest.webmanifest
bubblewrap build        # produces an .aab (Android App Bundle) + signing key
```
- Add a `manifest.webmanifest` and a `assetlinks.json` (Digital Asset Links) so the app opens
  full-screen without a browser bar.
- Output is an **`.aab`** — the format Play requires.

### 2c. Play Console setup
1. Create a **Google Play Developer account** — one-time **$25** fee: https://play.google.com/console
2. Create the app → fill **store listing** (use the description in §0).
3. Upload **graphic assets**:
   - App icon 512×512 PNG (use the Tubeline mark — red rounded square + white bars/play arrow)
   - Feature graphic 1024×500
   - At least 2 phone screenshots (and 7-inch/10-inch tablet shots recommended)
4. Complete required forms: **Privacy Policy URL**, **Data safety**, **Content rating**,
   **Target audience**, **Ads** declaration.
5. **Pricing** → set app to **Free** (see §4).
6. Roll out to **Internal testing** → **Closed** → **Production**.

### 2d. In-app purchase for Tubeline AI ($1)
- In Play Console → **Monetize → Products → In-app products**, create a **one-time managed
  product** `tubeline_ai_unlock` priced at **$1.00**.
- In the TWA, use the **Play Billing** via the Digital Goods API / Payment Request, or implement
  billing in a thin native layer. The current "Upgrade — $1.00" button is a placeholder that
  must be wired to Play Billing before release.
- Google takes a service fee (15% for the first $1M/yr under the standard program).

---

## 3. Apple App Store — later

Once Play is stable, the same hosted site can ship to iOS:
- **Apple Developer Program**: **$99/year** — https://developer.apple.com/programs/
- iOS does **not** allow pure TWA; options:
  - Wrap the site in a **WKWebView** shell app (simplest), or
  - Rebuild the UI natively / with a cross-platform framework (Flutter, React Native, Capacitor).
  - **Capacitor** is the smoothest path to reuse this exact HTML/JS UI on iOS.
- Use **StoreKit In-App Purchase** for the $1 Tubeline AI unlock (Apple takes 15–30%).
- Apple review is stricter — ensure the app provides clear value beyond a website and includes a
  privacy policy + account-deletion path if you add sign-in.

---

## 4. Pricing plan

| Phase | App price | In-app |
|---|---|---|
| Launch | **Free to download** | — |
| ~1 month after launch | Free | **Tubeline AI** one-time unlock |
| | | Target **$0.25** ⚠️ — see note | 
| Recommended | Free | **Tubeline AI $1.00** one-time |

> ⚠️ **About the $0.25 idea:** Google Play and Apple enforce **minimum price points**. Google's
> lowest tier is around **$0.10–$0.99** depending on market, and Apple's lowest tier is
> typically **$0.49–$0.99**. A flat $0.25 may not be selectable in every country. Cleaner plan:
> keep the **app Free**, and sell **Tubeline AI as a $1.00 one-time in-app purchase** (matches
> your "$1 upgrade" ask and avoids minimum-price problems). You can run intro promos instead of a
> permanent $0.25 price.

---

## 5. Tubeline AI — paid features ($1 unlock)

The Pro panel in the app currently previews these (blurred + locked). To ship them, add an
AI backend endpoint (e.g. OpenAI/Gemini) gated behind the purchase entitlement:

- **Growth forecast** — project next-30-day views/uploads from the historical series.
- **Best time to post** — cluster top videos by weekday/hour of `published_at`.
- **AI title & topic ideas** — generate from the channel's best-performing titles.
- **Content-gap finder** — compare the channel's topics against audience demand.
- **Auto performance report** — a shareable AI-written summary (ties into existing export/share).

Keep AI calls server-side; verify the Play/Apple purchase receipt before returning AI results.

---

## 6. How Tubeline compares to top YouTube analytics tools

| Capability | TubeBuddy / vidIQ / Social Blade | **Tubeline** |
|---|---|---|
| Public channel timeline (uploads/views/likes) | ✅ | ✅ |
| Works on **any** channel without login | Partial | ✅ |
| Clean mobile dashboard + export (PDF/Excel/CSV/Doc) | Partial | ✅ |
| Share to all social platforms | ❌ mostly | ✅ |
| Demographics / watch time | ✅ (owned channels, paid) | ⏳ phase 2 (channel sign-in) |
| Keyword/SEO tools | ✅ | ❌ (out of scope) |
| AI insights | ✅ (subscription) | ✅ **one-time $1** |

**Tubeline's edge:** simple, fast, no-login exploration of *any* channel, first-class export &
sharing, and a cheap one-time AI unlock instead of a monthly subscription.

To reach parity on owned-channel analytics (demographics, average view duration, traffic
sources), add **YouTube OAuth + YouTube Analytics API** — these require the viewer to sign in and
only return data for channels they own/manage.

---

## 7. Pre-launch checklist
- [ ] Trademark cleared & filed (or fallback name chosen)
- [ ] Domain + support email + privacy policy URL live
- [ ] Backend deployed over HTTPS with `YOUTUBE_API_KEY` set
- [ ] Android package name finalized (immutable)
- [ ] Icon 512², feature graphic 1024×500, screenshots ready
- [ ] Data safety + content rating forms completed
- [ ] Play Billing wired to the $1 Tubeline AI product
- [ ] Internal → closed → production rollout
