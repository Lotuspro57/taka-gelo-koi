# টাকা গেল কই? (Taka Gelo Koi?)

A simple, Bengali-first money diary for Android — "where did my money go?".
This is the renamed and redesigned **MyKhata**: same data, friendlier screens.

<p align="center"><img src="design/icon-512.png" width="160" alt="App icon"></p>

## What changed

| | MyKhata | টাকা গেল কই? |
|---|---|---|
| Name | MyKhata | **টাকা গেল কই?** |
| Language | English | Bengali UI, Bengali digits (৳১,২৫০), Hind Siliguri font bundled (works offline) |
| Add an entry | long form + select boxes | one screen: big amount, number pad with `+` `−`, tap a category picture, save |
| Navigation | 5 small tabs + hidden modal | Home · খাতা · **＋** · কই গেল? · পাওনা-দেনা |
| Home | many small tiles | one clear answer: "this month you have ৳X left", top spending, today's entries |
| Calculator | separate pop-up | built into the number pad |
| Receivable / payable | "R/P" tab | **পাওনা-দেনা** — "আমি পাবো / আমি দেবো", "টাকা পেয়েছি / শোধ করেছি" |
| Edit an entry | delete only | tap an entry → ঠিক করুন (edit) or মুছুন |
| Delete / reset | browser `confirm()` (blocked in some WebViews) | in-app dialogs |
| Theme | 8 dark themes + custom colour | Light / Dark / Auto + 6 accent colours |
| Backup | transactions + categories | + পাওনা-দেনা + daily opening balances (old backups still import) |
| Back button | exits the app | closes sheets/screens first, then goes Home, then exits |

Your existing data is **not** touched: the storage keys are unchanged
(`mk_txs`, `mk_ecats`, `mk_icats`, `mykhata_rp`, `mk_ob`) and category names are
still stored in English — they are only *shown* in Bengali.

## Repo layout

```
web/                    the app (one HTML file + fonts + logo) – edit here
  index.html
tools/build_web.py      inlines fonts + logo -> app/src/main/assets/index.html
tools/make_icons.py     renders the icon + every Android launcher PNG
design/                 icon.svg, icon-512.png, play-store-icon-512.png
app/                    Android (Kotlin) WebView shell + bridge
  src/main/java/app/takagelokoi/MainActivity.kt
.github/workflows/build-apk.yml   builds a debug APK on every push
```

## Build the APK

**Easiest — GitHub does it for you**

1. Create an empty repo on GitHub, then:
   ```bash
   git init && git add . && git commit -m "টাকা গেল কই? v2.0"
   git branch -M main
   git remote add origin https://github.com/<you>/<repo>.git
   git push -u origin main
   ```
2. Open the repo → **Actions → Build APK → latest run → Artifacts → taka-gelo-koi-debug-apk**.
3. Unzip, copy the `.apk` to your phone, install.

**Locally** — Android Studio (Koala or newer): *Open* this folder → Run. Or with JDK 17 + Android SDK 34 + Gradle 8.7: `gradle assembleDebug`.

## Keeping your old MyKhata data

* If your old APK used a **different package name**, Android treats this as a new app.
  In the old app: *Settings → Export Backup*. In the new app: *সেটিংস → ব্যাকআপ ফিরিয়ে আনুন*.
* If you want to install **over** the old app (data stays), set `applicationId` in
  `app/build.gradle.kts` to the old package name and sign with the same key.

## Change the app without rebuilding the APK

1. Edit `web/index.html`, run `python3 tools/build_web.py`.
2. Send `app/src/main/assets/index.html` to the phone.
3. In the app: *সেটিংস → আপডেট ফাইল বেছে নিন → আপডেট চালু করুন*. Data stays.

(A newly installed APK always replaces an older side-loaded update.)

## Regenerate the icon

```bash
pip install playwright && playwright install chromium
python3 tools/make_icons.py
```

## Notes

* Fonts: Hind Siliguri, SIL Open Font License (`web/fonts/OFL-LICENSE.txt`).
* The web app was tested in a browser against MyKhata-format data. The Kotlin shell
  was written without an Android SDK available, so the first CI build is its first compile.
