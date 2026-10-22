"""Complete, static RenewGrid schema baseline for FRESH databases only.

The legacy revisions are preserved. Existing databases at a known Alembic
revision do not reapply this ancestor. Never stamp an unverified database.

Revision ID: a6f21e309bb4
Revises:
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

revision = 'a6f21e309bb4'
down_revision = None
branch_labels = None
depends_on = None

userrole_enum = ENUM('USER', 'COLLECTOR', 'RECYCLER', 'ADMIN', name='userrole', create_type=False)
wastecategory_enum = ENUM('LAPTOPS', 'MOBILE', 'MONITORS', 'PRINTERS', 'CIRCUITS', 'BATTERIES', 'MIXED', name='wastecategory', create_type=False)
pickupstatus_enum = ENUM('PENDING', 'ASSIGNED', 'ACCEPTED', 'IN_PROGRESS', 'PROOF_UPLOADED', 'COLLECTED', 'DELIVERED', 'PROCESSING', 'RECYCLED', 'COMPLETED', 'CANCELLED', 'REJECTED', 'IN_ROUTE', name='pickupstatus', create_type=False)


def upgrade():
    bind = op.get_bind()
    # Do not silently overwrite or stamp a populated preexisting database.
    existing = set(sa.inspect(bind).get_table_names()) - {'alembic_version'}
    if existing:
        raise RuntimeError('RenewGrid baseline requires an empty database. Back up and reconcile existing databases separately.')
    if bind.dialect.name == 'postgresql':
        for enum_type in (userrole_enum, wastecategory_enum, pickupstatus_enum):
            enum_type.create(bind, checkfirst=True)
    # Frozen schema snapshot generated from the 2026-09-09 project models.
    op.create_table('app_config',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=100), nullable=False),
    sa.Column('value', sa.Text(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    op.create_index(op.f('ix_app_config_id'), 'app_config', ['id'], unique=False)
    op.create_table('pricing_rules',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('base_price', sa.Float(), nullable=False),
    sa.Column('per_kg_rate', sa.Float(), nullable=False),
    sa.Column('premium_rate', sa.Float(), nullable=False),
    sa.Column('condition_multiplier_working', sa.Float(), nullable=False),
    sa.Column('condition_multiplier_partial', sa.Float(), nullable=False),
    sa.Column('condition_multiplier_broken', sa.Float(), nullable=False),
    sa.Column('min_weight', sa.Float(), nullable=False),
    sa.Column('unit', sa.String(length=20), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pricing_rules_id'), 'pricing_rules', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(length=150), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('phone_number', sa.String(length=20), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('profile_image', sa.String(length=1000), nullable=True),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('role', userrole_enum, nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_available', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('notifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('is_read', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_table('waste_uploads',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('category', wastecategory_enum, nullable=False),
    sa.Column('condition', sa.String(length=100), nullable=True),
    sa.Column('estimated_weight', sa.Float(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('ai_detected_type', sa.String(length=255), nullable=True),
    sa.Column('ai_confidence', sa.Float(), nullable=True),
    sa.Column('estimated_price', sa.Float(), nullable=True),
    sa.Column('estimated_credit_points', sa.Integer(), nullable=True),
    sa.Column('estimated_co2_saved', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_waste_uploads_id'), 'waste_uploads', ['id'], unique=False)
    op.create_table('pickup_requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('waste_upload_id', sa.Integer(), nullable=False),
    sa.Column('collector_id', sa.Integer(), nullable=True),
    sa.Column('recycler_id', sa.Integer(), nullable=True),
    sa.Column('address', sa.String(length=500), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('pickup_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('status', pickupstatus_enum, nullable=False),
    sa.Column('final_collected_weight', sa.Float(), nullable=True),
    sa.Column('final_price', sa.Float(), nullable=True),
    sa.Column('collector_notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['collector_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['recycler_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['waste_upload_id'], ['waste_uploads.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pickup_requests_id'), 'pickup_requests', ['id'], unique=False)
    op.create_table('waste_images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('waste_id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(length=1000), nullable=False),
    sa.Column('is_primary', sa.Boolean(), nullable=False),
    sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['waste_id'], ['waste_uploads.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_waste_images_id'), 'waste_images', ['id'], unique=False)
    op.create_table('collector_proofs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pickup_id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(length=1000), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['pickup_id'], ['pickup_requests.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('pickup_id')
    )
    op.create_index(op.f('ix_collector_proofs_id'), 'collector_proofs', ['id'], unique=False)
    op.create_table('pickup_reviews',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pickup_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['pickup_id'], ['pickup_requests.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pickup_reviews_id'), 'pickup_reviews', ['id'], unique=False)
    op.create_table('pickup_status_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pickup_id', sa.Integer(), nullable=False),
    sa.Column('status', pickupstatus_enum, nullable=False),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('changed_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('changed_by_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['changed_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['pickup_id'], ['pickup_requests.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pickup_status_history_id'), 'pickup_status_history', ['id'], unique=False)
    op.create_table('processing_records',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pickup_id', sa.Integer(), nullable=False),
    sa.Column('recycler_id', sa.Integer(), nullable=False),
    sa.Column('decision', sa.String(length=50), nullable=False),
    sa.Column('outcome', pickupstatus_enum, nullable=True),
    sa.Column('processing_notes', sa.Text(), nullable=True),
    sa.Column('revenue_generated', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['pickup_id'], ['pickup_requests.id'], ),
    sa.ForeignKeyConstraint(['recycler_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('pickup_id')
    )
    op.create_index(op.f('ix_processing_records_id'), 'processing_records', ['id'], unique=False)
    op.create_table('recycler_inventory',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recycler_id', sa.Integer(), nullable=False),
    sa.Column('pickup_id', sa.Integer(), nullable=False),
    sa.Column('item_description', sa.Text(), nullable=True),
    sa.Column('weight_kg', sa.Float(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['pickup_id'], ['pickup_requests.id'], ),
    sa.ForeignKeyConstraint(['recycler_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recycler_inventory_id'), 'recycler_inventory', ['id'], unique=False)
    op.create_table('recycler_payments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pickup_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('recycler_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('waste_item', sa.String(length=500), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['pickup_id'], ['pickup_requests.id'], ),
    sa.ForeignKeyConstraint(['recycler_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recycler_payments_id'), 'recycler_payments', ['id'], unique=False)
    op.create_table('rewards',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('pickup_id', sa.Integer(), nullable=False),
    sa.Column('points', sa.Integer(), nullable=False),
    sa.Column('co2_saved_kg', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['pickup_id'], ['pickup_requests.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rewards_id'), 'rewards', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # Only use on a fresh, disposable database. Never downgrade live data.
    op.drop_index(op.f('ix_rewards_id'), table_name='rewards')
    op.drop_table('rewards')
    op.drop_index(op.f('ix_recycler_payments_id'), table_name='recycler_payments')
    op.drop_table('recycler_payments')
    op.drop_index(op.f('ix_recycler_inventory_id'), table_name='recycler_inventory')
    op.drop_table('recycler_inventory')
    op.drop_index(op.f('ix_processing_records_id'), table_name='processing_records')
    op.drop_table('processing_records')
    op.drop_index(op.f('ix_pickup_status_history_id'), table_name='pickup_status_history')
    op.drop_table('pickup_status_history')
    op.drop_index(op.f('ix_pickup_reviews_id'), table_name='pickup_reviews')
    op.drop_table('pickup_reviews')
    op.drop_index(op.f('ix_collector_proofs_id'), table_name='collector_proofs')
    op.drop_table('collector_proofs')
    op.drop_index(op.f('ix_waste_images_id'), table_name='waste_images')
    op.drop_table('waste_images')
    op.drop_index(op.f('ix_pickup_requests_id'), table_name='pickup_requests')
    op.drop_table('pickup_requests')
    op.drop_index(op.f('ix_waste_uploads_id'), table_name='waste_uploads')
    op.drop_table('waste_uploads')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_pricing_rules_id'), table_name='pricing_rules')
    op.drop_table('pricing_rules')
    op.drop_index(op.f('ix_app_config_id'), table_name='app_config')
    op.drop_table('app_config')
    # ### end Alembic commands ###
    if op.get_bind().dialect.name == 'postgresql':
        for enum_type in (pickupstatus_enum, wastecategory_enum, userrole_enum):
            enum_type.drop(op.get_bind(), checkfirst=True)
