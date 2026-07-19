/**
 * The four legal / policy pages, all driven from this one file.
 *
 * ⚠️  THIS IS PLACEHOLDER TEXT. It is written to look and read like a real
 * policy so the pages are not empty, but it has not been reviewed by a lawyer
 * and several details are invented (company name, address, GSTIN, timelines).
 *
 * Before you take real orders, replace every [SQUARE BRACKET] and have the
 * result checked by someone qualified. Indian e-commerce policies interact with
 * the Consumer Protection (E-Commerce) Rules 2020 and the DPDP Act 2023 — these
 * are not decorative documents.
 *
 * Structure: each policy has `title`, `updated`, optional `intro`, and a list of
 * `sections` ({ heading, body }). `body` is a list of paragraphs; a paragraph
 * starting with "- " renders as a bullet.
 */

export interface PolicySection {
  heading: string
  body: string[]
}

export interface Policy {
  slug: string
  title: string
  updated: string
  intro?: string
  sections: PolicySection[]
}

/** Shown on every policy page. Change these in one place. */
export const legalEntity = {
  name: '[Manero Coffee Private Limited]',
  address: '[12 Brew Street, Indiranagar, Bengaluru 560038, Karnataka, India]',
  email: 'hello@manero.in',
  phone: '+91 98765 43210',
  gstin: '[29AAAAA0000A1Z5]',
}

const LAST_UPDATED = '19 July 2026'

// ---------------------------------------------------------------- Terms ---

const terms: Policy = {
  slug: 'terms',
  title: 'Terms of Service',
  updated: LAST_UPDATED,
  intro:
    `These terms govern your use of this website and any order you place with ` +
    `${legalEntity.name} ("Manero", "we", "us"). By placing an order you accept them.`,
  sections: [
    {
      heading: '1. Who we are',
      body: [
        `${legalEntity.name}, registered at ${legalEntity.address}. ` +
          `GSTIN ${legalEntity.gstin}.`,
        `You can reach us at ${legalEntity.email} or ${legalEntity.phone}.`,
      ],
    },
    {
      heading: '2. Orders',
      body: [
        'An order is an offer to buy. It is accepted only when we confirm ' +
          'dispatch — not when payment is taken. If we cannot fulfil an order we ' +
          'will refund you in full.',
        'We may refuse or cancel an order where the item is unavailable, where ' +
          'a price or description was wrong, or where we suspect fraud.',
        'Prices shown include GST unless stated otherwise. Delivery charges are ' +
          'shown separately at checkout before you pay.',
      ],
    },
    {
      heading: '3. Pricing and payment',
      body: [
        'Payment is processed by our payment partner. We do not receive or store ' +
          'your card details.',
        'If a product is listed at an obviously incorrect price, we will contact ' +
          'you before dispatch and you may cancel for a full refund.',
      ],
    },
    {
      heading: '4. Product information',
      body: [
        'Coffee is an agricultural product. Flavour notes describe what we taste ' +
          'and are not a guarantee; harvest, roast date and your brewing method ' +
          'all affect the cup.',
        'Photographs are illustrative. Packaging may change.',
        '- Allergens: our roastery also handles [nuts, dairy]. If you have a ' +
          'severe allergy, contact us before ordering.',
      ],
    },
    {
      heading: '5. Your account and conduct',
      body: [
        'You are responsible for the accuracy of the delivery details you give us. ' +
          'We are not liable for orders lost because of an incorrect address.',
        'You may not resell our products commercially without a wholesale ' +
          'agreement, scrape this site, or interfere with its operation.',
      ],
    },
    {
      heading: '6. Liability',
      body: [
        'Nothing here limits liability for death or personal injury caused by ' +
          'negligence, or anything else that cannot be limited under Indian law.',
        'Subject to that, our total liability for any order is limited to the ' +
          'amount you paid for it.',
      ],
    },
    {
      heading: '7. Governing law',
      body: [
        'These terms are governed by the laws of India. Disputes are subject to ' +
          'the exclusive jurisdiction of the courts at [Bengaluru, Karnataka].',
      ],
    },
    {
      heading: '8. Changes',
      body: [
        'We may update these terms. The version in force is the one published ' +
          'here when you place your order.',
      ],
    },
  ],
}

// -------------------------------------------------------------- Privacy ---

