/**
 * All the words on the Our Story page live here, so you can rewrite them
 * without touching any Vue markup. Change a string, save, done.
 *
 * This is placeholder copy written to fit the layout — replace it with the real
 * Manero story when you have it. Keep the lengths roughly similar and the
 * design will hold up.
 */

export const hero = {
  eyebrow: 'Our story',
  title: 'We got tired of\nbad coffee at home.',
  lede:
    'Manero began with a simple frustration: brilliant coffee grows a few hours ' +
    'from where we live, yet most of it leaves the country, and what stays on the ' +
    'shelf is stale by the time it reaches a cup.',
}

/** The founder narrative. Two or three paragraphs reads best. */
export const origin = {
  title: 'It started on an estate in Chikmagalur',
  paragraphs: [
    'We were standing in a drying yard at 6am, watching a farmer turn parchment ' +
      'coffee by hand. He had been growing Arabica for thirty years. He had never ' +
      'tasted his own beans properly roasted.',
    'That felt wrong. The coffee was extraordinary — floral, sweet, nothing like ' +
      'the bitter instant most of us grew up on. It was going into a shipping ' +
      'container bound for Europe, where someone would put their name on it.',
    'So we started buying small lots directly, roasting them in batches we could ' +
      'actually taste, and shipping them within 48 hours. No warehouse. No middle ' +
      'men. Just coffee that still tastes like the place it came from.',
  ],
  pullQuote: 'Coffee should taste like where it grew, not like how long it sat.',
  image:
    'https://images.unsplash.com/photo-1524350876685-274059332603?auto=format&fit=crop&w=1000&q=80',
  imageAlt: 'Coffee cherries drying in the sun on an estate',
}

/** Three short differentiators. Icons are plain emoji — swap freely. */
export const values = [
  {
    icon: '🌱',
    title: 'Bought direct',
    body:
      'We buy from estates we have walked, at prices we are not embarrassed to ' +
      'publish. Every bag names the farm it came from.',
  },
  {
    icon: '🔥',
    title: 'Roasted to order',
    body:
      'Nothing sits in a warehouse. We roast in small batches through the week ' +
      'and ship within 48 hours, so it reaches you close to peak.',
  },
  {
    icon: '⚖️',
    title: 'Ground for how you brew',
    body:
      'Filter, espresso, French press, or instant — tell us how you make it and ' +
      'we grind for that, instead of one compromise for everyone.',
  },
]

/** The farm-to-cup journey. Four steps fits the layout best. */
export const process = [
  {
    step: '01',
    title: 'Picked ripe',
    body:
      'Selective hand-picking, cherry by cherry. Slower and more expensive than ' +
      'stripping a branch, and the only way to keep unripe fruit out of the cup.',
  },
  {
    step: '02',
    title: 'Rested and sorted',
    body:
      'Sun-dried on raised beds, then rested in parchment for six weeks so the ' +
      'moisture evens out and the sweetness settles.',
  },
  {
    step: '03',
    title: 'Roasted in small batches',
    body:
      'Twelve kilos at a time. Every batch is cupped before it is approved, and ' +
      'anything that misses the profile is not sold.',
  },
  {
    step: '04',
    title: 'Shipped within 48 hours',
    body:
      'Packed in one-way valve bags the day after roasting, with the roast date ' +
      'printed on every pack. No stock sitting in a warehouse.',
  },
]

/** Small credibility numbers. Keep to three or four. */
export const stats = [
  { value: '6', label: 'partner estates' },
  { value: '48hrs', label: 'roast to dispatch' },
  { value: '1,600m', label: 'highest elevation' },
  { value: '100%', label: 'traceable to farm' },
]

/** What the brand commits to beyond selling coffee. */
export const commitments = {
  title: 'What we owe the people who grow it',
  intro:
    'Coffee has a long history of paying the least to the people doing the most ' +
    'work. We are a small company and cannot fix that, but we can refuse to be ' +
    'part of it.',
  items: [
    {
      title: 'Above-market prices, published',
      body:
        'We pay a premium over the local commodity rate and print what we paid ' +
        'on the estate pages. If we ever stop, you will be able to see it.',
    },
    {
      title: 'Multi-year commitments',
      body:
        'We buy from the same farms year after year, including in bad harvests. ' +
        'A one-season buyer is not a partner.',
    },
    {
      title: '1% to picker education',
      body:
        'One percent of revenue funds schooling for the children of seasonal ' +
        'pickers, who move between estates and lose school years to it.',
    },
  ],
}

export const closing = {
  title: 'Come taste the difference',
  body:
    'Start with the Signature Arabica if you want somewhere to begin. If you ' +
    'would rather we picked for you, tell us how you brew and we will suggest one.',
  primaryLabel: 'Shop the coffee',
  secondaryLabel: 'Ask us anything',
}
