"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-10-29 23:23:24.982332
"""
from alembic import op
import sqlalchemy as sa


revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Databases from before Alembic was added were created by Base.metadata.create_all
    # and already have these tables; adopt them as-is instead of failing.
    if sa.inspect(op.get_bind()).has_table("users"):
        return

    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)

    op.create_table('cars',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('plate', sa.String(), nullable=False),
    sa.Column('make', sa.String(), nullable=False),
    sa.Column('model', sa.String(), nullable=False),
    sa.Column('model_year', sa.Integer(), nullable=True),
    sa.Column('current_odometer', sa.Integer(), nullable=False),
    sa.Column('is_favorite', sa.Boolean(), nullable=False),
    sa.Column('vin', sa.String(), nullable=True),
    sa.Column('engine_model', sa.String(), nullable=True),
    sa.Column('engine_volume', sa.Double(), nullable=True),
    sa.Column('transmission', sa.Enum('MANUAL', 'AUTOMATIC', 'CVT', 'DCT', name='transmissiontype'), nullable=True),
    sa.Column('drive_type', sa.Enum('FWD', 'RWD', 'AWD', name='drivetype'), nullable=True),
    sa.Column('tire_size', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('vin')
    )
    with op.batch_alter_table('cars', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_cars_plate'), ['plate'], unique=True)
        batch_op.create_index(batch_op.f('ix_cars_user_id'), ['user_id'], unique=False)

    op.create_table('inspections',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('car_id', sa.Integer(), nullable=False),
    sa.Column('renewed_date', sa.Date(), nullable=False),
    sa.Column('expiry_date', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['car_id'], ['cars.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('inspections', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_inspections_car_id'), ['car_id'], unique=False)

    op.create_table('insurances',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('car_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('CIVIL_LIABILITY', 'CASCO', name='insurancetype'), nullable=False),
    sa.Column('renewed_date', sa.Date(), nullable=False),
    sa.Column('expiry_date', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['car_id'], ['cars.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('insurances', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_insurances_car_id'), ['car_id'], unique=False)

    op.create_table('refuelings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('car_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('fuel_type', sa.Enum('PETROL', 'LPG', 'CNG', 'DIESEL', 'ELECTRICITY', name='fueltype'), nullable=False),
    sa.Column('cost_eur', sa.Double(), nullable=False),
    sa.Column('quantity_liters', sa.Double(), nullable=True),
    sa.Column('odometer', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['car_id'], ['cars.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('refuelings', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_refuelings_car_id'), ['car_id'], unique=False)

    op.create_table('services',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('car_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('parts_list', sa.JSON(), nullable=True),
    sa.Column('part_numbers', sa.JSON(), nullable=True),
    sa.Column('next_service_date', sa.Date(), nullable=True),
    sa.Column('next_service_odometer', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['car_id'], ['cars.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_services_car_id'), ['car_id'], unique=False)

    op.create_table('vignettes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('car_id', sa.Integer(), nullable=False),
    sa.Column('country_code', sa.String(), nullable=False),
    sa.Column('date_start', sa.Date(), nullable=False),
    sa.Column('date_end', sa.Date(), nullable=False),
    sa.Column('price', sa.Double(), nullable=True),
    sa.Column('currency', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('vehicle_type', sa.String(), nullable=True),
    sa.Column('vehicle_class', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['car_id'], ['cars.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('vignettes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_vignettes_car_id'), ['car_id'], unique=False)



def downgrade() -> None:
    with op.batch_alter_table('vignettes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_vignettes_car_id'))

    op.drop_table('vignettes')
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_services_car_id'))

    op.drop_table('services')
    with op.batch_alter_table('refuelings', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_refuelings_car_id'))

    op.drop_table('refuelings')
    with op.batch_alter_table('insurances', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_insurances_car_id'))

    op.drop_table('insurances')
    with op.batch_alter_table('inspections', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_inspections_car_id'))

    op.drop_table('inspections')
    with op.batch_alter_table('cars', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_cars_user_id'))
        batch_op.drop_index(batch_op.f('ix_cars_plate'))

    op.drop_table('cars')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')
