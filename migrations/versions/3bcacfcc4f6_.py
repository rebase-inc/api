"""empty message

Revision ID: 3bcacfcc4f6
Revises: None
Create Date: 2015-08-02 17:10:52.866988

"""

# revision identifiers, used by Alembic.
revision = '3bcacfcc4f6'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('organization',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('talent_pool',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('term_sheet',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('legalese', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('last_seen', sa.DateTime(), nullable=False),
    sa.Column('admin', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('work',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('state', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('auction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('duration', sa.Integer(), nullable=False),
    sa.Column('finish_work_by', sa.DateTime(), nullable=False),
    sa.Column('redundancy', sa.Integer(), nullable=False),
    sa.Column('term_sheet_id', sa.Integer(), nullable=False),
    sa.Column('state', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['term_sheet_id'], ['term_sheet.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('credit',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('paid', sa.Boolean(), nullable=False),
    sa.Column('work_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['work_id'], ['work.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('debit',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('paid', sa.Boolean(), nullable=False),
    sa.Column('work_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['work_id'], ['work.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('mediation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dev_answer', sa.String(), nullable=True),
    sa.Column('client_answer', sa.Integer(), nullable=True),
    sa.Column('timeout', sa.DateTime(), nullable=False),
    sa.Column('work_id', sa.Integer(), nullable=False),
    sa.Column('state', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['work_id'], ['work.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('project',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('review',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('work_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['work_id'], ['work.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('arbitration',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('mediation_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['mediation_id'], ['mediation.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('code_repository',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['project.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('contractor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('busyness', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['role.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('manager',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['role.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('remote_project',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['project.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ticket',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('discriminator', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ticket_set',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('auction_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['auction_id'], ['auction.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bank_account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=True),
    sa.Column('contractor_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('routing_number', sa.Integer(), nullable=False),
    sa.Column('account_number', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['contractor_id'], ['contractor.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bid',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('auction_id', sa.Integer(), nullable=False),
    sa.Column('contractor_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['auction_id'], ['auction.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['contractor_id'], ['contractor.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('code_clearance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('pre_approved', sa.Boolean(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('contractor_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['contractor_id'], ['contractor.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('feedback',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('contractor_id', sa.Integer(), nullable=False),
    sa.Column('auction_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['auction_id'], ['auction.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['contractor_id'], ['contractor.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('github_project',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['remote_project.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('internal_ticket',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['ticket.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('nomination',
    sa.Column('contractor_id', sa.Integer(), nullable=False),
    sa.Column('ticket_set_id', sa.Integer(), nullable=False),
    sa.Column('auction_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['auction_id'], ['auction.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['contractor_id'], ['contractor.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['ticket_set_id'], ['ticket_set.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('contractor_id', 'ticket_set_id')
    )
    op.create_table('remote_ticket',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['ticket.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('remote_work_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['contractor.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('skill_requirement',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['ticket.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('skill_set',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['contractor.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ticket_snapshot',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('ticket_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['ticket_id'], ['ticket.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bid_limit',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('ticket_set_id', sa.Integer(), nullable=True),
    sa.Column('ticket_snapshot_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['ticket_set_id'], ['ticket_set.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['ticket_snapshot_id'], ['ticket_snapshot.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('review_id', sa.Integer(), nullable=True),
    sa.Column('mediation_id', sa.Integer(), nullable=True),
    sa.Column('ticket_id', sa.Integer(), nullable=True),
    sa.Column('feedback_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['feedback_id'], ['feedback.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mediation_id'], ['mediation.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['review_id'], ['review.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['ticket_id'], ['ticket.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('contract',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['bid.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('github_account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('remote_work_history_id', sa.Integer(), nullable=True),
    sa.Column('user_name', sa.String(), nullable=False),
    sa.Column('auth_token', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['remote_work_history_id'], ['remote_work_history.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('github_ticket',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['remote_ticket.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('job_fit',
    sa.Column('contractor_id', sa.Integer(), nullable=False),
    sa.Column('ticket_set_id', sa.Integer(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['contractor_id', 'ticket_set_id'], ['nomination.contractor_id', 'nomination.ticket_set_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('contractor_id', 'ticket_set_id')
    )
    op.create_table('work_offer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('work_id', sa.Integer(), nullable=True),
    sa.Column('bid_id', sa.Integer(), nullable=True),
    sa.Column('contractor_id', sa.Integer(), nullable=False),
    sa.Column('ticket_snapshot_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['bid_id'], ['bid.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['contractor_id'], ['contractor.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['ticket_snapshot_id'], ['ticket_snapshot.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['work_id'], ['work.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ticket_match',
    sa.Column('skill_requirement_id', sa.Integer(), nullable=False),
    sa.Column('skill_set_id', sa.Integer(), nullable=False),
    sa.Column('contractor_id', sa.Integer(), nullable=True),
    sa.Column('ticket_set_id', sa.Integer(), nullable=True),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['contractor_id', 'ticket_set_id'], ['job_fit.contractor_id', 'job_fit.ticket_set_id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['skill_requirement_id'], ['skill_requirement.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['skill_set_id'], ['skill_set.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('skill_requirement_id', 'skill_set_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ticket_match')
    op.drop_table('work_offer')
    op.drop_table('job_fit')
    op.drop_table('github_ticket')
    op.drop_table('github_account')
    op.drop_table('contract')
    op.drop_table('comment')
    op.drop_table('bid_limit')
    op.drop_table('ticket_snapshot')
    op.drop_table('skill_set')
    op.drop_table('skill_requirement')
    op.drop_table('remote_work_history')
    op.drop_table('remote_ticket')
    op.drop_table('nomination')
    op.drop_table('internal_ticket')
    op.drop_table('github_project')
    op.drop_table('feedback')
    op.drop_table('code_clearance')
    op.drop_table('bid')
    op.drop_table('bank_account')
    op.drop_table('ticket_set')
    op.drop_table('ticket')
    op.drop_table('remote_project')
    op.drop_table('manager')
    op.drop_table('contractor')
    op.drop_table('code_repository')
    op.drop_table('arbitration')
    op.drop_table('role')
    op.drop_table('review')
    op.drop_table('project')
    op.drop_table('mediation')
    op.drop_table('debit')
    op.drop_table('credit')
    op.drop_table('auction')
    op.drop_table('work')
    op.drop_table('user')
    op.drop_table('term_sheet')
    op.drop_table('talent_pool')
    op.drop_table('organization')
    ### end Alembic commands ###
