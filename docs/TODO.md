# OpenMeets - Development Roadmap

**Purpose:** Track what has been done AND what remains to be built

---

## Status Legend

- ✅ **Done** - Implemented and functional
- 🔄 **In Progress** - Currently being built
- 📋 **To Do** - Not yet started
- ❌ **Blocked** - Needs resolution

---

## Backend API

### Authentication

| Feature | Status | Notes |
|---------|--------|-------|
| User registration | ✅ Done | Basic implementation |
| User login | ✅ Done | JWT tokens |
| Token refresh | 📋 To Do | Implement refresh endpoint |
| Password reset | 📋 To Do | Email token flow |
| Email verification | 📋 To Do | Send verification email |
| Session management | 📋 To Do | View/logout sessions |

### Organizations

| Feature | Status | Notes |
|---------|--------|-------|
| Create organization | ✅ Done | Basic implementation |
| Update organization | ✅ Done | Implemented |
| Delete organization | 📋 To Do | Soft delete |
| Add members | 📋 To Do | Invite by email |
| Change member roles | 📋 To Do | Admin/member |
| Remove members | 📋 To Do | Soft delete |
| Organization followers | 📋 To Do | Follow/unfollow |
| Invite members | 📋 To Do | Email invitations |

### Events

| Feature | Status | Notes |
|---------|--------|-------|
| Create event | ✅ Done | Basic CRUD |
| Update event | ✅ Done | Implemented |
| Delete event | 📋 To Do | Draft only |
| Publish event | 📋 To Do | Status change |
| Cancel event | 📋 To Do | Status change |
| Duplicate event | 📋 To Do | Copy event data |
| Event types | ✅ Done | Enum defined |
| Visibility controls | ✅ Done | Public/private |
| Venue support | ✅ Done | JSON address |
| Online events | ✅ Done | is_online flag |
| Staff assignment | 📋 To Do | Assign from members |

### Tickets

| Feature | Status | Notes |
|---------|--------|-------|
| Create ticket type | ✅ Done | Basic CRUD |
| Update ticket | ✅ Done | Implemented |
| Set pricing | ✅ Done | price, currency |
| Inventory | ✅ Done | quantity tracking |
| Sale windows | ✅ Done | sale_start, sale_end |
| Order limits | ✅ Done | min/max per order |
| Deactivate ticket | 📋 To Do | is_active toggle |

### Orders

| Feature | Status | Notes |
|---------|--------|-------|
| Create order | 📋 To Do | With items |
| View order | 📋 To Do | Order details |
| Order expiry | 📋 To Do | 15 min timer |
| Cancel order | 📋 To Do | Release tickets |
| Guest checkout | 📋 To Do | No auth required |

### Payments

| Feature | Status | Notes |
|---------|--------|-------|
| Stripe integration | 📋 To Do | Payment intents |
| Razorpay integration | 📋 To Do | Payment intents |
| Webhook handling | 📋 To Do | Confirm payment |
| Refund processing | 📋 To Do | Full/partial |
| Payment status | 📋 To Do | Track status |

### Attendees

| Feature | Status | Notes |
|---------|--------|-------|
| View attendees | 📋 To Do | List + filters |
| Search | 📋 To Do | By name/email |
| Export | 📋 To Do | CSV export |
| Check-in | 📋 To Do | Status update |
| QR check-in | 📋 To Do | Scan QR code |
| Undo check-in | 📋 To Do | Reset status |
| Notes | 📋 To Do | Add notes |

### Analytics

| Feature | Status | Notes |
|---------|--------|-------|
| Registration stats | 📋 To Do | Count + timeline |
| Revenue reports | 📋 To Do | Earnings |
| Ticket breakdown | 📋 To Do | By type |
| Attendance rates | 📋 To Do | Check-in % |
| Export reports | 📋 To Do | CSV/Excel |

### Background Tasks (Celery)

| Task | Status | Notes |
|------|--------|-------|
| Order expiry | 📋 To Do | Release tickets |
| Payment webhook | 📋 To Do | Process async |
| PDF generation | 📋 To Do | Tickets w/ QR |
| Email sending | 📋 To Do | Queue emails |
| Event reminders | 📋 To Do | 24hr before |

