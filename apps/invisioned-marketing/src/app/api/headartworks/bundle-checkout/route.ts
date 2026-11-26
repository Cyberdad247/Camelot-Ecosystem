import { NextResponse } from "next/server";

export const runtime = "nodejs";

const VARIANT_CATALOG = {
  candles: {
    "Matte Obsidian Ceramic": "gid://shopify/ProductVariant/44910283720888",
    "Brushed Titanium Alloy": "gid://shopify/ProductVariant/44910283753656",
    "Luxora Gold Relic": "gid://shopify/ProductVariant/44910283786424",
  },
  bodySpray: "gid://shopify/ProductVariant/44910283819192",
  incenseCones: "gid://shopify/ProductVariant/44910283851960",
};

export async function POST(req: Request) {
  try {
    const body = await req.json().catch(() => ({}));
    const vessel = (body.vessel as keyof typeof VARIANT_CATALOG.candles) || "Matte Obsidian Ceramic";
    const candleVariantId = VARIANT_CATALOG.candles[vessel] || VARIANT_CATALOG.candles["Matte Obsidian Ceramic"];

    const cartInput = {
      lines: [
        {
          merchandiseId: candleVariantId,
          quantity: 1,
          attributes: [
            { key: "_bundle_id", value: "THE_HEAD_LIGHTS_EDIT" },
            { key: "_vessel_finish", value: vessel },
            { key: "_artisan_origin", value: "Cleveland, OH" },
          ],
        },
        {
          merchandiseId: VARIANT_CATALOG.bodySpray,
          quantity: 1,
          attributes: [
            { key: "_bundle_id", value: "THE_HEAD_LIGHTS_EDIT" },
            { key: "_product_role", value: "Atmospheric Body Spray" },
          ],
        },
        {
          merchandiseId: VARIANT_CATALOG.incenseCones,
          quantity: 1,
          attributes: [
            { key: "_bundle_id", value: "THE_HEAD_LIGHTS_EDIT" },
            { key: "_product_role", value: "Midnight Incense Cones" },
          ],
        },
      ],
      discountCodes: ["TRIAD_BUNDLE_15"],
      attributes: [
        { key: "Curated_By", value: "Lady Aurelia Ω (Sovereign Concierge)" },
        { key: "Studio_Source", value: "Head Artworks LLC (Cleveland, OH)" },
      ],
    };

    const storefrontEndpoint =
      process.env.HEADARTWORKS_SHOPIFY_ENDPOINT ||
      "https://headartwork.myshopify.com/api/2024-01/graphql.json";
    const publicToken = process.env.HEADARTWORKS_SHOPIFY_STOREFRONT_TOKEN;

    if (!publicToken) {
      return NextResponse.json(
        {
          status: "SIMULATED_CHECKOUT",
          bundle: "THE_HEAD_LIGHTS_EDIT",
          message:
            "HEADARTWORKS_SHOPIFY_STOREFRONT_TOKEN is not configured; returning offline bundle preview.",
          discountCodes: cartInput.discountCodes,
        },
        { status: 200 }
      );
    }

    try {
      const shopifyRes = await fetch(storefrontEndpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Shopify-Storefront-Access-Token": publicToken,
        },
        body: JSON.stringify({
          query: `
            mutation CreateHeadLightsEditCart($input: CartInput!) {
              cartCreate(input: $input) {
                cart {
                  id
                  checkoutUrl
                  totalQuantity
                  cost {
                    totalAmount { amount currencyCode }
                    subtotalAmount { amount currencyCode }
                  }
                }
              }
            }
          `,
          variables: { input: cartInput },
        }),
      });

      const shopifyJson = await shopifyRes.json();
      if (shopifyJson.data?.cartCreate?.cart) {
        const cart = shopifyJson.data.cartCreate.cart;
        return NextResponse.json({
          status: "SUCCESS",
          cartId: cart.id,
          checkoutUrl: cart.checkoutUrl,
          totalQuantity: cart.totalQuantity,
          cost: cart.cost,
          appliedDiscount: "TRIAD_BUNDLE_15 (15% Savings)",
        });
      }
    } catch (err) {
      console.warn("[Bundle Checkout Route]: Storefront API offline, fallback activated", err);
    }

    // Deterministic fallback response for offline testing
    return NextResponse.json({
      status: "ATOMIC_FALLBACK_ACTIVE",
      checkoutUrl: "https://headartwork.myshopify.com/cart?discount=TRIAD_BUNDLE_15",
      bundle: "THE_HEAD_LIGHTS_EDIT",
      vessel,
      subtotal: 78.0,
      appliedDiscount: "TRIAD_BUNDLE_15",
    });
  } catch (err) {
    return NextResponse.json(
      { error: "Failed to generate atomic bundle checkout" },
      { status: 500 }
    );
  }
}
