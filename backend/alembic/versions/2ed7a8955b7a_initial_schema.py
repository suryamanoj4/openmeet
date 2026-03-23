"""Initial schema - create all tables

Revision ID: 2ed7a8955b7a
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('is_email_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_is_active', 'users', ['is_active'])

    # Create organizations table
    op.create_table('organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=True),
        sa.Column('social_links', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    )
    op.create_index('idx_organizations_slug', 'organizations', ['slug'], unique=True)
    op.create_index('idx_organizations_is_active', 'organizations', ['is_active'])

    # Create members table
    op.create_table('members',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, default='member'),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id', ], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id', ], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.UniqueConstraint('user_id', 'organization_id', name='uq_members_user_org'),
    )
    op.create_index('idx_members_user_id', 'members', ['user_id'])
    op.create_index('idx_members_organization_id', 'members', ['organization_id'])
    op.create_index('idx_members_is_active', 'members', ['is_active'])

    # Create followers table
    op.create_table('followers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id', ], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id', ], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'organization_id', name='uq_followers_user_org'),
    )
    op.create_index('idx_followers_user_id', 'followers', ['user_id'])
    op.create_index('idx_followers_organization_id', 'followers', ['organization_id'])

    # Create events table
    op.create_table('events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='draft'),
        sa.Column('visibility', sa.String(length=50), nullable=False, default='public'),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=False, default='UTC'),
        sa.Column('venue_name', sa.String(length=255), nullable=True),
        sa.Column('venue_address', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_online', sa.Boolean(), nullable=False, default=False),
        sa.Column('online_url', sa.String(length=500), nullable=True),
        sa.Column('max_attendees', sa.Integer(), nullable=True),
        sa.Column('registration_open_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('registration_close_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cover_image_url', sa.String(length=500), nullable=True),
        sa.Column('banner_image_url', sa.String(length=500), nullable=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id', ], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    )
    op.create_index('idx_events_organization_id', 'events', ['organization_id'])
    op.create_index('idx_events_organization_slug', 'events', ['organization_id', 'slug'], unique=True)
    op.create_index('idx_events_status', 'events', ['status'])
    op.create_index('idx_events_visibility', 'events', ['visibility'])
    op.create_index('idx_events_start_date', 'events', ['start_date'])
    op.create_index('idx_events_is_active', 'events', ['is_active'])

    # Create event_staff table
    op.create_table('event_staff',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('member_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('assigned_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['event_id'], ['events.id', ], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['member_id'], ['members.id', ], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ),
        sa.UniqueConstraint('event_id', 'member_id', 'role', name='uq_event_staff_event_member_role'),
    )
    op.create_index('idx_event_staff_event_id', 'event_staff', ['event_id'])
    op.create_index('idx_event_staff_member_id', 'event_staff', ['member_id'])
    op.create_index('idx_event_staff_is_active', 'event_staff', ['is_active'])

    # Create tickets table
    op.create_table('tickets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('quantity', sa.Integer(), nullable=False, default=0),
        sa.Column('sold_quantity', sa.Integer(), nullable=False, default=0),
        sa.Column('min_per_order', sa.Integer(), nullable=False, default=1),
        sa.Column('max_per_order', sa.Integer(), nullable=False, default=10),
        sa.Column('sale_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sale_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['event_id'], ['events.id', ], ondelete='CASCADE'),
        sa.CheckConstraint('quantity >= 0', name='chk_tickets_quantity'),
        sa.CheckConstraint('sold_quantity <= quantity', name='chk_tickets_sold_quantity'),
        sa.CheckConstraint('price >= 0', name='chk_tickets_price'),
    )
    op.create_index('idx_tickets_event_id', 'tickets', ['event_id'])
    op.create_index('idx_tickets_is_active', 'tickets', ['is_active'])

    # Create orders table
    op.create_table('orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_number', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('customer_email', sa.String(length=255), nullable=False),
        sa.Column('customer_name', sa.String(length=255), nullable=False),
        sa.Column('customer_phone', sa.String(length=20), nullable=True),
        sa.Column('subtotal', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(precision=10, scale=2), nullable=False, default=0),
        sa.Column('discount_amount', sa.Numeric(precision=10, scale=2), nullable=False, default=0),
        sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('payment_status', sa.String(length=50), nullable=False, default='unpaid'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['event_id'], ['events.id', ], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    )
    op.create_index('idx_orders_event_id', 'orders', ['event_id'])
    op.create_index('idx_orders_order_number', 'orders', ['order_number'], unique=True)
    op.create_index('idx_orders_customer_email', 'orders', ['customer_email'])
    op.create_index('idx_orders_status', 'orders', ['status'])
    op.create_index('idx_orders_payment_status', 'orders', ['payment_status'])
    op.create_index('idx_orders_is_active', 'orders', ['is_active'])

    # Create order_items table
    op.create_table('order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ticket_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id', ], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id', ], ondelete='RESTRICT'),
        sa.CheckConstraint('quantity > 0', name='chk_order_items_quantity'),
        sa.CheckConstraint('unit_price >= 0', name='chk_order_items_unit_price'),
    )
    op.create_index('idx_order_items_order_id', 'order_items', ['order_id'])
    op.create_index('idx_order_items_ticket_id', 'order_items', ['ticket_id'])

    # Create attendees table
    op.create_table('attendees',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ticket_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column('job_title', sa.String(length=100), nullable=True),
        sa.Column('custom_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('check_in_status', sa.String(length=50), nullable=False, default='not_checked_in'),
        sa.Column('check_in_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('check_in_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['order_item_id'], ['order_items.id', ], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id', ], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['check_in_by'], ['users.id'], ),
    )
    op.create_index('idx_attendees_order_item_id', 'attendees', ['order_item_id'])
    op.create_index('idx_attendees_ticket_id', 'attendees', ['ticket_id'])
    op.create_index('idx_attendees_email', 'attendees', ['email'])
    op.create_index('idx_attendees_check_in_status', 'attendees', ['check_in_status'])
    op.create_index('idx_attendees_is_active', 'attendees', ['is_active'])

    # Create payments table
    op.create_table('payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('provider_payment_id', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('refunded_amount', sa.Numeric(precision=10, scale=2), nullable=False, default=0),
        sa.Column('refund_reason', sa.Text(), nullable=True),
        sa.Column('refunded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id', ], ondelete='CASCADE'),
    )
    op.create_index('idx_payments_order_id', 'payments', ['order_id'])
    op.create_index('idx_payments_provider_payment_id', 'payments', ['provider_payment_id'], unique=True)
    op.create_index('idx_payments_status', 'payments', ['status'])
    op.create_index('idx_payments_is_active', 'payments', ['is_active'])

    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('changes', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    )
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_resource', 'audit_logs', ['resource_type', 'resource_id'])
    op.create_index('idx_audit_logs_organization_id', 'audit_logs', ['organization_id'])
    op.create_index('idx_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('idx_audit_logs_is_active', 'audit_logs', ['is_active'])

    # Create refresh_tokens table
    op.create_table('refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False, default=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_ip', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id', ], ondelete='CASCADE'),
    )
    op.create_index('idx_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('idx_refresh_tokens_token_hash', 'refresh_tokens', ['token_hash'], unique=True)
    op.create_index('idx_refresh_tokens_is_active', 'refresh_tokens', ['is_active'])

    # Create email_logs table
    op.create_table('email_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recipient_email', sa.String(length=255), nullable=False),
        sa.Column('template_name', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_email_logs_recipient_email', 'email_logs', ['recipient_email'])
    op.create_index('idx_email_logs_status', 'email_logs', ['status'])
    op.create_index('idx_email_logs_is_active', 'email_logs', ['is_active'])


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('email_logs')
    op.drop_table('refresh_tokens')
    op.drop_table('audit_logs')
    op.drop_table('payments')
    op.drop_table('attendees')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('tickets')
    op.drop_table('event_staff')
    op.drop_table('events')
    op.drop_table('followers')
    op.drop_table('members')
    op.drop_table('organizations')
    op.drop_table('users')