const privacy: Policy = {
  slug: 'privacy',
  title: 'Privacy Policy',
  updated: LAST_UPDATED,
  intro:
    'This explains what personal data we collect, why, and what you can do ' +
    'about it. We collect as little as we can and we do not sell it.',
  sections: [
    {
      heading: '1. What we collect',
      body: [
        '- Order details: your name, email, phone number and delivery address.',
        '- Communications: anything you send us through the contact form or by email.',
        '- Technical data: pages visited and approximate location derived from ' +
          'your IP address, used to keep the site working.',
        'We do NOT collect or store card numbers. Payments are handled entirely ' +
          'by our payment partner.',
      ],
    },
    {
      heading: '2. Why we use it',
      body: [
        '- To take payment, pack your order and get it to you.',
        '- To answer your questions.',
        '- To meet tax and accounting obligations.',
        '- To send marketing email, but only if you have asked us to.',
      ],
    },
    {
      heading: '3. Who we share it with',
      body: [
        'Only those who need it to deliver your order:',
        '- Our payment partner, to process the transaction.',
        '- Our courier, to deliver the parcel.',
        '- Our accountants and, where legally required, government authorities.',
        'We do not sell your data, and we do not share it for anyone else\'s ' +
          'advertising.',
      ],
    },
    {
      heading: '4. How long we keep it',
      body: [
        'Order records are kept for [8] years to satisfy tax law. Contact ' +
          'messages are kept for [2] years. Marketing consent is kept until you ' +
          'withdraw it.',
      ],
    },
    {
      heading: '5. Your rights',
      body: [
        'Under the Digital Personal Data Protection Act 2023 you can ask us to:',
        '- Show you the personal data we hold about you.',
        '- Correct anything that is wrong.',
        '- Delete your data, where we are not legally required to keep it.',
        '- Withdraw consent for marketing at any time.',
        `Write to ${legalEntity.email} and we will respond within [30] days.`,
      ],
    },
    {
      heading: '6. Cookies',
      body: [
        'We use a small number of cookies that are necessary for the site to ' +
          'work — chiefly remembering what is in your basket. [If you add ' +
          'analytics or advertising cookies, you must say so here and obtain ' +
          'consent before setting them.]',
      ],
    },
    {
      heading: '7. Security',
      body: [
        'Data is transmitted over encrypted connections and access is limited to ' +
          'staff who need it. No system is perfectly secure; if a breach affects ' +
          'you we will tell you and the relevant authority without undue delay.',
      ],
    },
  ],
}

// ------------------------------------------------------------- Shipping ---

const shipping: Policy = {
  slug: 'shipping',
  title: 'Shipping Policy',
  updated: LAST_UPDATED,
  intro:
    'We roast to order, so dispatch takes a little longer than a warehouse — ' +
    'and the coffee arrives fresher because of it.',
  sections: [
    {
      heading: 'Dispatch time',
      body: [
        'Orders are roasted and dispatched within [48 hours], excluding Sundays ' +
          'and public holidays. Orders placed after [2pm] are processed the ' +
          'following working day.',
      ],
    },
    {
      heading: 'Delivery time',
      body: [
        '- Metros (Bengaluru, Mumbai, Delhi NCR, Chennai, Hyderabad, Pune, ' +
          'Kolkata): [2–4] working days.',
        '- Rest of India: [4–7] working days.',
        '- Remote and North-Eastern pin codes: up to [10] working days.',
        'These are estimates from dispatch, not from when you order.',
      ],
    },
    {
      heading: 'Charges',
      body: [
        'Flat [₹49] across India. Free on orders above [₹599].',
        'We currently ship only within India. [Remove this line if you begin ' +
          'shipping internationally.]',
      ],
    },
    {
      heading: 'Tracking',
      body: [
        'You will receive a tracking link by email when your parcel is ' +
          'dispatched. If it has not arrived within [7] working days of that ' +
          `email, contact us at ${legalEntity.email} and we will chase it.`,
      ],
    },
    {
      heading: 'Failed delivery',
      body: [
        'Couriers normally attempt delivery [three] times. If all attempts fail ' +
          'the parcel returns to us, and we will refund the order less the ' +
          'shipping cost.',
        'If the address you gave was incomplete or wrong, redelivery is chargeable.',
      ],
    },
    {
      heading: 'Damaged in transit',
      body: [
        'Tell us within [48 hours] of delivery with photographs of the parcel and ' +
          'contents, and we will replace it at no cost.',
      ],
    },
  ],
}

// --------------------------------------------------- Cancellation/Refund ---

const refunds: Policy = {
  slug: 'refunds',
  title: 'Cancellation & Refund Policy',
  updated: LAST_UPDATED,
  intro:
    'Coffee is personal. If what arrived is not right for you, tell us — we ' +
    'would rather find you a bag you like than keep your money.',
  sections: [
    {
      heading: 'Cancelling an order',
      body: [
        'You can cancel free of charge any time before dispatch. Email ' +
          `${legalEntity.email} with your order number.`,
        'Once roasted and dispatched an order cannot be cancelled, but you can ' +
          'return it under the section below.',
      ],
    },
    {
      heading: 'Returns',
      body: [
        'Because coffee is a consumable, we accept returns only where:',
        '- The item arrived damaged, or',
        '- We sent the wrong item, or',
        '- The coffee is faulty — stale, contaminated, or past its date.',
        'Tell us within [14 days] of delivery at ' +
          `${legalEntity.email}, with your order number and a photograph.`,
        'We do not accept returns simply because a flavour was not to taste — ' +
          'but do tell us anyway, because we will usually make it right.',
      ],
    },
    {
      heading: 'Refunds',
      body: [
        'Approved refunds are issued to the original payment method within ' +
          '[5–7] working days of approval. Your bank may take a few days more ' +
          'to show it.',
        'Where a replacement is preferred we will dispatch it with the next roast.',
      ],
    },
    {
      heading: 'Cancelled by us',
      body: [
        'If we cancel an order — because of stock, a pricing error, or a delivery ' +
          'problem — you receive a full refund including shipping, with no ' +
          'deduction.',
      ],
    },
    {
      heading: 'How to reach us',
      body: [
        `Email ${legalEntity.email} or call ${legalEntity.phone}, [Mon–Sat, ` +
          '10am–6pm IST]. Have your order number ready.',
      ],
    },
  ],
}

export const policies: Policy[] = [terms, privacy, shipping, refunds]

export const policyBySlug = (slug: string): Policy | undefined =>
  policies.find((p) => p.slug === slug)
