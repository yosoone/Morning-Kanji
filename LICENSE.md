# Licence

This repository holds three kinds of material, each under its own terms.

## 1. The generated pages: CC BY-SA 4.0

Every PDF page this project produces is © Yoso ([hub.yoso.one](https://hub.yoso.one)) and is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International** licence: <https://creativecommons.org/licenses/by-sa/4.0/>.

The pages must carry this licence because they are built from the share-alike data in section 2. KanjiVG is under CC BY-SA 3.0, which allows adaptations to be licensed under a later version with the same licence elements, so a single CC BY-SA 4.0 licence covers both sources.

Each page carries its credits and licence in the footer.

## 2. Third-party data

### Stroke data: KanjiVG

- **Files:** `kanjivg/*.svg`, unmodified copies. Each file keeps its own copyright header.
- **Copyright:** © Ulrich Apel
- **Licence:** Creative Commons Attribution-ShareAlike 3.0, <https://creativecommons.org/licenses/by-sa/3.0/>
- **Source:** <https://kanjivg.tagaini.net>

### Readings and meanings: KANJIDIC2 and JMdict

- **Use:** the readings, meanings, stroke counts and grades in `days/*.json` were checked against these files.
- **Copyright:** © Electronic Dictionary Research and Development Group (EDRDG)
- **Licence:** Creative Commons Attribution-ShareAlike 4.0, <https://creativecommons.org/licenses/by-sa/4.0/>
- **Licence statement:** <https://www.edrdg.org/edrdg/licence.html>
- **Project pages:** [KANJIDIC Project](https://www.edrdg.org/wiki/KANJIDIC_Project.html), [JMdict Project](https://www.edrdg.org/jmdict/j_jmdict.html)

This publication has included material from the JMdict and KANJIDIC dictionary files in accordance with the licence provisions of the Electronic Dictionary Research and Development Group.

## 3. Everything else: all rights reserved

The code (`make_page.py`, `send_page.sh`, the workflow), the page design and the writing prompts are © Yoso. All rights reserved.

## Tools used, not included

These are used to build or send the pages, but are not copied into this repository:

- **Noto Sans CJK** font, embedded in each PDF: SIL Open Font License 1.1, which allows embedding in documents.
- **rmapi**, which uploads the pages: AGPL-3.0. It is downloaded and run unchanged, so its terms do not extend to this project.
- **wkhtmltopdf**, **pypdf** and **poppler-utils**, used to build the PDF.
