<h1 align="center">Nox Aeterna</h1>

<p align="center"><em>Midnight-clad, lightning-wreathed. A classical gothic dark theme for Obsidian, inspired by the Night Lords.</em></p>

<p align="center">English · <a href="README.zh-CN.md">简体中文</a></p>

![Nox Aeterna in Obsidian: file explorer and local graph on the left, a note in reading view, calendar and outline on the right](docs/images/cover.webp)

## The look

Nox Aeterna (Latin for "eternal night") is inspired by the Night Lords, the VIII Legion of *Warhammer 40,000*, who came from Nostramo, a world that never saw the sun. Their armour is midnight blue, painted with lightning and hung with bone and bat wings. The theme borrows that heraldry and sets it out like an old printed book.

- **Palette.** Deep midnight-blue backgrounds, bone-white text, brass ornaments, crimson accents and pale lightning blue for interface frames. It never uses pure black or pure white.
- **Type.** Classical book typography. EB Garamond sets the text, Cinzel capitals the headings, and Noto Serif SC the Chinese. Empty tabs carry a blackletter epigraph.
- **Ornament.** Heraldic silhouettes in a few solid colours: a winged skull under the note title, a raised wing beside each H2, and a lightning-and-skull divider in place of the horizontal rule.
- **Dark Deco frames.** Thin double lines with bat-wing fan corners frame the sidebar panels, dialogs, the properties block and images. The structure is Art Deco; the motifs are gothic.
- **Atmosphere.** A faint mottled texture, a soft vignette and a fork of lightning at the foot of the file list. Each can be turned down or off.
- **Quiet where you read.** Ornament stays in headings, margins and frames. Body text is left plain, with a generous 1.85 line height.

**At a glance**

- Dark only. In light mode the theme still renders dark.
- Typography for both English and Simplified Chinese, with automatic CJK–Latin spacing and proper Chinese punctuation glyphs.
- The Style Settings page reads in English or Chinese.
- Works offline. Fonts, textures and icons are all embedded, and the theme makes no network requests.
- 34 Style Settings options. Most decorations can be switched off or swapped for Obsidian's own style.
- Built for the desktop app and tested on Obsidian 1.14 (Windows).

![Palette](docs/images/palette.webp)

## Gallery

All screenshots are taken in Obsidian 1.14 with the sample vault in [`demo-vault/`](demo-vault). Open that folder as a vault to try every style yourself.

### Notes

The note title sits over a winged skull. The properties block gets a brass double frame with its heading set into the top line. H1 has a centred rule with a small skull. Internal links are ember red, external links lightning blue, and highlights crimson.

![Title, properties, inline styles and H1](docs/images/note-title.webp)

H2 carries a raised crimson wing, and H3 a brass diamond. Blockquotes get a crimson bar. Nested lists use brass and hollow diamond bullets, and checked tasks are struck through behind a crimson box.

![H2, H3, blockquote, nested lists, ordered list and tasks](docs/images/note-lists.webp)

Tables have a dark header row in small capitals. H4 to H6 step down from lightning blue to muted italic.

![Table, H4, H5 and H6](docs/images/note-table.webp)

The horizontal rule is a lightning-and-skull divider. Code blocks sit on a darker panel with a crimson edge. Mermaid diagrams are recoloured to match, with night-blue boxes in bronze frames and crimson for start points and notes.

![Divider, code blocks, math and a Mermaid diagram](docs/images/note-code.webp)

Images are mounted on a dark mat inside the same bronze frame as the properties block. A night vignette or Obsidian's plain style can be chosen instead, and `|noframe` after an image leaves that one image plain. Embedded notes get a brass bar, and footnotes gather under a final divider.

![Image with caption, embedded note and footnotes](docs/images/note-media.webp)

Live preview keeps the same look while you edit.

![Live preview](docs/images/live.webp)

### Callouts

Each callout type has its own silhouette icon, from a quill for notes to a tarot moon for questions, claw slashes for warnings and a spider web for bugs.

![All callout types](docs/images/callouts.webp)

By default a callout looks like a patch of hide sewn onto the page: a running stitch in bone white just inside the edge, a stitched line under the title, and a small Latin label in bronze before the title (NOTA for notes, CAVE for warnings, QUAESTIO for questions, and so on). The stitching and the Latin labels can each be hidden.

### Sidebars and tabs

