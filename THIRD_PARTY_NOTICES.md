# Third-party materials / 第三方资料说明

The MIT license in this repository covers the project's original code and original documentation. It does not relicense third-party quotations, extracted game descriptions, trademarks, or other material whose rights belong to others.

## PoE2DB and extracted game descriptions

- Source: [PoE2DB](https://poe2db.tw/), including the [Currency](https://poe2db.tw/us/Currency), [Essence](https://poe2db.tw/us/Essence), [Omen](https://poe2db.tw/us/Omen), [Abyss](https://poe2db.tw/us/Abyss) and linked item pages.
- PoE2DB identifies its wiki content as [Creative Commons Attribution–NonCommercial–ShareAlike 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/) unless otherwise noted. That license, including attribution, non-commercial use and share-alike conditions where applicable, remains attached to material derived from those sources. Third-party portions are excluded from the project's MIT grant.
- `references/item-descriptions.json` stores extracted descriptions with per-item `source_url` and `as_of` attribution. `references/item-contracts.json` combines these descriptions with this project's structured annotations. `references/catalog-audit.json` and `references/catalog-index.md` organize item names and categories from the cited directories. Other reference documents retain links beside source-dependent assertions.
- Changes made here include extracting and formatting descriptions, organizing names and categories, adding Chinese mechanism annotations, and recording uncertainty and applicability. These are not unchanged copies of entire source pages. Preserve the source links and this notice when redistributing the third-party portions or adaptations.

## Path of Exile 2 / Grinding Gear Games

Path of Exile, Path of Exile 2, their game text and associated intellectual property belong to Grinding Gear Games and their respective rights holders. References identify game mechanics. This independent community project is not endorsed by Grinding Gear Games.

Official patch notes are linked from the relevant reference documents, including [0.5.0 notes](https://www.pathofexile.com/forum/view-thread/3932540). The repository's license does not grant rights to third-party game assets or trademarks.

## Other references and live providers

Reference documents link to PoE2Wiki, player posts and other sources for specific claims; a link is not a claim of ownership or a blanket license over those sources. Their applicable terms remain separate.

The price script fetches data from [poe.ninja](https://poe.ninja/docs/api) and [poecurrency.top](https://poecurrency.top/api.html). Provider data and service terms are independent of this code's MIT license. Live price snapshots are not committed. The small JSON files in `tests/fixtures/` are synthetic fixtures for local tests, not live market quotations.
