# 🌐 I2L Phygital

> **STATUS:** In Development · Web Application

I2L Phygital is a web application bridging physical and digital experiences. Features a modern component architecture with database migrations and shared library support.

> ⚠️ **Note:** The build framework and exact dependencies have not been fully verified. Directory structure suggests Next.js App Router with Prisma-managed PostgreSQL migrations. Verify `package.json` before running build commands.

## Structure

```
i2l-phygital/
├── app/         # Application pages (App Router layout)
├── components/  # React component library
├── lib/         # Shared utilities and helpers
└── migrations/  # Database migration files
```

## Setup

```bash
# From monorepo root (02_FORGE/)
cd apps/i2l-phygital

# Install dependencies
npm install

# Start dev server
npm run dev
```
