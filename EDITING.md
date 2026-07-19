# Editing guide

How to change the things you'll most often want to change, without needing to understand
the whole codebase. Every path is relative to the project root.

After editing any frontend file, the dev server (`npm run dev`) reloads the page
automatically — you don't need to restart anything.

---

## 0. The admin panel — the easiest way to change products

There is now a staff area at **<http://localhost:5173/admin>** where you can add,
edit, hide and delete products without touching any code. Prices are entered in
rupees; the conversion to paise happens for you.

**Create your account first** (one time, on the machine running the backend):

```bash
cd backend
.venv/Scripts/python -m app.cli create-admin      # Windows
.venv/bin/python -m app.cli create-admin          # Linux/macOS
```

It asks for an email and password at a prompt. The password is never passed as
a command argument, because arguments end up in your shell history.

Other commands: `list-admins`, `reset-password`, `deactivate-admin`.

### Hide vs Delete

- **Hide** — the product disappears from the shop but stays in the database, and
  past orders that reference it remain intact. Reversible with **Restore**.
- **Delete** — permanent. Refused outright for any product that appears in a past
  order, because removing it would rewrite what those orders say was bought.

Use Hide for anything you have ever sold. Delete is for mistakes.

> The sections below still apply — the seed file is useful for bulk changes, and
> everything else on the site is edited in code.

---

## 1. The logo

**File:** `frontend/src/assets/logo/manero-logo.jpg`

Overwrite that file with your own image, keeping the **same filename**. Nothing else to
change — the header and footer both read from it.

Two constraints, because it's a JPEG:

- **The background must be near-black (`#0d0b09`).** JPEG has no transparency, so the
  background is baked into the image. If yours is a different shade, it shows as a
  visible rectangle against the header. (`manero-logo.jpeg` in the same folder is your
  original artwork, kept as a backup to re-derive from.)
- **Crop out empty margins.** Your original was square with wide black borders; at header
  size the mark would shrink to a fraction of the space. The version in use is cropped
  tight to the artwork.

To change the displayed size: `frontend/src/components/AppHeader.vue` (`.logo { height }`)
and `AppFooter.vue`.

---

## 2. Product photos, names, prices, descriptions

Products live in the **database**, not in the frontend. They're loaded from a seed file:

**File:** `backend/app/seeds/seed_products.py`

Each product is a block in the `PRODUCTS` list:

```python
{
    "slug": "instant-hazelnut",              # URL: /shop/instant-hazelnut
    "name": "Instant Hazelnut",              # shown on the card and page
    "description": "Roasted hazelnut ...",   # the "About this coffee" paragraph
    "bean_type": BeanType.ARABICA,           # filter: Arabica / Robusta / Blend
    "roast_level": RoastLevel.MEDIUM,        # filter: Light / Medium / Dark
    "grind": Grind.INSTANT,                  # filter: Whole Bean / Filter / Espresso / Instant
    "flavour": Flavour.HAZELNUT,             # filter: Original / Hazelnut / Vanilla / Caramel / Mocha
    "origin": "Blended & freeze-dried in India",
    "tasting_notes": "Toasted hazelnut, cream, cocoa",
    "image": "1572442388796-11668a67e53d",   # see below
    "bestseller": True,                      # shows on the homepage
    "variants": [(50, 27900, 32900), (100, 49900, None)],
},
```

### Prices

**Prices are in paise, not rupees.** ₹279.00 is written `27900`. This is deliberate —
storing money as whole numbers avoids the rounding errors you get with decimals.

Each variant is `(size_in_grams, price, was_price)`:

- `(250, 44900, 49900)` → 250g, ₹449.00, was ₹499.00 → shows a **10% off** badge
- `(500, 84900, None)`  → 500g, ₹849.00, no discount badge

The discount percentage is calculated for you; don't write it anywhere.

### Photos

The `"image"` field currently holds an Unsplash photo ID (placeholder stock photography).
To use your own product photos, replace that whole field with a full URL:

```python
"image_url_full": "https://your-cdn.com/photos/hazelnut.jpg",
```

...and in the same file change the line that builds the URL:

```python
product.image_url = IMG.format(id=spec["image"])
```

to:

```python
product.image_url = spec["image_url_full"]
```

If you'd rather host images inside the project: put them in `frontend/public/products/`
and use `"/products/hazelnut.jpg"` as the URL.

### Applying your changes

Re-run the seed script from the `backend` folder:

```
.venv\Scripts\python -m app.seeds.seed_products
```

(The database must be running — see "Database" in `README.md` if you get a connection
error.)

It matches products by `slug` and updates them in place, so running it repeatedly is
safe — it won't create duplicates. Refresh the browser to see the changes.

> Adding a product? Copy an existing block and give it a **new, unique `slug`**.
> Deleting one? Removing it from this file does *not* delete it from the database —
> set `is_active` to `False` instead, or delete the row directly.

---

## 3. Our Story and Contact page content

Every word on these two pages lives in plain data files — no Vue markup to touch.

| Page | File |
| --- | --- |
| Our Story (`/story`) | `frontend/src/content/story.ts` |
| Contact (`/contact`) | `frontend/src/content/contact.ts` |

