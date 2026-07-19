/**
 * All the words and details on the Contact page. Edit here, not in the Vue file.
 *
 * IMPORTANT: the email, phone and address below are placeholders. Replace them
 * with your real details before the site goes live — a contact page with a
 * fictional address is worse than none.
 */

export const hero = {
  eyebrow: 'Contact',
  title: 'Talk to us',
  lede:
    'Questions about a roast, a wholesale order, or an order that has gone ' +
    'astray — a real person reads every message.',
}

/**
 * Ways to reach you. `href` makes the card clickable:
 *   mailto:…   opens their email app
 *   tel:…      dials on a phone
 *   https://wa.me/91…  opens WhatsApp
 * Set href to null for a card that is information only (an address).
 */
export const channels = [
  {
    icon: '✉️',
    label: 'Email',
    value: 'hello@manero.in',
    href: 'mailto:hello@manero.in',
    note: 'We reply within one working day.',
  },
  {
    icon: '💬',
    label: 'WhatsApp',
    value: '+91 98765 43210',
    href: 'https://wa.me/919876543210',
    note: 'Quickest for order questions.',
  },
  {
    icon: '📞',
    label: 'Phone',
    value: '+91 98765 43210',
    href: 'tel:+919876543210',
    note: 'Mon–Sat, 10am–6pm IST.',
  },
  {
    icon: '📍',
    label: 'Roastery',
    value: '12 Brew Street, Indiranagar\nBengaluru 560038, Karnataka',
    href: null,
    note: 'Visits by appointment.',
  },
]

/** Options in the "What is this about?" dropdown. */
export const subjects = [
  { value: 'general', label: 'General question' },
  { value: 'order', label: 'About an order' },
  { value: 'wholesale', label: 'Wholesale / bulk' },
  { value: 'partnership', label: 'Partnership' },
  { value: 'feedback', label: 'Feedback' },
]

export const form = {
  title: 'Send us a message',
  intro: 'Fill this in and we will get back to you by email.',
  successTitle: 'Message received',
  successBody:
    'Thanks for getting in touch. We will reply to the email address you gave ' +
    'us, usually within one working day.',
}

/** Answers to the questions you get asked most. Keep them short. */
export const faqs = [
  {
    q: 'How fresh is the coffee when it arrives?',
    a:
      'We roast in small batches through the week and dispatch within 48 hours ' +
      'of roasting. The roast date is printed on every pack.',
  },
  {
    q: 'Which grind should I choose?',
    a:
      'Pick the one matching how you brew: Filter for a South Indian filter or ' +
      'pour-over, Espresso for a machine, Whole Bean if you grind at home, and ' +
      'Instant for freeze-dried. If in doubt, ask us.',
  },
  {
    q: 'How long does delivery take?',
    a:
      'Metros usually take 2–4 working days, the rest of India 4–7. You will ' +
      'get a tracking link by email once your order is dispatched.',
  },
  {
    q: 'Do you supply cafés and offices?',
    a:
      'Yes. We do 1kg and 5kg bags at wholesale rates, with a standing weekly ' +
      'roast if you need it. Choose "Wholesale / bulk" above and tell us your ' +
      'volume.',
  },
  {
    q: 'What if I do not like it?',
    a:
      'Tell us within 14 days and we will replace it with something better ' +
      'suited or refund you. Coffee is personal and we would rather find you ' +
      'the right bag than keep your money.',
  },
]
