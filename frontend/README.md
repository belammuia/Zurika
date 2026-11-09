# Zurika frontend

Standalone Angular + TypeScript + Tailwind CSS frontend prototype for the Zurika motor-insurance claims platform. The project is intentionally isolated under `frontend/` when copied into the existing repository; it does not change Django, Celery, Redis, PostgreSQL, or backend configuration.

## Run locally

Requirements: Node.js 20.19+ and npm.

```bash
npm install
npm start
```

Open [http://localhost:4200](http://localhost:4200).

## Production build

```bash
npm run build
```

## Design reference

This implementation follows the supplied **Project Design** PDF (dated 9 October 2026). The interface carries through its pale grey workspace, white cards, compact tables, blue primary actions, role-specific side navigation, customer claim wizard, claims officer queue/review, and routing rules. The supplied vehicle evidence photographs are used in the local prototype assets.

## Included screens

- Sign-in with Customer / Claims Officer role tabs
- Customer dashboard, My Claims, claim detail / progress, three-step File a Claim flow, and submission confirmation
- Claims Officer dashboard, Claims Queue, detailed claim review with Approve / Reject / Request More Info / Reassign actions, and Routing Rules
- Senior Officer dashboard and approvals queue
- Administrator overview, insurer directory, team & access, payouts, and audit trail
- Documents register and local role preview selector

## Prototype behaviour

All records are mock data in `src/app/mock-data.ts`. Search and filters, routing-rule toggles/editing, the member invite form, claim submission steps, and claim review actions run locally in the browser. No authentication, API requests, real document uploads, claim state persistence, payout instructions, or backend integration is connected.

## Structure

```text
src/
  app/
    core/            # Role preview state
    pages/           # Standalone routed screens
    app.component.ts # Role-aware application shell
    app.routes.ts    # Angular routes
    mock-data.ts     # Typed demonstration records
    models.ts        # Domain interfaces and unions
  assets/            # Evidence photos extracted from the supplied design PDF
  styles.css         # Tailwind CSS import and product component styles
```

The root Django project is deliberately not included in this frontend package. Extract this folder as `frontend/` in the Zurika repository to keep concerns separate.
