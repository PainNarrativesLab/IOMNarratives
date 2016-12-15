"""
These are data models for the iom_classify database
Created by adam on 11/29/15
"""
__author__ = 'adam'

# sqlalchemy tools

import sqlalchemy
from sqlalchemy import Table, Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


attributions_table = Table('attributions', Base.metadata,
                           Column('id', Integer, primary_key=True),
                                  Column('respondent_id', Integer, ForeignKey('respondents.id')),
                                  Column('category_id', Integer, ForeignKey('categories.id')),
                           Column('is_attributed', Boolean, default=0),
                           Column('is_mentioned', Boolean, default=0),
                           Column('user_id', Integer, nullable=True),
                           Column('confirmation', DateTime, nullable=True)
            )


# class CAttribution(Base):
#     """Attributions of a category to a person
#     """
#     __tablename__ = "attributions"
#     id = Column(Integer, primary_key=True)
#
#     # The respondent with the property
#     respondent_id = Column(Integer, ForeignKey('respondents.id'))
#
#     # The property potentially attributed to the respondent
#     category_id = Column(Integer, ForeignKey('category_id'))
#
#     # Whether the property is attributed to the respondent
#     is_attributed = Column(Boolean)
#
#     # Whether the property is mentioned by the respondent
#     is_mentioned = Column(Boolean)
#
#     # The user who verified the attribution
#     user_id = Column(Integer, ForeignKey('respondents.id'))
#
#     # When the attribution was verified
#     confirmation = Column(DateTime)
#
#     # When the record was created
#     created_at = Column(DateTime)
#
#     # Last time that anything was done to the record
#     updated_at = Column(DateTime)
#
#     def __init__(self):
#         Base.__init__(self)
#
#         def is_confirmed(self):
#             """Whether the attribution has been confirmed
#             """
#         if self.confirmation and self.user_id:
#             return True
#         else:
#             return False
#


class CPerson(Base):
    """Properties:
        content: String of all vignettes attributed to the
            person. Only available after get_concatenated_responses called
        id: The person's id number. From iom_testimony.respondents.id
        condition_ids: Tuple of all condition ids attributed to the person. Only
            available after get_condition_ids called.
        condition_names: Tuple of string names of conditions attributed to the person. Only
            available after get_condition_names called.
    """
    __tablename__ = "respondents"
    id = Column(Integer, primary_key=True)
    content = Column(String)

    # Relation to attributions table
    #  attributions = relationship('attributions', backref='respondentsAtts', uselist=True)

    categories = relationship('CCategory', secondary=attributions_table, backref='respondentCats')

    # Relation to reviews table
    #reviews = relationship('reviews', backref='respondentsRevs', uselist=True)

    def __init__(self):
        Base.__init__(self)
        # initialize condition related stuff
        self._conditions = []
        self.attributed_conditions = [] # List of CCondition objects
        self._attributed_condition_ids = []
        self._attributed_condition_names = []

        self.mentioned_conditions = [] # List of CCondition objects
        self._mentioned_condition_ids = []
        self._mentioned_condition_names = []

        # initialize sex related stuff
        self._sex = []
        self._is_male = False
        self._is_female = False

        # initialize meds related stuff
        self._meds = []
        self._mentions_opioids = False
        self._uses_opioids = False

        # initialize patient-or-provider stuff
        self._patient_provider = []
        self._is_patient = False
        self._is_provider_personal = False
        self._is_provider_professional = False

        self._sort_conditions()

