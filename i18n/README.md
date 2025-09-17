# ISTools Internationalization (i18n)

This directory contains translation files for the ISTools QGIS plugin.

## Available Languages

- **English (en)**: Default language
- **Portuguese Brazil (pt_BR)**: Brazilian Portuguese translation

## File Structure

- `*.ts` files: Translation source files (human-readable XML format)
- `*.qm` files: Compiled translation files (binary format used by Qt)
- `compile_translations.py`: Script to compile .ts files to .qm files

## Adding New Translations

### Method 1: Using Qt Linguist (Recommended)

1. Install Qt development tools that include Qt Linguist
2. Copy `istools_en.ts` to `istools_[language_code].ts`
3. Open the new file in Qt Linguist
4. Translate all strings
5. Save and release the file to generate the .qm file

### Method 2: Manual Editing

1. Copy `istools_en.ts` to `istools_[language_code].ts`
2. Edit the XML file manually:
   - Update the `language` attribute in the `<TS>` tag
   - Translate the content between `<translation>` tags
   - Keep the `<source>` tags unchanged
3. Compile using the compilation script or Qt tools

## Compiling Translations

### Using the Compilation Script

```bash
python compile_translations.py
```

This script will:
- Find all .ts files in the i18n directory
- Locate the Qt lrelease tool
- Compile each .ts file to its corresponding .qm file

### Manual Compilation

If you have Qt development tools installed:

```bash
lrelease istools_pt_BR.ts -qm istools_pt_BR.qm
lrelease istools_en.ts -qm istools_en.qm
```

## Language Codes

Use standard ISO language codes:
- `en` - English
- `pt_BR` - Portuguese (Brazil)
- `pt_PT` - Portuguese (Portugal)
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `zh_CN` - Chinese (Simplified)
- `ja` - Japanese

## How Translation Loading Works

1. The plugin detects the current QGIS locale using `QgsApplication.locale()`
2. It looks for a matching .qm file (e.g., `istools_pt_BR.qm` for Brazilian Portuguese)
3. If an exact match isn't found, it tries the base language (e.g., `istools_pt.qm` for `pt_BR`)
4. If no translation file is found, the plugin uses the default English strings

## Translation Context

Strings are organized by context (class names):
- `ISTools`: Main plugin class
- `ExtendLines`: Extend Lines tool
- `PolygonGenerator`: Polygon Generator tool
- `BoundedPolygonGenerator`: Bounded Polygon Generator tool
- `PointOnSurfaceGenerator`: Point on Surface Generator tool

## Testing Translations

1. Compile the translation files
2. Set QGIS to use the target language:
   - Go to Settings > Options > General
   - Change "User Interface Translation"
   - Restart QGIS
3. Load the ISTools plugin and verify the translations

## Contributing Translations

We welcome contributions for new language translations!

1. Create a new translation file following the naming convention
2. Translate all strings while keeping the context and meaning
3. Test the translation in QGIS
4. Submit a pull request with your translation file

## Notes

- Always keep the `<source>` tags in English - these are used as keys
- Only modify the content between `<translation>` tags
- Maintain consistent terminology throughout the translation
- Consider the context and UI space limitations when translating
- Test your translations in the actual QGIS interface