Each sidebar panel is a framed card, and the active sidebar tab flies a legion banner. The active tab in the main area has clipped corners and a crimson point, and a pinned tab shows a dagger. Card spacing is adjustable from 0 to 24 px.

![Sidebar cards, legion banner and tabs](docs/images/frames.webp)

On the left, the ribbon hangs as a chain of iron rings ending in a steel skull. Hovering a ring turns it crimson, and its tooltip carries a blood-red seal. On the right, the button row above each sidebar panel folds into a pair of bat wings and unfolds on hover. This works on the file explorer, outline, bookmarks, tags and backlinks panels; the search box stays usable.

<p align="center">
  <img src="docs/images/ribbon.webp" width="338" align="top" alt="Ribbon chain with a tooltip">
  &nbsp;&nbsp;
  <img src="docs/images/nav-wings.webp" width="278" align="top" alt="Sidebar buttons unfolding from bat wings">
</p>

The file explorer has three folder icon styles: a hanging bat that spreads its crimson wings when the folder opens, a bronze folder, or Obsidian's own arrow.

![Folder icon styles](docs/images/folders.webp)

In the outline, every heading is marked with a skull. As you hover a heading, a blood thread runs down to it from each of its parent headings. You can switch to a simple sliding marker or to Obsidian's own outline.

<p align="center"><img src="docs/images/outline-thread.webp" width="289" alt="Blood thread following the mouse in the outline"></p>

![Outline styles](docs/images/outline.webp)

### Dialogs and empty tabs

The command palette, settings and hover previews share the sidebar frame.

![Command palette and hover preview](docs/images/dialogs.webp)

<p align="center"><img src="docs/images/empty.webp" width="583" alt="Empty tab"></p>

### Auto-hide (optional)

All four of these are in Style Settings under *Interface*:

| Option | What it does |
|---|---|
| Auto-hide view header | The bar with back/forward buttons and the breadcrumb slides away. Hover the top edge of the note to bring it back. Works with the Editing Toolbar plugin in top mode. |
| Auto-hide ribbon | The ribbon slides out of the left window edge on hover and pushes the left sidebar aside instead of covering it. |
| Auto-hide vault switcher | The vault name row at the bottom of the left sidebar appears on hover. |
| Auto-collapse sidebar buttons | Folds sidebar button rows into bat wings, as shown above. On by default. |

## Installation

**From Obsidian:** go to *Settings → Appearance → Themes → Manage*, search for **Nox Aeterna**, then choose *Install and use*.

**Manually:** copy `theme.css` and `manifest.json` into `<your vault>/.obsidian/themes/Nox Aeterna/`, then select the theme in *Settings → Appearance*.

**Recommended:**

