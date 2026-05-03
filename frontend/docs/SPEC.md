# OpenMeets Frontend - Technical Specification

**Purpose:** Explain frontend architecture AND guide frontend developers

---

## What the Frontend Does

The frontend provides:
- User authentication pages (login, register)
- Dashboard for managing organizations
- Event creation and management
- No-code page builder (drag-drop)
- Ticket purchase flow (checkout)
- Attendee management and check-in
- Analytics and reports

---

## Architecture

### Structure

```
frontend/src/
├── routes/              # SvelteKit routes
│   ├── (auth)/        # Auth pages
│   ├── (app)/         # Dashboard
│   └── event/         # Public pages
├── lib/
│   ├── components/    # Reusable components
│   │   ├── ui/        # Basic UI (button, input)
│   │   └── builder/   # Page builder
│   ├── services/      # API calls
│   ├── stores/        # Svelte stores
│   └── graphql/       # Queries/mutations
├── app.css            # Global styles
└── app.html          # HTML template
```

### Technology

- Svelte 5.x + SvelteKit - Framework
- TypeScript - Language
- TailwindCSS - Styling
- Urql - GraphQL client

---

## Pages

### Authentication

| Route | Component | Purpose |
|------|-----------|---------|
| /login | LoginPage | User login |
| /register | RegisterPage | User registration |

### Dashboard

| Route | Component | Purpose |
|------|-----------|---------|
| /dashboard | Dashboard | Main hub |
| /organization | OrgSettings | Manage org |
| /events | EventList | List events |
| /events/new | CreateEvent | Create event |
| /events/[id]/edit | EditEvent | Edit event |
| /attendees | AttendeeList | View attendees |
| /checkin | CheckIn | Scan QR codes |
| /reports | Reports | View analytics |

### Public

| Route | Component | Purpose |
|------|-----------|---------|
| /event/[slug] | EventPage | Public page |
| /event/[slug]/checkout | Checkout | Buy tickets |

---

## Component Library

### Basic UI Components

Located in `lib/components/ui/`:

| Component | Props | Purpose |
|-----------|-------|---------|
| Button | variant, size, loading | Actions |
| Input | type, error, label | Text entry |
| Select | options, value | Dropdown |
| Checkbox | checked, label | Boolean |
| Modal | open, title | Dialogs |
| Card | - | Content container |
| Badge | variant, status | Labels |
| Spinner | size | Loading |

### Builder Components

Located in `lib/components/builder/`:

| Component | Props | Purpose |
|-----------|-------|---------|
| Builder | eventId, sections | Main builder |
| Canvas | sections, onReorder | Drag area |
| Sidebar | components | Component picker |
| PropertiesPanel | block, onChange | Edit block |
| BlockRenderer | block | Render block |

---

## Page Builder

### Components (Blocks)

| Block | Props | Description |
|-------|-------|-------------|
| Hero | title, subtitle, cta, bgImage | Cover section |
| About | content | Event description |
| Schedule | items: Array | Timeline |
| Speakers | speakers: Array | Speaker grid |
| Sponsors | logos: Array | Sponsor logos |
| Venue | name, address, mapUrl | Location |
| FAQs | items: Array | Accordion |
| Tickets | eventId | Ticket selection |
| Registration | eventId | Sign up form |
| Gallery | images: Array | Image grid |
| Contact | email, socials | Contact info |
| CTA | title, button, link | Banner |

### Block Structure

```typescript
interface Block {
  id: string;
  type: 'hero' | 'about' | 'schedule' | ...;
  props: Record<string, any>;
  styles: {
    padding: string;
    backgroundColor: string;
    textAlign: 'left' | 'center' | 'right';
  };
  visibility: {
    desktop: boolean;
    tablet: boolean;
    mobile: boolean;
  };
}
```

### Theme

```typescript
interface Theme {
  primaryColor: string;
  secondaryColor: string;
  fontFamily: string;
  backgroundColor: string;
  borderRadius: string;
}
```

---

## State Management

### Stores

Located in `lib/stores/`:

| Store | Purpose | Key State |
|-------|---------|----------|
| auth | User auth | user, token, isAuthenticated |
| organization | Current org | org, members |
| events | Event list | events, loading |
| attendees | Attendee list | attendees, filters |
| builder | Page builder | sections, theme |

### Auth Store Example

```typescript
const auth = createAuthStore();

auth.subscribe(state => {
  // { user, token, isAuthenticated }
});

// Usage
auth.login(user, token);
auth.logout();
```

---

## GraphQL Client

### Configuration

```typescript
// lib/graphql/client.ts
import { createClient, cacheExchange } from 'urql';

export const client = createClient({
  url: '/graphql',
  exchanges: [cacheExchange],
});
```

### Queries

```typescript
// lib/graphql/queries/event.ts
export const GET_EVENT = gql`
  query GetEvent($id: UUID!) {
    event(id: $id) {
      id
      name
      startDate
      tickets { name, price }
    }
  }
`;
```

### Mutations

```typescript
// lib/graphql/mutations/order.ts
export const CREATE_ORDER = gql`
  mutation CreateOrder($input: CreateOrderInput!) {
    createOrder(input: $input) {
      id
      orderNumber
    }
  }
`;
```

---

## Implementation Order

### Step 1: Foundation
1. Set up SvelteKit + TailwindCSS
2. Create UI component library
3. Set up GraphQL client

### Step 2: Authentication
4. Build login page
5. Build register page
6. Implement auth store

### Step 3: Dashboard
7. Build dashboard home
8. Create navigation
9. Add organization pages

### Step 4: Events
10. Build event list
11. Create event form
12. Add event settings

### Step 5: Page Builder
13. Create builder canvas
14. Build component library
15. Add properties panel

### Step 6: Checkout
16. Ticket selection
17. Attendee forms
18. Payment integration

### Step 7: Attendees
19. Attendee list
20. Check-in interface
21. Reports

---

## Responsive Design

### Breakpoints

| Breakpoint | Width | Target |
|-----------|-------|--------|
| sm | 640px | Large phones |
| md | 768px | Tablets |
| lg | 1024px | Laptops |
| xl | 1280px | Desktops |

### Strategy

- Mobile-first CSS
- Touch targets: min 44px
- Fluid typography
- Container queries where needed

---

## Accessibility

### Requirements

- WCAG 2.1 AA
- Keyboard navigation
- Focus indicators
- Screen reader support
- Color contrast: 4.5:1

### Implementation

- Semantic HTML
- ARIA labels where needed
- Form associations
- Error announcements

---

## Performance Targets

| Metric | Target |
|--------|--------|
| FCP | <1.5s |
| LCP | <2.5s |
| TTI | <3s |
| CLS | <0.1 |

### Optimization

- Code splitting (SvelteKit automatic)
- Image optimization
- Lazy loading
- GraphQL caching

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Slow page loads | Enable code splitting |
| State inconsistencies | Use Svelte stores properly |
| Builder lag | Virtualize long lists |
| Check-in offline | Add service worker |

---

## Out of Scope

- Native mobile apps
- PWA (advanced)
- Real-time collaboration
- A/B testing
- Multi-language

---

**End of Frontend Spec**