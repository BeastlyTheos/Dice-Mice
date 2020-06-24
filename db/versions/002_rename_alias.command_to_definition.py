from sqlalchemy import Table, Column, Integer, String, MetaData

meta = MetaData()

alias = Table(
	'alias', meta,
	Column('user', Integer, primary_key=True),
	Column('name', String(32), primary_key=True),
	Column('command', String(512)),
)

c = alias.c.command


def upgrade(migrate_engine):
	meta.bind = migrate_engine
	c.alter(name='definition')
	alias.update()


def downgrade(migrate_engine):
	meta.bind = migrate_engine
	c.alter(name='command')
	alias.update()
