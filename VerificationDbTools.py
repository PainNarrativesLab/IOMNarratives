"""
Created by adam on 12/11/15
"""
__author__ = 'adam'

from sqlalchemy import create_engine

DB_NAME = 'iom_classify_dev' # if TEST  else 'iom_classify'

import sqlalchemy
import VerificationDataModels as VDM

# from sqlalchemy.orm import sessionmaker

classify_engine = create_engine('mysql+mysqlconnector://root:''@localhost/%s' % DB_NAME)

global_session = sqlalchemy.orm.sessionmaker(bind=classify_engine)


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, ForeignKey, Integer, String, Boolean, DateTime

from random import random

Base = declarative_base()


class CAttribution(Base):
    """Attributions of a category to a person
    Note: Can't merge into VerificationDataModels because will conflict with the use of the attributions table there
    """
    __tablename__ = "attributions"
    id = Column(Integer, primary_key=True)

    # respondent = relationship("VerificationDataModels.CPerson", back_populates="attributions")

    # category = relationship("VerificationDataModels.CCategory", back_populates="attributions")

    # The respondent with the property
    respondent_id = Column(Integer)
    # respondent_id = Column(Integer, ForeignKey('respondents.id'))

    # The property potentially attributed to the respondent
    category_id = Column(Integer)
    # category_id = Column(Integer, ForeignKey('category_id'))

    # Whether the property is attributed to the respondent
    is_attributed = Column(Boolean)

    # Whether the property is mentioned by the respondent
    is_mentioned = Column(Boolean)

    # The user who verified the attribution
    # dev
    user_id = Column(Integer)

    # When the attribution was verified
    confirmation = Column(DateTime)

    # When the record was created
    created_at = Column(DateTime)

    # Last time that anything was done to the record
    updated_at = Column(DateTime)

    def __init__(self):
        Base.__init__(self)

        def is_confirmed(self):
            """Whether the attribution has been confirmed
        """
        if self.confirmation and self.user_id:
            return True
        else:
            return False


class ClassificationDbPopulationTools:
    """
    These are tools for adding data from the iom_database into the
    iom_classify database
    """

    def __init__(self):
        self.session = global_session()
        
    def add_iom_respondents_to_classification_db(self, respondents):
        """Iterates through the list of respondents and
        adds them to the db. Also adds a row for each category
        and respondent pair to the attributions table.
        This does NOT add any respondent data to the attributions table other
        than the id.
        In the attributions table, the is_attributed and is_mentioned
        fields are set to their defaults of False.
        """
        categories = self.session.query(VDM.CCategory).all()
        added = 0
        for respondent in respondents:
            # Make the person
            p = VDM.CPerson()
            p.id = respondent.id
            # p.content = respondent.get_concatenated_responses()
            p.content = respondent.get_concatenated_responses_for_html()
            p.categories = categories
            self.session.add(p)
            added += 1
        self.session.commit()
        print("%s respondents added to db" % added)

    def add_patients_to_classification_db(self, patients):
        """Sets the is_attributed value to true for each respondent identified as a patient
        """
        added = 0
        for p in patients:
            row = self.session.query(CAttribution).filter(CAttribution.category_id == 1).filter(CAttribution.respondent_id == p.get_id()).first()
            row.is_attributed = True
            self.session.commit()
            added += 1
        print("%s respondents updated to be patients" % added)

    def add_conditions_to_classification_db(self, patients, respondents):
        """Adds mentions of conditions and attributions
        (assumes: patient + mention -> attribution) to
        the classification db
        :param respondents: 
        :param patients: 
        """
        patient_ids = [p.get_id() for p in patients]
        added = 0
        for respondent in respondents:
            for conditionId in respondent.get_condition_ids():
                # look up the appropriate category object based on the conditionId
                category = self.session.query(VDM.CCategory).filter(VDM.CCategory.iom_identifier == conditionId).first()
                # load the attribution of the category to the respondent
                row = self.session.query(CAttribution).filter(CAttribution.category_id == category.id).filter(CAttribution.respondent_id == respondent.id).first()
                row.is_mentioned = True
                if respondent.id in patient_ids:
                    row.is_attributed = True
                self.session.commit()
            added += 1
        print("%s respondents updated with conditions" % added)

    def add_providers_randomized_to_classification_db(self, providers):
        """This will add attributions of being a provider to the
        classification db. The catch is that the source db does not
        distinguish between provider-personal and provider-professional.
        So this randomly assigns those who have been identified as a provider
        to either provider-persona or provider-professional.
        :type providers: list
        """
        added = 0
        # The current id for 'Provider-professional'
        provider_professional_id = self.session.query(VDM.CCategory).filter(VDM.CCategory.description == 'Provider-professional').first().id
        # The current id for 'Provider-personal'
        provider_personal_id = self.session.query(VDM.CCategory).filter(VDM.CCategory.description == 'Provider-personal').first().id
        # respondent ids of people identified as providers
        provider_ids = [p.get_id() for p in providers]

        for pid in provider_ids:
            if random() < 0.5:
                winning_provider_category_id = provider_professional_id
            else:
                winning_provider_category_id = provider_personal_id
            # Get the attribution record for the winner provider-type
            record = self.session.query(CAttribution).filter(CAttribution.respondent_id == pid).filter(CAttribution.category_id == winning_provider_category_id).first()
            # Set the attribution and save
            record.is_attributed = True
            self.session.commit()
            added += 1
        print("%s respondents updated as providers" % added)

