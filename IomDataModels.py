"""
Contains the database connection tools and sqlalchemy models for iom database
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

import os
import sys
import xml.etree.ElementTree as ET

# sqlalchemy tools
import sqlalchemy
from sqlalchemy import Table, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# connecting to db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Connection(object):
    """
    Parent class for creating sqlalchemy engines, session objects,
    and other db interaction stuff behind the scenes from a file
    holding credentials

    Attributes:
        engine: sqlalchemy engine instance
        session: sqlalchemy local session object. This is the property that should do most work
        _credential_file: String path to file with db connection info
        _username: String db username
        _password: String db password
        _server: String db server
        _port: db port
        _db_name: String name of db
    """

    def __init__(self, credential_file=None):
        """
        Loads db connection credentials from file and returns a mysql sqlalchemy engine
        Args:
            :param credential_file: String path to the credential file to use
        Returns:
            :return: sqlalchemy.create_engine Engine instance
        """
        self._credential_file = credential_file
        self._load_credentials()
        self._make_engine()

    def _load_credentials(self):
        """
        Opens the credentials file and loads the attributes
        """
        if self._credential_file is not None:
            credentials = ET.parse(self._credential_file)
            self._server = credentials.find('db_host').text
            self._port = credentials.find('db_port').text
            if self._port is not None:
                self._port = int(self._port)
            self._username = credentials.find('db_user').text
            self._db_name = credentials.find('db_name').text
            self._password = credentials.find('db_password').text

    def _make_engine(self):
        """
        Creates the sqlalchemy engine and stores it in self.engine
        """
        raise NotImplementedError


class MySqlConnection(Connection):
    """
    Uses the MySQL-Connector-Python driver (pip install MySQL-Connector-Python driver)
    """

    def __init__(self, credential_file):
        self._driver = '+mysqlconnector'
        super().__init__(credential_file)

    def _make_engine(self):
        if self._port:
            server = "%s:%s" % (self._server, self._port)
        else:
            server = self._server
        self._dsn = "mysql%s://%s:%s@%s/%s" % (self._driver, self._username, self._password, server, self._db_name)
        self.engine = create_engine(self._dsn)


class SqliteConnection(Connection):
    """
    Makes a connection to an in memory sqlite database.
    Note that does not actually populate the database. That
    requires a call to: Base.metadata.create_all(SqliteConnection)
    """
    def __init__(self):
        super().__init__()

    def _make_engine(self):
        self.engine = create_engine('sqlite:///:memory:', echo=True)


class BaseDAO(object):
    """
    Parent class for database interactions.
    The parent will hold the single global connection (i.e. sqlalchemy Session)
    to the db.
    Instance classes will have their own session instances
    Attributes:
        global_session: (class attribute) A sqlalchemy configurable sessionmaker factory (sqlalchemy.orm.session.sessionmaker)
            bound to the engine. Is not itself a session. Instead, it needs to be instantiated: DAO.global_session()
        engine: sqlalchemy.engine.base.Engine instance
    """
    global_session = None

    def __init__(self, engine):
        assert(isinstance(engine, sqlalchemy.engine.base.Engine))
        self.engine = engine
        if BaseDAO.global_session is None:
            BaseDAO._create_session(engine)

    @staticmethod
    def _create_session(engine):
        """
        Instantiates the sessionmaker factory into the global_session attribute
        """
        BaseDAO.global_session = sqlalchemy.orm.sessionmaker(bind=engine)


class DAO(BaseDAO):
    """
    example instance. Need to use metaclass to ensure that
    all instances of DAO do this
    """
    def __init__(self, engine):
        assert(isinstance(engine, sqlalchemy.engine.base.Engine))
        super().__init__(engine)
        self.session = BaseDAO.global_session()


#######################################
# Database models                     #
#######################################
# Base class that maintains the catalog of tables and classes in db
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


class Person(object):
    """
    Parent class for Providers, Respondents, and Patients which contains
    methods for retrieving data for those objects to inherit

    Properties:
        concatenated_text: String of all vignettes attributed to the
            person. Only available after get_concatenated_responses called
        quote_ids: Tuple of all ids of vignettes attributed to the person. Only
            available after get_vignette_ids called
        condition_ids: Tuple of all condition ids attributed to the person. Only
            available after get_condition_ids called.
        condition_names: Tuple of string names of conditions attributed to the person. Only
            available after get_condition_names called.

    TODO: Consider adding __get__ method which checks if the relevant property has been set
        and then calls the relevant method if not.
    """

    def get_concatenated_responses(self):
        """
        Concatenates all the vignette text for the respondent
        and returns it.
        """
        self.concatenated_text = ""

        def addText(text):
            self.concatenated_text += text

        [addText(t.quoteText) for t in self.vignettes]
        return self.concatenated_text

    def get_vignette_ids(self):
        """
        Returns a tuple of the quote ids belonging to the respondent
        """
        self.quote_ids = []
        [self.quote_ids.append(t.quoteID) for t in self.vignettes]
        return tuple(self.quote_ids)

    def get_condition_ids(self):
        """
        Returns a tuple of unique condition ids identified for
        the person
        """
        self.condition_ids = []

        for t in self.vignettes:
            # iterate through each condition associated with each vignette
            [self.condition_ids.append(ci) for ci in t.get_condition_ids()]

        self.condition_ids = tuple(set(self.condition_ids))
        return self.condition_ids

    def get_condition_names(self):
        """
        Returns a tuple of any condition names identified for
        the vignette
        """
        self.condition_names = []

        for t in self.vignettes:
            # iterate through each condition associated with each vignette
            [self.condition_names.append(cn) for cn in t.get_condition_names()]

        self.condition_names = tuple(set(self.condition_names))

        return self.condition_names


class Provider(Base, Person):
    """
    Properties:
        respondentID: Integer respondent id
    """
    __tablename__ = "iom_providers"
    respondentID = Column(Integer, ForeignKey('iom_testimony.respondentID'), primary_key=True)
    # Relation to testimony table
    vignettes = relationship('Testimony', backref='iom_testimony', uselist=True)

    def __init__(self):
        Base.__init__(self)
        Person.__init__(self)


class Patient(Base, Person):
    """
    Properties:
        respondentID: Integer respondent id
    """
    __tablename__ = "iom_patients"
    respondentID = Column(Integer, ForeignKey('iom_testimony.respondentID'), primary_key=True)
    # Relation to testimony table
    vignettes = relationship(Testimony, uselist=True)

    def __init__(self):
        Base.__init__(self)
        Person.__init__(self)


class Respondent(Base, Person):
    """
    Properties:
        respondentID: Integer respondent id
    """
    __tablename__ = "iom_respondents"
    id = Column(Integer, ForeignKey('iom_testimony.respondentID'), primary_key=True)
    # Relation to testimony table
    vignettes = relationship('Testimony', uselist=True)

    def __init__(self):
        Base.__init__(self)
        Person.__init__(self)


if __name__ == '__main__':
    # connect to db
    # ORM's handle to database at global level
    Session = sessionmaker(bind=mysql_engine)