---

## Frontend

### Authentication Pages

| Page | Status | Notes |
|------|--------|-------|
| Login | ✅ Done | Implemented |
| Register | ✅ Done | Implemented |
| Forgot password | 📋 To Do | Reset flow |

### Dashboard

| Page | Status | Notes |
|------|--------|-------|
| Dashboard home | ✅ Done | Basic layout |
| Organization list | 📋 To Do | User's orgs |

### Organization Management

| Page | Status | Notes |
|------|--------|-------|
| Create org | 📋 To Do | Form |
| Org settings | 📋 To Do | Edit details |
| Member list | 📋 To Do | Role controls |
| Add member | 📋 To Do | Invite form |

### Event Management

| Page | Status | Notes |
|------|--------|-------|
| Event list | 📋 To Do | List view |
| Create event | 📋 To Do | Multi-step form |
| Edit event | 📋 To Do | Edit form |
| Event settings | 📋 To Do | Visibility |

### Page Builder

| Feature | Status | Notes |
|---------|--------|-------|
| Builder UI | 📋 To Do | Drag-drop |
| Component library | 📋 To Do | 15+ blocks |
| Properties panel | 📋 To Do | Edit props |
| Live preview | 📋 To Do | Desktop/mobile |
| Theme system | 📋 To Do | Colors/fonts |
| Save/publish | 📋 To Do | Export JSON |

### Ticketing

| Page | Status | Notes |
|------|--------|-------|
| Ticket list | 📋 To Do | Manage types |
| Create ticket | 📋 To Do | Form |
| Order list | 📋 To Do | View orders |

### Checkout

| Page | Status | Notes |
|------|--------|-------|
| Ticket selection | 📋 To Do | Choose tickets |
| Attendee details | 📋 To Do | Per ticket |
| Payment form | 📋 To Do | Stripe/Razorpay |
| Confirmation | 📋 To Do | Success page |

### Attendee Management

| Page | Status | Notes |
|------|--------|-------|
| Attendee list | 📋 To Do | Search + filter |
| Export | 📋 To Do | Download |
| Attendee details | 📋 To Do | View profile |

### Check-in

| Page | Status | Notes |
|------|--------|-------|
| Check-in scanner | 📋 To Do | QR scanner |
| Manual search | 📋 To Do | Find attendee |
| Check-in stats | 📋 To Do | Real-time counts |

### Reports

| Page | Status | Notes |
|------|--------|-------|
| Registration stats | 📋 To Do | Charts |
| Revenue reports | 📋 To Do | Earnings |
| Export | 📋 To Do | CSV download |

### Public Pages

| Page | Status | Notes |
|------|--------|-------|
| Event page | 📋 To Do | Dynamic from builder |
| Ticket purchase | 📋 To Do | Checkout flow |
| Confirmation | 📋 To Do | Tickets sent |

---

## Database Models

### Implemented Models

- ✅ User
- ✅ Organization
- ✅ Member (basic)
- ✅ Event (basic)
- ✅ Ticket (basic)

### To Be Implemented

- 📋 Follower
- 📋 Invitation
- 📋 EventStaff
- 📋 Order
- 📋 OrderItem
- 📋 Attendee
- 📋 Payment
- 📋 RefreshToken
- 📋 AuditLog
- 📋 EmailLog
- 📋 Notification

---

## Priority Tasks

### Immediate (This Week)

1. 🔄 Complete order + payment flow
2. 🔄 Implement attendee CRUD
3. 🔄 Create attendee list page
4. 📋 Start page builder components

### Next (This Month)

5. 📋 Check-in system
6. 📋 Email campaigns
7. 📋 Analytics dashboard

### Later (This Quarter)

8. 📋 Advanced page builder
9. 📋 Notifications system
10. 📋 Performance optimization

---

## Notes

- Backend uses GraphQL (Strawberry)
- Frontend uses Svelte + TypeScript
- Database: PostgreSQL
- Task queue: Celery for async tasks
- Payments: Stripe + Razorpay

---

**End of Roadmap**