# def _sort_categories(self):
#     """
#     Called on init, this searches through categories and
#     pushes the attributions into the appropriate lists
#     """
#     for c in self.categories:
#         if c.is_condition():
#             pass # Will do this seperately
#         elif c.is_sex():
#             self._sex.append(c)
#         elif c.is_patient_provider():
#             self._patient_provider.append(c)
#         elif c.is_meds():
#             self._meds.append(c)

    def _sort_conditions(self):
        """
        Called on init, this searches through categories and
        pushes the attributions into the appropriate list
        """
        if len(self._conditions) is 0:
            for c in self.categories:
                if c.is_condition():
                    self._conditions.append(c)
                    if c.is_attributed():
                        self.attributed_conditions.append(c)
                        self._attributed_condition_ids.append(c.get_id())
                        self._attributed_condition_names.append(c.description)
                    if c.is_mentioned():
                        self.mentioned_conditions.append(c)
                        self._mentioned_condition_ids.append(c.get_id())
                        self._mentioned_condition_names.append(c.description)

    def _sort_sex(self):
        """
        Determines the sex of the respondent, if known
        """
        if len(self._sex) is 0:
            for c in self.categories:
                if c.is_sex():
                    self._sex.append(c)
            for s in self._sex:
                if s.description is 'Male':
                    self._is_male = True
                elif s.description is 'Female':
                    self._is_female = True

    def _sort_patient_provider(self):
        """
        Determines whether the person is a patient or provider
        """
        if len(self._patient_provider) is 0:
            for c in self.categories:
                if c.is_patient_provider():
                    self._patient_provider.append(c)
                for s in self._patient_provider:
                    if s.description is 'Patient':
                        self._is_patient = True
                    if s.description is 'Provider-professional':
                        self._is_provider_professional = True
                    if s.description is 'Provider-personal':
                        self.is_provider_personal = True

    def _sort_meds(self):
        """
        Determines whether the person mentions or says they use opioids"""
        if len(self._meds) is 0:
            for c in self.categories:
                if c.is_meds():
                    self._meds.append(c)
                for s in self._meds:
                    if s.is_mentioned():
                        self._mentions_opioids = True
                    if s.uses_opioids():
                        self._uses_opioids = True
    @property
    def is_male(self):
        """Whether the person is described as being male
        """
        self._sort_sex()
        return self._is_male

    @property
    def is_female(self):
        """Whether the person is described as being female
        """
        self._sort_sex()
        return self._is_female

    @property
    def is_patient(self):
        """Whether the person is described as sufferring from a chronic
        pain condition
        """
        self._sort_patient_provider()
        return self._is_patient

    @property
    def is_provider_personal(self):
        """Whether the person cares for a loved one with a chronic pain condition
        """
        self._sort_patient_provider()
        return self._is_provider_personal

    @property
    def is_provider_professional(self):
        """Whether the person cares for people with chronic pain conditions in a professional
        capaticity"""
        self._sort_patient_provider()
        return self.is_provider_professional

    @property
    def mentions_opioids(self):
        """Whether the person mentions opioids"""
        self._sort_meds()
        return self._mentions_opioids

    @property
    def uses_opioids(self):
        """Whether the person says they use opioids"""
        self._sort_meds()
        return self._uses_opioids

    @property
    def mentioned_condition_ids(self):
        """
        Returns a tuple of unique condition ids mentioned for
        the person
        """
        return tuple(set(self._mentioned_condition_ids))

    @property
    def attributed_condition_ids(self):
        """
        Returns a tuple of unique condition ids the person said
        they had
        """
        return tuple(set(self._attributed_condition_ids))

    @property
    def mentioned_condition_names(self):
        """
        Returns a tuple of any condition names which were mentioned by for
        the person
        """
        return tuple(set(self._mentioned_condition_names))

    @property
    def attributed_condition_names(self):
        return tuple(set(self._attributed_condition_names))

    def get_concatenated_responses(self):
        """
        Returns the concatenated text of all the vignettes for the respondent.
        """
        return self.content

    def get_id(self):
        """Getter for person's respondent id
        :return: int
        """
        if hasattr(self, 'respondent_id'):
            return self.respondentID
        elif hasattr(self, 'id'):
            return self.id
        else:
            raise Exception


def CategoryFactory(kind):
    if 'kind' is 'condition':
        return CCondition()
    elif 'kind' is 'sex':
        return CSex()
    elif 'kind' is 'meds':
        return CMeds()
    elif 'kind' is 'patientProvider':
        return CPatientProvider()


class CCategory(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    iom_identifier = Column(Integer)
    description = Column(String)
    section = Column(String)

    # many to many Condition<->Respondents
    #  respondents = relationship('CPerson', secondary=attributions_table2, backref='categories')

    def __init__(self):
        Base.__init__(self)

    @property
    def kind(self):
        self.section

    def is_condition(self):
        if self.section is 'condition':
            return True
        return False

    def is_sex(self):
        if self.section is 'sex':
            return True
        return False

    def is_meds(self):
        if self.section is 'meds':
            return True
        return False

    def is_patient_provider(self):
        if self.section is 'patientProvider':
            return True
        return False


class CMentionable(CCategory):
    """The sort of thing which can be mentioned or attributed
    """
    def __init__(self):
        CCategory.__init__(self)
        #dev self._check_consistency()

    def is_attributed(self):
        raise NotImplemented

    def is_mentioned(self):
        raise NotImplemented

    def _check_consistency(self):
        """
        Helper to make sure an inconsistent result didn't sneak in
        """
        if self.is_mentioned is False and self.is_attributed is True:
            raise Exception


class CCondition(CMentionable):
    """Category of the subtype section
    Properties:
        quote_ids: List of associated vignette ids
        respondent_ids: List of associated respondent ids
    """
    def __init__(self):
        CMentionable.__init__(self)


class CSex(CCategory):
    """
    Category of the subtype section
    Properties:
        quote_ids: List of associated vignette ids
        respondent_ids: List of associated respondent ids
    """
    def __init__(self):
        CCategory.__init__(self)

    def is_male(self):
        """
        Returns True if the person is identified as male
        """
        raise NotImplemented

    def is_female(self):
        """
        Returns True if the person is identified as female
        """
        raise NotImplemented


class CMeds(CMentionable):
    """
    Whether the person mentions opioids
    """
    def __init__(self):
        CMentionable.__init__(self)


class CPatient(CCategory):
    """
    Whether the person is a patient
    """
    def __init__(self):
        CCategory.__init__(self)


class CProvider(CCategory):
    """
    Whether the person is a provider
    """
    def __init__(self):
        CCategory.__init__(self)

