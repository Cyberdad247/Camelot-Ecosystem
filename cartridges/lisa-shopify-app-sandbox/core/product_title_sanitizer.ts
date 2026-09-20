/**
 * LISA SHOPIFY KNIGHT — Clean Product Title Sanitizer
 * Transforms internal image picker and timestamp filenames into clean, minimal, luxury product names.
 */

export interface RawShopifyProduct {
  id: string;
  title: string;
  price: string;
  category?: string;
}

export interface CleanProduct {
  id: string;
  rawTitle: string;
  cleanTitle: string;
  category: 'Soul' | 'Sporty' | 'Premium' | 'Earrings' | 'Breast Cancer' | 'Signature';
  badge: string;
}

export function sanitizeProductTitle(rawTitle: string): CleanProduct {
  const lower = rawTitle.toLowerCase();

  let category: CleanProduct['category'] = 'Signature';
  let cleanTitle = 'Custom Hand-Woven Keychain';
  let badge = 'Handmade';

  if (lower.includes('earring') || lower.includes('dangle') || lower.includes('matching pair')) {
    category = 'Earrings';
    cleanTitle = 'Hand-Woven Dangle Earrings';
    badge = 'Earrings';
  } else if (lower.includes('soul')) {
    category = 'Soul';
    cleanTitle = 'The Signature Soul Weave';
    badge = 'Most Loved';
  } else if (lower.includes('sporty')) {
    category = 'Sporty';
    cleanTitle = 'Game Day Sporty Weave';
    badge = 'Sports Edition';
  } else if (lower.includes('premium')) {
    category = 'Premium';
    cleanTitle = 'Deluxe Charm & Beaded Keychain';
    badge = 'Deluxe';
  } else if (lower.includes('breast cancer')) {
    category = 'Breast Cancer';
    cleanTitle = 'Hope & Strength Ribbon Keychain';
    badge = 'Charity Edition';
  } else if (lower.includes('splashy')) {
    category = 'Signature';
    cleanTitle = 'Splashy Colorburst Keychain';
    badge = 'Vibrant';
  } else if (lower.includes('skull')) {
    category = 'Signature';
    cleanTitle = 'Edgy Skull Accent Keychain';
    badge = 'Custom Charm';
  }

  return {
    id: rawTitle,
    rawTitle,
    cleanTitle,
    category,
    badge
  };
}