- Install the [Style Settings](https://github.com/mgmeyers/obsidian-style-settings) plugin. Every option lives there. Without it the theme runs on its defaults, except that sidebar button rows stay unfolded.
- Set *Settings → Appearance → Base color scheme* to **Dark**. Plugins such as Excalidraw choose their colours from it.

## Style Settings

At the top of the page, *Settings language* switches the page between English and Chinese, or follows Obsidian's own language. Defaults are shown in parentheses.

<p align="center"><img src="docs/images/settings.webp" width="640" alt="Style Settings page"></p>

| Group | Options |
|---|---|
| Atmosphere | Mottled texture and its strength (1) · Lightning under the file list and its brightness (0.45) · Vignette and its strength (0.62) |
| Ornaments | Winged skull under the title · Heading ornaments · Ornamental horizontal rule · Callout decoration · Callout Latin labels · Dark Deco card frames · Sidebar card spacing (8 px) · Themed or native callout icons · Folder icons (hanging bat / bronze folder / native) · Outline style (blood thread / marker / native) · Image style (bronze frame / night vignette / native) · Left-aligned H1 and note title |
| Interface | Auto-hide view header · Auto-hide ribbon · Auto-hide vault switcher · Auto-collapse sidebar buttons (on) |
| Typography | Chinese heading font (Noto Serif SC / Huiwen Mincho / STSong) · Body line height (1.85) · Body alignment (left / justify) · CJK–Latin auto spacing · Latin curly quotes · Sans-serif interface |
| Colours | Accent crimson `#b3262e` · Links `#e8705f` · Brass `#d2b07a` · Lightning blue `#9dbbe8` · Note background `#0b1424` |

## Fonts

| Role | Font |
|---|---|
| Body text (Latin) | EB Garamond, embedded |
| Headings (Latin) | Cinzel, embedded |
| Chinese | Noto Serif SC / Source Han Serif if installed. Otherwise an embedded subset of 6,763 common characters, with the system Song typeface for anything outside it |
| Chinese punctuation “ ” … — · | Glyphs from Noto Serif SC, so they never fall back to Latin forms |
| Empty-tab epigraph | Manufacturing Consent (Textura blackletter), embedded |

Huiwen Mincho can be chosen for Chinese headings, but you have to install it yourself.

## Compatibility

- **Obsidian version.** Built against the Obsidian 1.14 desktop app. Mobile has not been tested; the auto-hide options and the ribbon chain apply only on desktop.
- **Installer version.** A few effects depend on the Chromium version, which comes from your Obsidian *installer* rather than the app version (*Settings → About* shows it). The 1.12 installer ships Chromium 142 and gets everything. Older installers fall back as follows:
  - Below Chromium 125, the blood thread is drawn in segments, and the marker style shows a fixed line on the current heading instead of a sliding marker.
  - Settings dropdown options show in English only below Chromium 135.
  - The vault switcher snaps open instead of sliding below Chromium 129.
- **Mermaid.** Flowchart, sequence, class, state, ER, Gantt, pie, mind map and timeline diagrams are recoloured. Other diagram types keep Obsidian's inverted rendering, toned down so they no longer turn purple. Colours you set inside a diagram with `classDef` or `style` still take precedence.
- **Plugins.** The theme works with Style Settings and with Editing Toolbar's top mode. The calendar in the screenshots is the [Calendar](https://github.com/liamcain/obsidian-calendar-plugin) plugin.
- **File size.** `theme.css` is about 5 MB because the fonts, including the Chinese subset, are embedded. Community themes are not allowed to load fonts from the internet.

## Performance

Textures are pre-rendered images, never live SVG filters, and fixed backgrounds sit outside the scrolling layer. On Chromium at 125% display scaling, the file list scrolls at about 2.2 ms per frame, the same as the default theme, and a long note in reading view at about 2.4 ms per frame. The measurement scripts are in `tools/`.

## Credits

**Inspiration**

- [Fancy-a-Story](https://github.com/ElsaTam/obsidian-fancy-a-story): its Art Deco skin led to the Dark Deco frames and the sidebar banner.
- [Baseline](https://github.com/aaaaalexis/obsidian-baseline): its folding nav header led to the bat-wing button rows.
- [Maple](https://github.com/subframe7536/obsidian-theme-maple): its Logseq-style outline, after pengx17's bullet threading, is the basis of the blood thread.

**Artwork**

- [game-icons.net](https://game-icons.net) by Lorc, licensed CC BY 3.0:
  - the bat-wing outline (batwing-emblem);
  - the callout icons: quill, scroll-unfurled, semi-closed-eye, tied-scroll, candle-light, laurels, claw-slashes, crossed-bones, skull-crossed-bones, spider-web and open-book;
  - the pinned-tab dagger (stiletto).
- Heritage Library (HTC Heritage Type): a public-domain engraving, modified, for the outline skull.
- ICOOON MONO: the tarot card (modified) and the hollow profile skull (recoloured).
- Night Lords emblem: the community "wh_icons" set.
- The lightning, textures and remaining ornaments are drawn procedurally by the build scripts.
- Paintings in the sample vault, both public domain via Wikimedia Commons: Johan Christian Dahl, *View of Dresden by Moonlight* (1839), and Abraham-Louis-Rodolphe Ducros, *Night Storm at Cefalù* (c. 1800–1805).

**Fonts** (all under the SIL Open Font License 1.1)

- EB Garamond: Georg Duffner and Octavio Pardo.
- Cinzel: Natanael Gama.
- Manufacturing Consent: The Manufacturing Consent Project Authors.
- Noto Serif SC: Google and Adobe.

## Disclaimer

This is a fan work inspired by the Night Lords. *Warhammer 40,000*, the Night Lords and their emblem are trademarks of Games Workshop Ltd. The theme is unofficial and is not endorsed by or affiliated with Games Workshop.

## License

The theme code is covered by [LICENSE](LICENSE). Third-party artwork and fonts keep their own licenses, listed above.

Want to modify the theme? See [DEVELOPMENT.md](DEVELOPMENT.md) (in Chinese) for the source layout, the build and the implementation notes.
