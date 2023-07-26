import bcrypt
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class UserItem(Base):
  __tablename__ = 'users'

  user_id = Column('user_id', Integer, primary_key=True)
  first = Column('first', String, nullable=False)
  middle = Column('middle', String)
  last = Column('last', String)
  email = Column('email', String, unique=True, nullable=False)
  password = Column('_password', String(60), nullable=False)
  username = Column('username', String(42), unique=True)

  def __repr__(self):
    return f'<User {self.first} {self.last} ({self.user_id})>'

  def set_password(self, password):
    encoded = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(encoded, salt).decode('utf-8')

  def check_password(self, password):
    password_to_check = password.encode('utf-8')
    stored_password = self.password.encode('utf-8')
    return bcrypt.checkpw(password_to_check, stored_password)

class AgentItem(Base):
  __tablename__ = 'agents'

  agent_id = Column('agent_id', Integer, primary_key=True)
  name = Column('name', String(50), unique=True, nullable=False)
  use_case = Column('use_case', String, unique=True)

  def __repr__(self):
    return f'<Agent {self.name} ({self.agent_id})>'

class UtteranceItem(Base):
  __tablename__ = 'utterances'

  utt_id = Column('utt_id', Integer, primary_key=True)
  speaker = Column('speaker', String(10), nullable=False)
  text = Column('text', String, nullable=False)
  short_embed = Column('short_embed', Vector(384), nullable=False)
  medium_embed = Column('medium_embed', Vector(768))
  long_embed = Column('long_embed', Vector(1536))
  aggregation = Column('aggregation', String)
  operations = Column('operations', String)
  dact_id = Column('dact_id', Integer, ForeignKey('dialogue_acts.dact_id'))
  # state_id = Column('state_id', Integer, ForeignKey('states.state_id'))
  # agent_id = Column('agent_id', Integer, ForeignKey('agents.agent_id'))

  def __repr__(self):
    return f'<{self.speaker}: {self.text} ({self.utt_id})>'


class IntentItem(Base):
  __tablename__ = 'intents'

  intent_id = Column('intent_id', Integer, primary_key=True)
  level = Column('level', String(8), nullable=False)
  intent_name = Column('intent_name', String(32), nullable=False)
  description = Column('description', String)

  def __repr__(self):
    return f'<{self.intent_name} ({self.intent_id})>'

class DialogueActItem(Base):
  __tablename__ = 'dialogue_acts'

  dact_id = Column('dact_id', Integer, primary_key=True)
  dact = Column('dact', String(64), nullable=False)
  dax = Column('dax', String(4), nullable=False)
  description = Column('description', String)
  intent_id = Column('intent_id', Integer, ForeignKey('intents.intent_id'))
  agent_id = Column('agent_id', Integer, ForeignKey('agents.agent_id'))

  def __repr__(self):
    return f'<{self.dact} ({self.dact_id})>'


class StateItem(Base):
  __tablename__ = 'states'

  state_id = Column('state_id', Integer, primary_key=True)
  table_name = Column('table_name', String)
  table_cols = Column('table_cols', String)
  aggregation = Column('aggregation', String)
  operations = Column('operations', String)
  campaigns = Column('campaigns', String)
  channels = Column('channels', String)
  metric = Column('metric', Float)
