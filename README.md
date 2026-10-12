# GBL Technologies — Website V2

A one-page redesign for GBL Technologies focused on a client-first conversion journey: earn attention, explain the cost of a weak first impression, show proof, present selected work, share client stories, and lead visitors into a project enquiry.

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
