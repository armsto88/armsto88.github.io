# TA / SENSOR - BRAND KIT (v1.0)

A production-ready **vector recreation** of the approved SENSOR monogram concept. It follows the previous visual direction but is newly redrawn as scalable SVG paths, not a pixel-perfect vector trace of the concept image.

## What to use

- **Primary logo**: `01_Vector_Logos/ta-mark-olive-sage.svg` (two-tone).
- **Simple mark**: `01_Vector_Logos/ta-mark-olive.svg` (single olive).
- **Monochrome**: `ta-mark-black.svg`, `ta-mark-white.svg`, `ta-mark-charcoal.svg`.
- **Horizontal lockups**: eight SVG versions with your name, four including an ecology/engineering descriptor. The wordmark uses the Inter font or an OS sans-serif fallback.
- **Transparent PNG exports**: 512, 1024, and 2048px versions of each mark, plus wide lockups.
- **Favicons**: `03_Favicons/favicon.svg` and `favicon.ico`, individual PNG sizes, apple touch and Android Chrome icons. Favicon is a compact optical redraw so it stays clearer at small sizes.
- **Brand style guide**: `05_Brand_Guidelines/TA_Sensor_Brand_Style_Guide.pdf` (4 pages).
- **Web style system**: `04_Website_Assets/ta-brand.css` (light and dark modes), `design-tokens.json`, a standalone demonstration page `website-preview.html`, and `favicon-and-header-snippet.html`.
- **Social image**: `04_Website_Assets/social-preview-1200x630.png`.

## Core palette

| Role | Hex | Purpose |
| --- | --- | --- |
| Olive | #556241 | Main logo, links, primary buttons |
| Sage | #8A9A7B | Secondary stroke, quiet visual accents |
| Charcoal | #1F1F1F | Text and black-style monochrome |
| Off-white | #F6F7F2 | Page background |
| Dark olive | #35402D | Dark sections, hero accents |
| Pale sage | #E9EDE4 | Secondary surface |
| Border | #D7DED2 | Light dividers |
| Muted text | #657063 | Secondary readable text |

Inter is the recommended web font, with system sans-serif fallbacks. **No fonts are bundled.**

## Install on your website

1. Copy everything from `03_Favicons/` to your site's static `public/` folder.
2. Paste the favicon links from `04_Website_Assets/favicon-and-header-snippet.html` into your site's `<head>`.
3. Copy `04_Website_Assets/ta-brand.css` to `public/assets/` or your application's stylesheet directory and import it.
4. Copy `01_Vector_Logos/ta-mark-olive.svg` into your assets folder and use it as your navbar symbol.
5. Set `<html data-theme="dark">` to use the supplied dark-theme variables.
6. Open `04_Website_Assets/website-preview.html` locally to inspect website colours/components.
7. Make sure `site.webmanifest` icon paths point to the location you used.

## Logo handling

- Preserve the aspect ratio; never stretch the master SVG.
- Leave at least ~10% of the logo's height clear around it where possible.
- Prefer the full logo above ~120px display width. For 16px favicons use the **optically adjusted** favicon, not the full logo.
- Use the solid single-colour paths for PCB silkscreen, engraving and black-and-white printing.
- White reversed artwork is designed for dark backgrounds; it will be invisible on white.
- Raster previews are convenience exports. SVG files are the masters.

## Notes

This is an original **manual vector interpretation** of your approved concept for practical use. Any final formal brand registration / trademark clearance would require a separate similarity search.
