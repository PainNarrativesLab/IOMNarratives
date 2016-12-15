import os
import unittest

# constants
BASE = os.getenv("HOME") + '/Dropbox/PainNarrativesLab'
CREDENTIAL_FILE = '%s/private_credentials/iom_sql_local_credentials.xml' % BASE
TEST = True
DB_NAME = 'iom_data_dev'  # if TEST else 'iom_classify'

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



class PersonTest(unittest.TestCase):

    def test_get_concatenated_responses_for_html(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
