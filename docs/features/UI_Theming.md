# UI Theming & Branding

**Deliverable:** P3-1.1 — Themed InvenioRDM instance (minor UI "look and feel" customisation)
**Phase:** 3 (January 2026)
**Date:** March 2026
**Status:** Implemented

---

## Overview

The InvenioRDM instance has been branded and themed for the Turath project. All visual customisations are implemented as InvenioRDM template overrides and Semantic UI LESS variable overrides, following InvenioRDM's recommended extension pattern — no core framework files are modified.

---

## Branding Assets

Custom brand assets are served as static files:

```
site/turath_inveniordm/static/images/
├── Turath Logo with Tagline for Homepage.png   ← full logo for homepage sidebar
├── Tagline Alone for Invenio Pages.png          ← tagline strip for header
├── Logo Alone for Invenio Pages.png             ← logo mark for header
├── carousel-1.png                               ← homepage carousel slide 1
├── carousel-2.png                               ← homepage carousel slide 2
├── carousel-3.png                               ← homepage carousel slide 3
└── carousel-4.png                               ← homepage carousel slide 4
```

---

## Custom Homepage

The default InvenioRDM frontpage has been replaced with a bespoke Turath homepage (`templates/semantic-ui/invenio_app_rdm/frontpage.html`) featuring:

- **Sidebar layout** — left panel with the Turath logo, dual-mode search form (Metadata / Full-text toggle), and collection navigation links
- **Main content area** — carousel of manuscript images on the right
- **Bilingual** — search placeholder reads "Search بالعربي or in English"
- **Collection navigation** — quick links to Arabian Chronicles, Newspapers and Magazines, Hajj collection, Oral Histories

### Structure

```html
<div class="turath-homepage">
  <aside class="turath-homepage-sidebar">
    <!-- Logo, search form, collection nav -->
  </aside>
  <main class="turath-homepage-main-content">
    <!-- Carousel of manuscript images -->
  </main>
</div>
```

---

## Custom Header (All Pages)

The default InvenioRDM header has been replaced (`templates/semantic-ui/invenio_app_rdm/header.html`) with a Turath-branded header containing:

- **Turath logo + tagline** on the left
- **Search bar** in the centre (using the custom `TurathHeaderSearchBar` React component)
- Two-row layout with sufficient whitespace for the Arabic/English logo treatment

---

## CSS Customisation

All custom styles are defined in `assets/less/site/globals/site.overrides` using Semantic UI LESS variables:

### Key Style Variables

```less
@turath-left-column-width: 380px;
@turath-record-sidebar-width: 400px;
```

### Selected Custom Styles

| Element | Customisation |
|---------|--------------|
| `.turath-branding` | Flex layout for logo + tagline side-by-side |
| `.turath-branding-logo` | Max height 70px, object-fit: contain |
| `.turath-branding-tagline` | Max height 55px, max-width 160px |
| `.turath-homepage` | Full-viewport flex layout, no scroll |
| `.turath-homepage-sidebar` | 350px fixed width, background `#e5eae7` |
| `.turath-homepage-main-content` | Remaining width, carousel display |

---

## React Component Overrides

The search interface components are overridden via InvenioRDM's overridable registry:

| Component | File | Customisation |
|-----------|------|--------------|
| Search result item | `TurathResultsListItem.js` | Shows HOCR highlight snippets below each result |
| Search result card | `TurathResultsListItemCard.js` | Compact card view for grid layout |
| Header search bar | `TurathHeaderSearchBar.js` | Dual-mode (metadata/fulltext) search input |
| Main search bar | `TurathSearchBar.js` | Homepage search with mode toggle |

---

## InvenioRDM Theming Pattern

All overrides follow the standard InvenioRDM approach — no core files modified:

1. **Template overrides** live in `site/turath_inveniordm/templates/semantic-ui/`
2. **Static assets** live in `site/turath_inveniordm/static/`
3. **CSS overrides** live in `assets/less/site/globals/site.overrides`
4. **React component overrides** live in `site/turath_inveniordm/assets/semantic-ui/js/`

This means upgrading InvenioRDM to a future version will not overwrite these customisations.
