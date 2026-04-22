# SKILL BIBLE — Next.js 15+ (App Router)
# Knight: Sir Syntax | Layer: L2_KINETIC | v400.1.0
# LOAD: NEXT_MODERN — instilled on Next.js/React/TypeScript/UI tasks

## STACK
- **Next.js**: 15+ App Router (`app/` directory)
- **Language**: TypeScript strict mode (`tsc --strict` mandatory)
- **Styling**: Tailwind CSS exclusively — custom CSS forbidden except `globals.css`
- **State**: Supabase (no local state management libraries)
- **Auth**: NextAuth.js v5
- **Validation**: Zod schemas at all boundaries
- **DB**: Prisma ORM
- **Package manager**: pnpm
- **Bundler**: Turbopack (dev), standard Next.js (prod)
- **Deployment**: Vercel
- **E2E Testing**: Playwright

## CONVENTIONS — App Router
```typescript
// Correct: Server Component (default)
export default async function Page({ params }: { params: { id: string } }) {
  const data = await fetchData(params.id); // direct async, no useEffect
  return <Component data={data} />;
}

// Correct: Server Action
"use server";
export async function updateItem(formData: FormData) {
  const validated = ItemSchema.parse(Object.fromEntries(formData));
  await db.item.update({ where: { id: validated.id }, data: validated });
  revalidatePath("/items");
}

// Correct: Route Handler
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  return Response.json(await getItems(searchParams));
}
```

## PATTERNS
- Server Components by default — only add `"use client"` when browser APIs needed
- Streaming with `<Suspense>` boundaries for async data
- Parallel routes (`@slot`) for dashboard layouts
- Metadata API (`generateMetadata`) for SEO — never raw `<head>`
- Partial Prerendering (PPR) for static shell + dynamic content

## ANTI-PATTERNS (Sir Gideon will STING)
- `"use client"` for data fetching → use Server Component
- `getServerSideProps` → pages router legacy, forbidden in App Router
- Local state (useState/useReducer) for persistent data → use Supabase
- Global CSS outside `app/globals.css` → Tailwind only
- Fetching in `useEffect` when Server Component works → perf regression
- Deprecated libraries (no release in 12 months) → Lady Apis to find replacement
- Missing Zod validation at API/form boundaries → injection risk
