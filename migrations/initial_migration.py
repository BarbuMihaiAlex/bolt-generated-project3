"""
Initial database migration for the containers plugin.
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    # Modify ContainerChallengeModel
    with op.batch_alter_table('container_challenge_model') as batch_op:
        # First add the new columns
        batch_op.add_column(sa.Column('port_range_start', sa.Integer))
        batch_op.add_column(sa.Column('port_range_end', sa.Integer))
        
        # If you want to migrate existing data:
        # 1. Copy data from 'port' to 'port_range_start'
        # 2. Set 'port_range_end' equal to 'port'
        # 3. Then drop the old 'port' column
        
    # Modify ContainerInfoModel
    with op.batch_alter_table('container_info_model') as batch_op:
        # Add the new ports column
        batch_op.add_column(sa.Column('ports', sa.Text))
        
        # If you want to migrate existing data:
        # 1. Convert single 'port' value to JSON format in 'ports'
        # 2. Then drop the old 'port' column

def downgrade():
    # Remove new columns if needed to rollback
    with op.batch_alter_table('container_challenge_model') as batch_op:
        batch_op.drop_column('port_range_start')
        batch_op.drop_column('port_range_end')
        
    with op.batch_alter_table('container_info_model') as batch_op:
        batch_op.drop_column('ports')
