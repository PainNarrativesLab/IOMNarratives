"""
Contains the sqlalchemy models for the database
Created by adam on 11/11/15

In order to use this, import the module and
create a sqlalchemy engine named 'engine' then do:

# connect to db
from sqlalchemy.orm import sessionmaker

# ORM's handle to database at global level
Session = sessionmaker(bind=engine)

Finally when ready to make queries, do:
#connect to db: Local object
session = Session()

The local session object is then used to make queries like:
s = session.query(Testimony).all() # All testimony objects
s1 = session.query(Testimony).order_by(Testimony.quoteID)[0:99] # First 100 vignettes

"""
__author__ = 'adam'

from sqlalchemy import Table, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


# Create base for models
Base = declarative_base()


condition_testimony_table = Table('iom_conditionsXtestimony', Base.metadata,
                                  Column('quoteID', Integer, ForeignKey('iom_testimony.quoteID')),
                                  Column('conditionID', Integer, ForeignKey('iom_conditions.conditionID'))
                                  )


class Testimony(Base):
    """
    Properties:
        condition_ids: Tuple of condition ids identified in vignette
        condition_names: Tuple of condition names identified in vignette
    """
    __tablename__ = "iom_testimony"
    quoteID = Column(Integer, primary_key=True)
    respondentID = Column(Integer)
    questionNumber = Column(Integer)
    quoteText = Column(String)
    # many to many Testimony<->Condition
    conditions = relationship('Condition', secondary=condition_testimony_table, backref="iom_testimony")

    def get_condition_ids(self):
        """
        Returns a tuple of unique condition ids identified for
        the vignette
        """
        self.condition_ids = []
        [self.condition_ids.append(c.conditionID) for c in self.conditions]
        self.condition_ids = tuple(set(self.condition_ids))
        return self.condition_ids

    def get_condition_names(self):
        """
        Returns a tuple of any condition names identified for
        the vignette
        """
        self.condition_names = []
        [self.condition_names.append(c.conditionName) for c in self.conditions]
        self.condition_names = tuple(set(self.condition_names))
        return self.condition_names



class Condition(Base):
    """
    Properties:
        quote_ids: List of associated vignette ids
        respondent_ids: List of associated respondent ids
    """
    __tablename__ = 'iom_conditions'
    conditionID = Column(Integer, primary_key=True)
    conditionName = Column(String)
    # many to many Condition<->Alias
    aliases = relationship('Alias', backref='iom_conditions')
    # many to many Testimony<->Condition
    testimony = relationship('Testimony', secondary=condition_testimony_table, backref="iom_conditions")

    def get_vignette_ids(self):
        """
        Returns a tuple of quote ids wherein the condition is mentioned
        """
        self.quote_ids = []
        [self.quote_ids.append(t.quoteID) for t in self.testimony]
        return tuple(self.quote_ids)

    def get_respondent_ids(self):
        """
        Returns a tuple of ids of respondents who mentioned the condition
        Also sets attribute respondent_ids
        """
        self.respondent_ids = []
        [self.respondent_ids.append(t.respondentID) for t in self.testimony]
        self.respondent_ids = tuple(set(self.respondent_ids))
        return self.respondent_ids


class Alias(Base):
    __tablename__ = 'iom_conditionAliases'
    aliasID = Column(Integer, primary_key=True)
    conditionAlias = Column(String)
    conditionID = Column(Integer, ForeignKey('iom_conditions.conditionID'))
    condition = relationship('Condition', backref='iom_conditionAliases')


class Provider(Base):
    """
    Properties:
        respondentID: Integer respondent id
        concatenated_text: All vignette text for the person
    """
    __tablename__ = "iom_providers"
    respondentID = Column(Integer, ForeignKey('iom_testimony.respondentID'), primary_key=True)
    # Relation to testimony table
    vignettes = relationship('Testimony', backref='iom_testimony', uselist=True)

    def get_concatenated_responses(self):
        """
        Concatenates all the vignette text for the provider
        and returns it.
        """
        self.concatenated_text = ""

        def addText(text):
            self.concatenated_text += text

        [addText(t.quoteText) for t in self.vignettes]
        return self.concatenated_text


class Patient(Base):
    """
    Properties:
        respondentID: Integer respondent id
        concatenated_text: All vignette text for the person
    """
    __tablename__ = "iom_patients"
    respondentID = Column(Integer, ForeignKey('iom_testimony.respondentID'), primary_key=True)
    # Relation to testimony table
    vignettes = relationship(Testimony, uselist=True)

    def get_concatenated_responses(self):
        """
        Concatenates all the vignette text for the provider
        and returns it.
        """
        self.concatenated_text = ""

        def addText(text):
            self.concatenated_text += text

        [addText(t.quoteText) for t in self.vignettes]
        return self.concatenated_text