Open either, change the strings, save. The page reloads instantly.

### `story.ts`

- `hero` — the headline and opening paragraph. The `\n` in the title is where the
  headline breaks onto a second line; move it or remove it.
- `origin` — the founder narrative: `paragraphs` is a list, so add or remove
  entries freely. `pullQuote` is the large italic line. `image` takes any URL.
- `values` — the three "how we do it differently" cards. Icons are plain emoji.
- `process` — the four farm-to-cup steps.
- `stats` — the four numbers on the dark strip.
- `commitments` — the social-responsibility section.
- `closing` — the final call to action.

**The copy currently in there is placeholder** — written to fit the layout, not
true. Replace it with the real Manero story. Keep each piece roughly the same
length and the design will hold.

### `contact.ts`

- `channels` — email, WhatsApp, phone, address. Set `href` to make a card
  clickable (`mailto:`, `tel:`, `https://wa.me/…`) or `null` for display only.
- `subjects` — the options in the "What is this about?" dropdown.
- `faqs` — the accordion. Add or remove entries; the first is open by default.

> **Replace the placeholder contact details before going live.** The email,
> phone number and address in there are invented. A contact page with a
> fictional address is worse than no contact page.

### Where the messages go

The contact form is real — submissions are stored in the database, not emailed
(there is no mail provider wired up yet). Read them with:

```bash
./db.sh "SELECT created_at, name, email, subject, message FROM contact_messages WHERE NOT handled ORDER BY id DESC"
```

Mark one as dealt with so it drops out of that list:

```bash
./db.sh "UPDATE contact_messages SET handled = true WHERE id = 1"
```

**Check this regularly** — nothing notifies you when a message arrives.

---

## 4. Homepage text

**File:** `frontend/src/views/HomeView.vue`

Near the top you'll find the editable content as plain lists:

- `categories` — the four cards under the hero (label, blurb, and where they link)
- `promises` — the three icon boxes near the bottom (icon, title, copy)

The hero headline, sub-heading and button labels are in the `<template>` block just
below — search for `Coffee worth` and edit the text directly.

---

## 5. Header and footer links

- **Header menu:** `frontend/src/components/AppHeader.vue` → the `links` list
- **Footer columns:** `frontend/src/components/AppFooter.vue` → the `columns` list

Both use the same shape: `{ to: '/shop?grind=filter', label: 'Filter Coffee' }`. The `to`
value is any URL on the site — filter links are just the shop page with a query string,
so `?bean_type=arabica` or `?roast_level=dark` work as menu items.

---

## 6. Brand name and tagline

**File:** `frontend/src/assets/logo/index.ts`

```ts
export const BRAND_NAME = 'Manero'
export const BRAND_TAGLINE = 'Small-batch coffee, roasted to order'
```

Used in the footer, the payment dialog, and accessibility labels.

The browser tab title and search-engine description are in `frontend/index.html`.

---

## 7. Colours

**File:** `frontend/src/style.css` — the `:root` block at the very top.

```css
--espresso:    #0d0b09;   /* header, footer, hero background */
--gold:        #d4af37;   /* buttons, badges, accents */
--gold-light:  #f0d98a;   /* hover states, headings on dark */
--foam:        #faf7f2;   /* page background */
--paper:       #ffffff;   /* cards, panels */
--ink:         #17120e;   /* body text */
--ink-soft:    #6b5f52;   /* secondary text */
--accent:      #b8860b;   /* links, primary buttons */
```

Changing these restyles the entire site. **One catch:** `--espresso` must stay matched to
the logo's baked-in background. If you change it, the logo will show a rectangle — you'd
need to re-edit the image to match.

---

## 8. Shipping cost and free-shipping threshold

**File:** `backend/.env`

```
SHIPPING_FEE_PAISE=4900              # ₹49.00 flat rate
FREE_SHIPPING_THRESHOLD_PAISE=59900  # free above ₹599.00
```

Again in paise. Restart the backend after changing these.

The "Free shipping over ₹599" text on the homepage is separate marketing copy in
`HomeView.vue` — update it to match if you change the threshold.

---

## 9. Payment gateway

**File:** `backend/.env`

```
PAYMENT_PROVIDER=dummy    # or: razorpay
```

`dummy` needs no account and shows a simulated payment dialog. See the Payments section
of `README.md` for switching to real Razorpay.

---

## Quick reference

| I want to change... | File |
| --- | --- |
| Logo | `frontend/src/assets/logo/manero-logo.jpg` |
| Product names, prices, photos | `backend/app/seeds/seed_products.py` (then re-run the seed) |
| Our Story page copy | `frontend/src/content/story.ts` |
| Contact details, FAQs | `frontend/src/content/contact.ts` |
| Reading contact form messages | `./db.sh "SELECT * FROM contact_messages WHERE NOT handled"` |
| Homepage sections and copy | `frontend/src/views/HomeView.vue` |
| Menu / footer links | `AppHeader.vue` / `AppFooter.vue` |
| Brand name, tagline | `frontend/src/assets/logo/index.ts` |
| Tab title, meta description | `frontend/index.html` |
| Colours | `frontend/src/style.css` (`:root`) |
| Shipping cost, payment gateway | `backend/.env` |
