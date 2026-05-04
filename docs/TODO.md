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
| User registration | ✅ Done | register mutation with JWT |
| User login | ✅ Done | login mutation with JWT |
| Token refresh | ✅ Done | refreshToken mutation |
| Token revoke | ✅ Done | revokeToken + logout mutations |
| Session management | ✅ Done | logout_all mutation |
| RBAC (roles) | ✅ Done | user/organizer/admin + is_superuser |
| Password reset | 📋 To Do | Email token flow |
| Email verification | 📋 To Do | Send verification email |

### Organizations

| Feature | Status | Notes |
|---------|--------|-------|
| Create organization | ✅ Done | Full CRUD |
| Update organization | ✅ Done | Implemented |
| Delete organization | ✅ Done | Soft delete |
| Add members | ✅ Done | addOrganizationMember |
| Change member roles | ✅ Done | updateMemberRole |
| Remove members | ✅ Done | Soft delete |
| Organization followers | ✅ Done | Follow/unfollow |
| Invite members | 📋 To Do | Email invitations |

### Events

| Feature | Status | Notes |
|---------|--------|-------|
| Create event | ✅ Done | Full CRUD |
| Update event | ✅ Done | Implemented |
| Delete event | ✅ Done | Soft delete |
| Publish event | ✅ Done | Status change via update |
| Cancel event | ✅ Done | Status change via update |
| Duplicate event | 📋 To Do | Copy event data |
| Event types | ✅ Done | Enum defined |
| Visibility controls | ✅ Done | Public/private |
| Venue support | ✅ Done | JSON address |
| Online events | ✅ Done | is_online flag |
| Staff assignment | 📋 To Do | Assign from members |

### Tickets

| Feature | Status | Notes |
|---------|--------|-------|
| Create ticket type | ✅ Done | Full CRUD |
| Update ticket | ✅ Done | Implemented |
| Set pricing | ✅ Done | price, currency |
| Inventory | ✅ Done | quantity tracking |
| Sale windows | ✅ Done | sale_start, sale_end |
| Order limits | ✅ Done | min/max per order |
| Deactivate ticket | ✅ Done | is_active toggle |

### Orders

| Feature | Status | Notes |
|---------|--------|-------|
| Create order | ✅ Done | With items, ticket reservation |
| View order | ✅ Done | By ID, number, event, email |
| Order expiry | ✅ Done | Background task every 60s |
| Cancel order | ✅ Done | Release tickets |
| Confirm order | ✅ Done | Mark paid/confirmed |
| Guest checkout | ✅ Done | No auth required |

### Payments

| Feature | Status | Notes |
|---------|--------|-------|
| Payment model | ✅ Done | Full Payment model |
| Payment queries | ✅ Done | By ID, provider_id, order |
| Create payment | ✅ Done | Initiated by frontend |
| Webhook handling | ✅ Done | Stripe + Razorpay webhooks |
| Payment status updates | ✅ Done | success/failed/refunded |
| Refund processing | ✅ Done | Full/partial refund |
| Stripe integration | 📋 To Do | Frontend SDK only |
| Razorpay integration | 📋 To Do | Frontend SDK only |

### Attendees

| Feature | Status | Notes |
|---------|--------|-------|
| View attendees | ✅ Done | List + filters |
| Search | ✅ Done | By name/email |
| Check-in | ✅ Done | Status update (bool) |
| Undo check-in | ✅ Done | Reset status |
| Notes | ✅ Done | Add/update notes |
| QR check-in | 📋 To Do | Scan QR code |
| Export | 📋 To Do | CSV export |

### Analytics

| Feature | Status | Notes |
|---------|--------|-------|
| Registration stats | 📋 To Do | Count + timeline |
| Revenue reports | 📋 To Do | Earnings |
| Ticket breakdown | 📋 To Do | By type |
| Attendance rates | 📋 To Do | Check-in % |
| Export reports | 📋 To Do | CSV/Excel |

### Background Tasks

| Task | Status | Notes |
|------|--------|-------|
| Order expiry | ✅ Done | asyncio task every 60s |
| Token cleanup | ✅ Done | asyncio task every 1hr |
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
| Payment integration | 📋 To Do | See integration steps below |
| Confirmation | 📋 To Do | Success page |

### Payment Integration Steps (Frontend)

1. **Load Razorpay Checkout SDK** in `<script>` tag:
   ```html
   <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
   ```

2. **Create payment order** on checkout submit:
   ```graphql
   mutation {
     createPaymentOrder(orderId: "...", provider: "razorpay") {
       providerOrderId   # razorpay_order_id
       providerKeyId     # RAZORPAY_KEY_ID
       orderId
       orderNumber
       amount            # in paise
       currency
     }
   }
   ```

3. **Open Razorpay Checkout modal** with the response:
   ```ts
   const rzp = new Razorpay({
     key: data.createPaymentOrder.providerKeyId,
     order_id: data.createPaymentOrder.providerOrderId,
     amount: data.createPaymentOrder.amount,
     currency: data.createPaymentOrder.currency,
     name: "OpenMeets",
     prefill: { email: customerEmail, name: customerName },
     handler: async (response) => {
       // Step 4 — verify on backend
     }
   });
   rzp.open();
   ```

4. **Verify payment** in the `handler` callback:
   ```graphql
   mutation {
     verifyPayment(
       orderId: "..."
       providerPaymentId: response.razorpay_payment_id
       providerOrderId: response.razorpay_order_id
       signature: response.razorpay_signature
       provider: "razorpay"
     ) {
       success
       paymentStatus
       message
     }
   }
   ```

5. **On success** (`verifyPayment.success === true`):
   - Show confirmation page
   - Redirect to order confirmation

6. **Edge cases**:
   - Payment modal dismissed → keep order in pending state (auto-expires in 15min)
   - Network failure during verification → retry verifyPayment with same signature
   - Webhook handles missed callbacks as backup (backend `POST /webhooks/razorpay`)

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

- ✅ User (with role + is_superuser)
- ✅ Organization
- ✅ Member
- ✅ Event
- ✅ Ticket
- ✅ Order
- ✅ OrderItem
- ✅ Attendee
- ✅ Payment
- ✅ RefreshToken
- ✅ AuditLog
- ✅ EmailLog
- ✅ Follower
- ✅ EventStaff

### To Be Implemented

- 📋 Invitation
- 📋 Notification

---

## Priority Tasks

### Immediate (This Week)

1. ✅ Complete order + payment flow
2. ✅ Implement attendee CRUD
3. ✅ Auth system (JWT + RBAC)
4. ✅ Background tasks (order expiry)
5. 📋 Start frontend integration

### Next (This Month)

6. 📋 Frontend auth pages (login/register)
7. 📋 Organization + event management UI
8. 📋 Checkout flow (Stripe/Razorpay SDKs)
9. 📋 Check-in system

### Later (This Quarter)

10. 📋 Page builder
11. 📋 Email campaigns
12. 📋 Analytics dashboard
13. 📋 Notifications system

---

## Notes

- Backend uses GraphQL (Strawberry) + FastAPI
- Frontend uses Svelte + TypeScript
- Database: PostgreSQL
- Background tasks: asyncio scheduler (no Celery/Redis needed)
- Payments: Stripe + Razorpay (frontend SDKs + backend webhooks)

---

**End of Roadmap**