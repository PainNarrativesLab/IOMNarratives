import os
import unittest

# constants
BASE = os.getenv("HOME") + '/Dropbox/PainNarrativesLab'
CREDENTIAL_FILE = '%s/private_credentials/iom_sql_local_credentials.xml' % BASE
TEST = True
DB_NAME = 'iom_classify_dev'  # if TEST else 'iom_classify'

# database orm tools
import sqlalchemy
from sqlalchemy import create_engine

from IomDataModels import Condition, Testimony, Patient, Provider, Respondent #, Alias
import IomDataModels

import VerificationDataModels as VDM

import VerificationDbTools as VDT

# load the db connection info
conn = IomDataModels.MySqlConnection(CREDENTIAL_FILE)
# create the session connection to the iom db
dao = IomDataModels.DAO(conn.engine)

conditions = dao.session.query(Condition).all()
vignettes = dao.session.query(Testimony).all()
patients = dao.session.query(Patient).all()
providers = dao.session.query(Provider).all()
respondents = dao.session.query(Respondent).all()
#aliases = dao.session.query(Alias).all()

# prepare classifier db connection
classify_engine = create_engine('mysql+mysqlconnector://root:''@localhost/%s' % DB_NAME)
classify_global_session = sqlalchemy.orm.sessionmaker(bind=classify_engine)


# Tests to verify correct mapping iom_data -> iom_classify


class RespondentsTest(unittest.TestCase):
    def setUp(self):
        self.session = classify_global_session()
        self.iom_respondent_ids = [r.id for r in respondents]

    def test_all_respondents_added(self):
        """
        Ensures that there is a respondent in the classify db matching each respondent
        in the iom db
        Verifies iom_db -> classify_db
        """
        for respondent in respondents:
            inDb = self.session.query(VDM.CPerson).filter(VDM.CPerson.id == respondent.id).first()
            self.assertEqual(type(inDb), VDM.CPerson)
            self.assertEqual(inDb.id, respondent.id)

    def test_no_extra_respondents(self):
        """
        Checks that the two sets of respondents are the same size and that the classify db
        does not have any respondents not in the iom_data db
        Verifies classify_db -> iom_db
        """
        self.assertTrue(len(self.iom_respondent_ids) > 0)
        self.assertEqual(len(self.iom_respondent_ids), len(respondents))
        for respondent in self.session.query(VDM.CPerson).all():
            self.assertTrue(respondent.id in self.iom_respondent_ids)


class ConditionsTest(unittest.TestCase):
    def setUp(self):
        self.session = classify_global_session()
        self.patient_ids = [p.get_id() for p in patients]

    def test_condition_ids_properly_associated(self):
        """
        Makes sure conditions are property associated across db
        Verifies iom_db -> classify_db

        """
        for respondent in respondents:
            condition_ids = respondent.get_condition_ids()
            if condition_ids and len(condition_ids) > 0:
                # condition_names = respondent.get_condition_names()
                for cid in condition_ids:
                    # Get the corresponding id for the classification db
                    category_id = self.session.query(VDM.CCondition)\
                        .filter(VDM.CCondition.iom_identifier == cid)\
                        .first()\
                        .id

                    attribution = self.session.query(VDT.CAttribution)\
                        .filter(VDT.CAttribution.category_id == category_id)\
                        .filter(VDT.CAttribution.respondent_id == respondent.id)\
                        .first()
                    # Make sure is mentioned by respondent
                    self.assertEquals(attribution.is_mentioned, 1)
                    # We assumed that mention + patient = attribution
                    # So, we check if attributed only if they are a patient
                    if respondent.id in self.patient_ids:
                        self.assertEquals(attribution.is_attributed, 1)
                    else:
                        self.assertEquals(attribution.is_attributed, 0)


if __name__ == '__main__':
    unittest.main()