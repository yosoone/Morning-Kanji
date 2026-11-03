# Morning page

A one-page writing sheet for the **reMarkable 2**, sent to the tablet before dawn each day. Each page holds one kanji (its readings, parts, stroke order and tracing boxes) and a prompt for a River text, with lined space to write.

The day files in `days/` hold the content, so opening them spoils the surprise.

## How it works

1. **Schedule:** GitHub Actions tries `.github/workflows/morning.yml` every hour from **00:47 to 06:47 in Miyazaki**, because GitHub can delay or drop scheduled runs.[^5] The first run that finds an unsent page sends it; the rest stop at once.
2. **Pick:** `send_page.sh` looks for `days/<today>.json`, using the date in Japan. If there is no file, it does nothing.
3. **Build:** `make_page.py` renders a one-page PDF at the reMarkable 2 screen size (1404 × 1872 px at 226 dpi).
4. **Send:** [rmapi](https://github.com/ddvk/rmapi)[^1] uploads it to a folder called **Morning** on the tablet. The file is named by date only.
5. **Record:** the date goes into `sent.log`, so a page is never sent twice. Keep this repository private: GitHub pauses scheduled workflows in public repositories after 60 days without activity.[^2]

## One-time setup

### 1. Pair rmapi with your reMarkable account

On your Mac, in Terminal:

1. Download `rmapi-macos-arm64.zip` or `rmapi-macos-intel.zip` from the [v0.0.35 release](https://github.com/ddvk/rmapi/releases/tag/v0.0.35)[^1] and unzip it.
2. Run `./rmapi` once. It asks for a one-time code.
3. Get the code from [my.remarkable.com/device/desktop/connect](https://my.remarkable.com/device/desktop/connect) and paste it in.
4. Type `exit`. Your device token is now saved in `~/Library/Application Support/rmapi/rmapi.conf` on a Mac (`~/.config/rmapi/rmapi.conf` on Linux).

### 2. Add the token as a repository secret

In this repository on GitHub: **Settings → Secrets and variables → Actions → New repository secret**.

- **Name:** `RMAPI_CONFIG`
- **Value:** the whole contents of that file, e.g. `cat ~/Library/Application\ Support/rmapi/rmapi.conf`

Keep this token private. Anyone who has it can read and change the documents on your reMarkable.

### 3. Test

**Actions → Morning page → Run workflow**, and enter a date that has a day file.

## Adding days

Add `days/YYYY-MM-DD.json` in the same shape as the existing files, plus the KanjiVG stroke file for the kanji in `kanjivg/` (`<unicode-hex>.svg`, e.g. `0606f.svg`).

Every reading, meaning, stroke count and grade is checked against KANJIDIC2 and JMdict before a day is added.[^3]

To build a page locally without sending it:

```sh
DRY_RUN=1 ./send_page.sh 2026-11-03
```

Local builds need `wkhtmltopdf`, `fonts-noto-cjk`, `poppler-utils` and the Python package `pypdf`.

## Licences

- **Stroke data:** KanjiVG, © Ulrich Apel, CC BY-SA 3.0.[^4] The files in `kanjivg/` are unchanged copies, and each page carries the credit.
- **Dictionary data:** KANJIDIC2 and JMdict, Electronic Dictionary Research and Development Group, CC BY-SA 4.0.[^3]

Pages shared beyond personal use carry these share-alike terms with them.

[^1]: ddvk, *rmapi* (reMarkable cloud command-line client), GitHub, release v0.0.35, https://github.com/ddvk/rmapi/releases/tag/v0.0.35.
[^2]: GitHub Docs, "Disabling and enabling a workflow," https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows.
[^3]: Electronic Dictionary Research and Development Group, "KANJIDIC Project" and "JMdict-EDICT Dictionary Project," https://www.edrdg.org/.
[^4]: Ulrich Apel, *KanjiVG*, https://kanjivg.tagaini.net.
[^5]: GitHub Docs, "Events that trigger workflows: schedule," https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule.
