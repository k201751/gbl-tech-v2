# Point Zero — Website Draft

A one-page redesign for Point Zero focused on a client-first conversion journey: earn attention, explain the cost of a weak first impression, show proof, present selected work, share client stories, and lead visitors into a project enquiry.

## Live website

**[View the deployed website](https://k201751.github.io/gbl-tech-v2/)**

The production site is hosted with GitHub Pages from the `main` branch.

## Design direction

- Editorial black-and-white foundation with restrained powder-blue accents
- Large serif display typography paired with a clean sans-serif interface
- Exact GBL wordmark treatment used by the current company website
- Spacious, page-like sections with scroll-driven expansion
- Full-width project cards that stack and open as the visitor scrolls
- Responsive layouts for desktop, tablet, and mobile

## Main interactions

- Cinematic hero sequence with timed messaging and a persistent final animation
- Scroll progress indicator and context-aware navigation styling
- Animated `60+` proof counter
- Scroll-stacked selected-work cards
- Video testimonials that play on hover or tap
- Optional testimonial audio with a visible sound-state control
- Automatically advancing testimonial carousel that pauses during interaction
- Continuously moving written-testimonial rail
- Contact form that prepares a project-enquiry email
- Reduced-motion support through `prefers-reduced-motion`

## Local preview

No build step or package installation is required. Run any static file server from the project directory.

Using Python:

```powershell
cd D:\Dev-Projects\gbl-tech-v2
python -m http.server 4175
```

Then open [http://127.0.0.1:4175/](http://127.0.0.1:4175/).

## Project structure

```text
index.html   Page content and semantic structure
styles.css   Responsive design, layout, and motion
script.js    Hero, scroll, navigation, testimonial, and form behavior
assets/      Local fonts, project artwork, posters, and video files
```

## External resources

- `Inter` and `Newsreader` are loaded from Google Fonts.
- Three testimonial videos are served from the official GBL Technologies website; the remaining testimonial videos are stored locally in `assets/`.
- Selected-work cards link to their corresponding case studies on [gbltechnologies.com](https://gbltechnologies.com/).

## Deployment

GitHub Pages serves the repository root from `main`. Pushing an update to `main` publishes it to the live URL after GitHub completes the Pages deployment.


## Point Zero adaptation

- Uses the supplied Point Zero light and dark PNG logos, switching with the header surface.
- Mirrors the revamp navigation: Why it matters, Selected work, Case studies, Services, Contact us, Reviews, and Get a quote.
- Dropdowns share the header background and foreground colors and support click, keyboard, Escape, and outside-click dismissal. Mobile navigation scrolls independently.
- Contact and quote links remain on the homepage. Email and prepared enquiries use info@point0.com, matching the revamp.
- Separate pages now exist at case-studies/ and web-development/, with individual pages in case-study/ and service/. Menus and project cards link to those pages. New layouts use existing project artwork without copying revamp inner pages. Contact links return to index.html#contact.
- Legacy gbltechnologies.com URLs remain only as sources for existing testimonial media.
- JavaScript syntax and local navigation checked. Website Design and Chef Silvia pages verified in the browser at desktop and 390px mobile widths, including scroll reveals, section expansion and FAQ interaction.


Inner pages share inner.css and inner.js. work/build-pages.cjs generates their HTML from the homepage navigation and project metadata. The service details and case-study narratives now use the matching public revamp pages, archived in work/revamp-source/. work/source-content.cjs sanitizes and adapts the content into our editorial layouts. inner-motion.js applies homepage-style section expansion, reveals and reduced-motion support.
