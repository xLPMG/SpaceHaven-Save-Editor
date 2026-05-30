# UI Translations

This directory holds Qt Linguist translation files for the app's **UI strings**.

> **Note:** Game content strings (item names, trait names, backstories, etc.) are
> translated via the game's own `data/library/texts` file and the `game_texts`
> system in `src/texts_loader.py`.  Only this app's own labels, buttons, and
> menus live here.

## How translations work

The app uses Qt's standard `self.tr("string")` / `QTranslator` pipeline.

- Source strings are in **English** (the `self.tr(...)` call sites in the Python
  source files under `src/ui/`).
- Compiled `.qm` files are loaded at runtime when the user switches language.

## Adding a new translation

### 1. Extract source strings

```bash
pyside6-lupdate src/ui/*.py -ts translations/spacehaven_DE.ts
```

Replace `DE` with the appropriate language code (must match the codes in
`game_texts.LANG_DISPLAY`: `EN`, `DE`, `ES`, `FR`, `IT`, `PL`, `CS`, `RU`,
`PTBR`, `KO`, `JA`, `CN`, `TR`).

### 2. Translate

Open the `.ts` file in **Qt Linguist** (`linguist translations/spacehaven_DE.ts`)
and fill in the translations.

### 3. Compile

```bash
lrelease translations/spacehaven_DE.ts
```

This produces `translations/spacehaven_DE.qm` which the app will load
automatically when the user selects that language.

## File naming

`spacehaven_{LANG_CODE}.qm` — e.g. `spacehaven_DE.qm`, `spacehaven_FR.qm`.

The code in `MainWindow._install_translator()` constructs this path at runtime.
