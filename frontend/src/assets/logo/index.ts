/**
 * Single import point for the brand mark.
 *
 * `manero-logo.jpg` is the Manero artwork cropped to its content — the original
 * square render carries ~20% black margin on every side, which would shrink the
 * mark to a fraction of the header height. `manero-logo.jpeg` is that untouched
 * original, kept as the source to re-crop from.
 *
 * TO REPLACE THE LOGO: overwrite `manero-logo.jpg` with your own file, keeping
 * the name. No code change needed; the header and footer both read from here.
 *
 * Two things to know about the JPEG format:
 *  - No transparency. The dark ground is baked in, which is why the header and
 *    footer are --espresso (#0d0b09) — the same colour as the artwork's
 *    background. Against any other colour the logo shows a visible rectangle.
 *  - Fixed resolution. 1041px wide covers the largest on-screen use comfortably,
 *    but it will not scale indefinitely the way a vector would.
 */
import logoUrl from './manero-logo.jpg'

export { logoUrl }

export const BRAND_NAME = 'Manero'
export const BRAND_TAGLINE = 'Small-batch coffee, roasted to order'
