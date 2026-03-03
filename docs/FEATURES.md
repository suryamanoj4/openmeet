# OpenMeets - Feature List

A comprehensive list of features for the OpenMeets event management platform.

**Frontend:** Svelte + TypeScript  
**Backend:** FastAPI + Strawberry GraphQL

---

## 1. Authentication & User Management

### User Registration
- Email-based registration
- Password strength validation
- Email verification via token
- Resend verification email

### Login & Sessions
- Email/password login
- JWT-based authentication
- Access token (short-lived)
- Refresh token (long-lived)
- Remember me functionality
- Session management
- Logout (single session)
- Logout from all devices

### Password Management
- Forgot password flow
- Password reset via email token
- Change password (authenticated)
- Password reset invalidates active sessions

### User Profile
- View profile
- Update profile (name, phone, avatar)
- Change email with verification
- Delete account

---

## 2. Organization Management

### Organization CRUD
- Create organization (creator becomes first admin)
- Update organization details
- Delete organization (admin only)
- Organization logo upload
- Organization slug (unique identifier)
- Organization settings
- Organization description
- Organization social media links

### Organization Roles
- Admin (full control: manage members, create/publish events, manage settings, delete organization)
- Member (view events, view reports, can be assigned as event staff)

### Member Management
- Invite members by email (admin only)
- Accept/reject invitations
- Change member roles (admin can promote member to admin, and vice versa)
- Remove members from organization (admin only)
- View member list with roles
- Pending invitation management
- Invitation expiry (7 days)
- Bulk invite members (CSV upload)
- Transfer admin ownership (admin can transfer full control to another member)

### Organization Followers
- Follow organizations (any user, no membership required)
- Unfollow organizations
- Receive notifications for new events from followed organizations
- View follower count (public)
- Follower management (remove followers)
- Follower list visibility (public/private setting)

---

## 3. Event Management

### Event Creation & Editing
- Create events (organization admin only)
- Edit event details (event organizer or admin)
- Delete events (draft only, organizer or admin)
- Duplicate events
- Event cover image upload
- Event banner image upload
- Event staff assignment from organization members

### Event Details
- Event name & slug
- Event description (rich text)
- Event type (conference, workshop, meetup, webinar)
- Start date & time
- End date & time
- Timezone support
- Event status (draft, published, cancelled, completed)
- Event owner (organization)

### Venue Information
- Venue name
- Venue address
- Venue city
- Venue country
- Online event support
- Online meeting URL
- Hybrid event support (venue + online)

### Event Settings
- Maximum attendees
- Registration open date
- Registration close date
- Event visibility (public, private, unlisted)

### Event Lifecycle
- Draft mode (visible only to org members)
- Publish event (admin/organizer only)
- Cancel event (admin/organizer only)
- Auto-complete after event ends
- Event archival

### Event Discovery
- Public event listing
- Event search
- Event filtering (by date, type, location, organization)
- Event categories/tags
- Featured events
- Events from followed organizations

---

## 4. Event Registration & Payments

### Registration Flow
- User selects ticket type(s)
- User enters attendee information
- Payment integration (Stripe/Razorpay)
- Order confirmation on successful payment
- Automatic ticket generation
- Email confirmation with tickets

### Registration Settings
- Registration open/close dates
- Minimum and maximum tickets per order
- Ticket sale start/end dates
- Registration approval (optional, for free events)
- Registration form customization (custom fields)

### Payment Integration
- Secure payment gateway (Stripe, Razorpay)
- Credit/debit card support
- UPI support (India)
- Digital wallet support
- Payment status tracking
- Automatic retry for failed payments
- Payment receipt generation

### Refund Management
- Full refund
- Partial refund
- Refund reason tracking
- Refund status tracking
- Automatic refund policies
- Manual refund approval

---

## 5. Event Staff Management

### Staff Roles
- Organizer (full event control, can manage staff, edit event, manage tickets & orders)
- Co-organizer (manage tickets, orders, view reports, cannot delete event)
- Volunteer (view attendee list, check-in attendees)
- Security (check-in attendees only)

