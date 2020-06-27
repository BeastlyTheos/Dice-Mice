from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Alias(Base):
	__tablename__ = 'alias'
	user = Column(Integer, primary_key=True)
	name = Column(String(32), primary_key=True)
	definition = Column(String(512))

	def __repr__(self):
		return f"Alias {self.name} for user {self.user}"
