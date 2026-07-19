/**
 * Statutory business identifiers, shown in the footer and on the policy pages.
 *
 * ⚠️  EVERY VALUE BELOW IS A PLACEHOLDER. Replace them with your real
 * registrations before the site goes live.
 *
 * Displaying a fabricated FSSAI licence number on a site selling food is not a
 * cosmetic problem — it is a false statement about a food-safety registration,
 * and FSSAI display requirements are enforced. If you do not have a number yet,
 * set it to an empty string: the row then hides itself rather than showing
 * something invented.
 *
 * What each one is:
 *   FSSAI  14-digit licence from the Food Safety and Standards Authority of
 *          India. Mandatory for anyone manufacturing, packing or selling food,
 *          and must be displayed on the website and on every package.
 *   GSTIN  15-character Goods and Services Tax identification number.
 *   MSME   Udyam Registration Number, format UDYAM-XX-00-0000000. Optional —
 *          it signals a registered small business but is not compulsory.
 *   CIN    Corporate Identification Number, if you are a registered company.
 */

export const business = {
  legalName: '[Manero Coffee Private Limited]',
  tradeName: 'Manero',

  address: {
    line1: '[12 Brew Street, Indiranagar]',
    line2: '[Bengaluru 560038, Karnataka, India]',
  },

  email: 'hello@manero.in',
  phone: '+91 98765 43210',

  // Set any of these to '' to hide that row entirely.
  fssai: '[10012345678901]',
  gstin: '[29AAAAA0000A1Z5]',
  msme: '[UDYAM-KA-03-0000000]',
  cin: '[U15200KA2026PTC000000]',
}

/** Only the identifiers that have been filled in, ready to render. */
export const identifiers = [
  { label: 'FSSAI Licence', value: business.fssai },
  { label: 'GSTIN', value: business.gstin },
  { label: 'Udyam (MSME)', value: business.msme },
  { label: 'CIN', value: business.cin },
].filter((row) => row.value)