### Staff Assignment
- Assign staff from organization members only
- Assign multiple staff roles per event
- One organizer per event (can be transferred)
- Multiple co-organizers allowed
- Multiple volunteers allowed
- Multiple security staff allowed

### Staff Operations
- Assign staff to events (organizer or admin only)
- Remove staff from events (organizer or admin only)
- Change staff roles (organizer or admin only)
- Transfer organizer role to another member (current organizer only)
- View staff list with roles and permissions
- Custom permissions per role (advanced)
- Staff activity log

### Staff Selection Flow
1. Organization admin creates event (becomes default organizer)
2. Organizer/admin selects organization members for staff roles
3. Selected members receive notification of assignment
4. Members can accept or decline staff role
5. Staff members gain access based on their role permissions

---

## 6. Custom Event Page Builder

### Page Components
- Custom event title
- Rich text description editor
- Image gallery (multiple images)
- Event schedule/agenda builder
- Speaker/Presenter profiles
- Sponsor logos and links
- FAQ section
- Venue map integration
- Social media links
- Contact information

### Page Customization
- Drag-and-drop section ordering
- Show/hide sections toggle
- Custom color themes
- Font selection
- Layout templates (modern, classic, minimal)
- Mobile-responsive preview
- SEO settings (meta title, description)

### Page Management
- Save draft versions
- Preview before publishing
- Publish/unpublish toggle
- Version history
- Revert to previous version
- A/B testing (future)

### Content Blocks
- Hero section (title, subtitle, CTA)
- About event
- Schedule/timeline
- Speakers/presenters
- Sponsors/partners
- Venue information
- Registration/ticketing
- FAQ
- Contact form

---

## 7. Attendee Analytics & Management

### Registration Analytics
- Total registrations count
- Registration timeline (over time graph)
- Ticket type breakdown
- Revenue by ticket type
- Registration sources (direct, social, email)
- Conversion rate (page views to registrations)
- Drop-off points in registration funnel

### Attendee Status Tracking
- Registered (payment pending)
- Confirmed (payment completed)
- Checked-in
- No-show
- Cancelled
- Refunded

### Attendee Management
- View all attendees list
- Search attendees (name, email, order number)
- Filter by ticket type, status, check-in status
- Export attendee list (CSV, Excel)
- Bulk actions (check-in, cancel, email)
- Edit attendee information
- Transfer ticket to another person
- Add notes to attendee records

### Real-time Dashboard
- Live registration count
- Check-in progress (during event)
- Revenue tracker
- Ticket availability by type
- Recent registrations feed

---

## 8. Bulk Email Communication

### Email Campaigns
- Compose bulk emails to attendees
- Select recipient filters (all, by ticket type, by status)
- Email templates for common use cases
- Personalization tokens (name, ticket type, order number)
- Schedule email sending
- Send test email before campaign

### Email Recipient Filters
- All registered attendees
- By ticket type (VIP, General, etc.)
- By registration status (confirmed, pending, checked-in)
- By check-in status (checked-in, not checked-in)
- Custom attendee segments
- Exclude specific attendees

### Email Templates
- Welcome email
- Event reminder
- Event update notification
- Post-event follow-up
- Thank you email
- Custom templates

### Email Analytics
- Sent count
- Delivered count
- Open rate
- Click-through rate
- Bounce rate
- Unsubscribe count
- Email delivery status per recipient

### Communication History
- View all sent emails for event
- Email content archive
- Recipient list per email
- Delivery status tracking
- Failed email retry

---

## 9. Ticket Management

### Ticket Types
- Create multiple ticket types per event
- Ticket type name
- Ticket type description
- Ticket pricing
- Currency support
- Total quantity per ticket type
- Available quantity tracking
- Minimum tickets per order
- Maximum tickets per order
- Sale start date
- Sale end date
- Activate/deactivate ticket types
- Sort order for display

### Ticket Design
- Customizable ticket templates
- Background color selection
- Primary color selection
- Font family selection
- Logo positioning
- QR code display toggle
- Barcode display toggle
- Custom fields on ticket
- Template preview
- Multiple template styles

---

## 10. Order Management

