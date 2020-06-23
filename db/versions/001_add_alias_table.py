from sqlalchemy import Table, Column, Integer, String, MetaData

meta = MetaData()

alias = Table(
	'alias', meta,
	Column('user', Integer, primary_key=True),
	Column('name', String(32), primary_key=True),
	Column('command', String(512)),
)


def upgrade(migrate_engine):
	meta.bind = migrate_engine
	alias.create()


def downgrade(migrate_engine):
	meta.bind = migrate_engine
	alias.drop()
