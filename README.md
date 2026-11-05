# Morning page

A one-page writing sheet for the **reMarkable 2**, sent to the tablet before dawn each day. Each page holds one kanji (its readings, parts, stroke order and tracing boxes) and a prompt for a River text, with lined space to write.

The day files in `days/` hold the content, so opening them spoils the surprise.

## How it works

1. **Schedule:** GitHub Actions runs `.github/workflows/morning.yml` once a day at **21:47 in Miyazaki**, sending the page for the next morning. GitHub can delay or drop scheduled runs,[^5] so sending the evening before leaves room for a late run.
2. **Pick:** `send_page.sh` looks for `days/<date>.json` for the coming morning in Japan (any run before noon counts for that same day). If there is no file, it does nothing.
3. **Build:** `make_page.py` renders a one-page PDF at the reMarkable 2 screen size (1404 × 1872 px at 226 dpi).
4. **Send:** [rmapi](https://github.com/ddvk/rmapi)[^1] uploads it to the top level (root) of the tablet, named date-romaji, e.g. `2026-11-03-iki`. The tablet cannot display kanji in file names.
5. **Record:** the date goes into `sent.log`, so a page is never sent twice, and an exact copy of the PDF is kept in `archive/`. Keep this repository private: GitHub pauses scheduled workflows in public repositories after 60 days without activity.[^2]

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

See [LICENSE.md](LICENSE.md). In short:

- **Pages, including prompts and design:** © Yoso, [hub.yoso.one](https://hub.yoso.one), under CC BY-SA 4.0, credited as "Concept, design and prompts: Yoso".
- **Stroke data:** KanjiVG, © Ulrich Apel, CC BY-SA 3.0.[^4] The files in `kanjivg/` are unchanged copies, with their own copyright headers.
- **Dictionary data:** this package uses the JMdict and KANJIDIC dictionary files, © Electronic Dictionary Research and Development Group, under CC BY-SA 4.0, in accordance with the Group's licence.[^3]
- **Code:** © Yoso, all rights reserved.

Every page carries these credits in its footer, each with a link to its source and licence.

[^1]: ddvk, *rmapi* (reMarkable cloud command-line client), GitHub, release v0.0.35, https://github.com/ddvk/rmapi/releases/tag/v0.0.35.
[^2]: GitHub Docs, "Disabling and enabling a workflow," https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows.
[^3]: Electronic Dictionary Research and Development Group, "General Dictionary Licence Statement," https://www.edrdg.org/edrdg/licence.html; "KANJIDIC Project," https://www.edrdg.org/wiki/KANJIDIC_Project.html; "The JMDict Project," https://www.edrdg.org/jmdict/j_jmdict.html.
[^4]: Ulrich Apel, *KanjiVG*, https://kanjivg.tagaini.net.
[^5]: GitHub Docs, "Events that trigger workflows: schedule," https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule.