### Order Creation
- Select ticket types
- Add multiple ticket quantities
- Enter attendee details per ticket
- Order summary before payment
- Order number generation
- Order expiry (15 minutes)
- Ticket reservation during checkout

### Order Details
- View order information
- Order items breakdown
- Attendee list per order
- Payment status
- Order status tracking

### Order Statuses
- Pending (awaiting payment)
- Confirmed (payment successful)
- Cancelled
- Expired (payment timeout)
- Refunded

### Order Operations
- Cancel order (pending only)
- Confirm order (after payment)
- Resend order confirmation
- Download order receipt

---

## 11. Attendee Check-in Management

### Attendee Information
- First name
- Last name
- Email address
- Phone number
- Company name
- Job title
- Custom data fields

### Check-in Management
- QR code-based check-in
- Manual check-in
- Check-in status tracking
- Check-in time recording
- Check-in staff tracking
- Undo check-in
- On-site registration

---

## 12. PDF & Ticket Generation

### Ticket PDF Features
- Auto-generated PDF tickets
- Custom ticket design
- Event branding (logo, colors)
- Attendee information
- Ticket type information
- Order number
- Event details (date, time, venue)
- QR code for check-in
- Barcode option

### PDF Operations
- Generate ticket on payment confirmation
- Regenerate tickets
- Download tickets
- Email tickets as attachment
- Bulk ticket generation

### QR Code Features
- Unique QR code per ticket
- Signed QR payload (security)
- QR code contains ticket verification data
- Offline check-in support

---

## 13. Email System

### Transactional Emails
- Email verification
- Password reset
- Order confirmation
- Payment receipt
- Ticket delivery
- Event reminder (24 hours before)
- Event update notifications
- Member invitation
- Refund confirmation

### Email Templates
- Default email templates
- Customizable email templates per organization
- HTML email support
- Plain text email support
- Email template variables
- Template preview

### Email Management
- SMTP configuration
- Email delivery tracking
- Email failure logging
- Retry failed emails
- Resend email functionality

---

## 14. Public Event Pages

### Event Page Features
- Public event URL
- Event cover image
- Event description
- Event date & time
- Venue information
- Available ticket types
- Ticket pricing
- Buy tickets (with/without login)
- Organization branding
- Share event functionality

### Event Page Customization
- Custom event slug
- Event FAQ section
- Event schedule/agenda
- Speaker information
- Sponsor logos
- Social media links

---

## 15. Audit & Activity Logging

### Audit Trail
- User login/logout events
- Organization changes
- Event creation/modification
- Ticket sales
- Order changes
- Payment events
- Refund events
- Staff changes
- Setting changes

### Audit Log Details
- Timestamp
- User who performed action
- Action type
- Resource affected
- Changes made (before/after)
- IP address
- User agent

### Audit Log Access
- View audit logs (admin only)
- Filter by date range
- Filter by action type
- Filter by user
- Export audit logs

---

## 16. Notifications

### In-App Notifications
- New order received (organizer/admin)
- Payment confirmed (attendee, organizer)
- Event reminder (24 hours before)
- Member invitation
- Event update (all attendees)
- Staff assignment (selected members)
- New event from followed organization (followers)
- Event published (organization members)

### Notification Categories
- Orders & Payments
- Event Updates
- Staff Assignments
- Membership & Invitations
- Followed Organizations

### Notification Preferences
- Email notifications toggle (per category)
- In-app notifications toggle (per category)
- Push notifications toggle (future)
- Notification frequency (instant, daily digest, weekly)
- Unsubscribe from specific notification types
- Quiet hours setting

### Notification Delivery
- Real-time in-app notifications
- Email notifications
- Scheduled digest emails
- Unsubscribe links in emails

---

## 17. Reporting & Analytics

### Event Reports
- Total tickets sold
- Revenue summary
- Attendance rate
- Check-in statistics
- Sales over time
- Ticket type breakdown

### Order Reports
- Total orders
- Order status breakdown
- Payment success rate
- Refund statistics

### Attendee Reports
- Total attendees
- Check-in rate
- Demographics (if collected)

