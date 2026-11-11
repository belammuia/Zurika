# Zurika Frontend

Standalone React + TypeScript + Tailwind CSS frontend prototype for Zurika Motor Insurance Claims. The Django backend remains in the repository root and is not modified by this project.

## Requirements

- Node.js 20.19+ (Node 22 LTS recommended)
- npm 10+

## Run locally

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

## Build

```bash
npm run build
npm run preview
```

## Prototype navigation

The app starts on the claims-officer dashboard. Use the role selector in the top-right corner to preview each workspace:

- Customer
- Claims Officer
- Senior Officer
- Administrator

The login screen is available at `/login`. Demo login accepts any non-empty email and password; choose the role before signing in.

## Included interfaces

- Login and role preview
- Customer dashboard, claim submission, claims list and claim tracking
- Claims officer dashboard, queue, claim review and routing rules
- Senior officer approvals and payout oversight
- Administrator overview, payouts, insurers, team access, documents and audit trail

All data and interactions are local mock state. No API requests are made. The project uses React Router for navigation and Tailwind CSS v4 through the Vite plugin; the design-specific component styles are kept in `src/styles.css` to preserve the supplied Zurika design language.

## Project structure

```text
frontend/
├── public/assets/          # Vehicle evidence imagery from the design PDF
├── src/
│   ├── components/         # Shared layout and UI components
│   ├── data/               # Typed mock records and routing rules
│   ├── pages/              # Role-specific screens
│   ├── App.tsx
│   ├── main.tsx
│   ├── styles.css
│   └── types.ts
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```