### Export Options
- Export to CSV
- Export to Excel
- Export to PDF

---

## 18. Admin Dashboard

### Platform Administration
- View all organizations
- View all events
- View platform-wide statistics
- Manage users
- System settings

### Moderation
- Suspend organizations
- Remove events
- User management

---

## 19. Rate Limiting & Security

### Rate Limiting
- Login attempts limit
- Registration limit
- API rate limiting per user
- Email sending limit

### Security Features
- Password hashing
- JWT token security
- CORS configuration
- Input validation
- SQL injection prevention
- XSS prevention
- CSRF protection
- Account lockout after failed attempts

---

## 20. Settings & Configuration

### User Settings
- Profile settings
- Notification preferences
- Privacy settings
- Connected accounts

### Organization Settings
- General settings
- Branding settings
- Email template settings
- Payment settings
- Ticket design defaults

### Event Settings
- Registration settings
- Ticketing settings
- Email settings
- Check-in settings

---

## 21. Integrations

### Payment Gateways
- Stripe
- Razorpay

### Email Providers
- SendGrid
- AWS SES
- SMTP (generic)

### Future Integrations
- Google Calendar
- Zoom (for online events)
- Slack notifications
- Webhook support for third-party integrations

---

## 22. User & Organization Relationship

### User Journey Overview

**Key Principle:** Users cannot create events directly. All events must be created under an organization.

```
User Registration
       │
       ▼
┌──────────────────┐
│  Create/Join     │
│  Organization    │
└──────────────────┘
       │
       ├──► Admin (create & publish events, manage members)
       └──► Member (can be assigned as event staff)
       │
       ▼
┌──────────────────┐
│  Create Event    │ (Admin only)
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  Assign Staff    │ (from org members)
│  - Organizer     │
│  - Co-organizer  │
│  - Volunteer     │
│  - Security      │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  Publish Event   │
└──────────────────┘
```

### Permission Summary

| Action | User Role Required |
|--------|-------------------|
| Create organization | Any registered user |
| Join organization (via invite) | Any registered user |
| Follow organization | Any user (including guests) |
| Create event | Organization admin only |
| Publish event | Organization admin or event organizer |
| Edit event | Event organizer, co-organizer, or org admin |
| Manage event staff | Event organizer or org admin |
| Be assigned as event staff | Must be organization member (any role) |
| Buy tickets | Any user (guest checkout available) |
| Check-in attendees | Event volunteer or security staff |

### Organization Membership vs. Event Staff

**Organization Membership:**
- Grants access to organization resources
- Required to create events (admin) or be assigned as event staff
- Roles: Admin, Member

**Event Staff Role:**
- Specific to a single event
- Assigned from organization members
- Roles: Organizer, Co-organizer, Volunteer, Security
- Does not grant organization-level permissions

### Following vs. Membership

**Following:**
- No membership required
- Receive notifications for new events
- Cannot access member-only content
- Unlimited following

**Membership:**
- Invitation required (or join request if enabled)
- Access to member-only events and resources
- Can be assigned as event staff
- Single role per organization

---

## Feature Summary by Module

| Module | Feature Count |
|--------|---------------|
| 1. Authentication & User Management | 15 |
| 2. Organization Management | 20 |
| 3. Event Management | 28 |
| 4. Event Registration & Payments | 18 |
| 5. Event Staff Management | 12 |
| 6. Custom Event Page Builder | 25 |
| 7. Attendee Analytics & Management | 20 |
| 8. Bulk Email Communication | 22 |
| 9. Ticket Management | 18 |
| 10. Order Management | 12 |
| 11. Attendee Check-in Management | 10 |
| 12. PDF & Ticket Generation | 10 |
| 13. Email System | 12 |
| 14. Public Event Pages | 8 |
| 15. Audit & Activity Logging | 10 |
| 16. Notifications | 12 |
| 17. Reporting & Analytics | 10 |
| 18. Admin Dashboard | 5 |
| 19. Rate Limiting & Security | 10 |
| 20. Settings & Configuration | 12 |
| 21. Integrations | 6 |
| 22. User & Organization Relationship | 10 |

**Total Features: ~325**
