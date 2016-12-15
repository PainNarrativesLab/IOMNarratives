"""
This checks the consistency of the IOM data to be imported and
ensures that the contents of the database after import are the
same as the IOM files
"""
import os
import unittest

import pandas as pd
import numpy as np


# The largest quote id
MAX_QUOTE_ID = 4865

folder = "%s/Dropbox/Narrative pain project/Original records/ImportRedo 2016-01-10/" % os.getenv("HOME")
sheets = [
    "Add to end.xlsx",
    "PAF 2 Testimony SpellChecked.xlsx",
    "Testimony 1-500 SpellChecked.xlsx",
    "Testimony 501-999 SpellChecked.xlsx",
    "Testimony 1001-1498 SpellChecked.xlsx",
    "Testimony 1499-2805 SpellChecked.xlsx"]

sheet_data = []
for s in sheets:
    sheet_data.append(pd.read_excel(folder + s))
sheet_data = pd.concat(sheet_data)

# database orm tools
from sqlalchemy import create_engine
engine = create_engine('mysql+mysqlconnector://root:''@localhost/iom_data')


class CheckConsistencyOfDataInSpreadsheets(unittest.TestCase):
    """Check the consistency of the data to be imported """

    def test_uniqueness_of_quote_ids(self):
        """Quote ids should be integers from 0 to MAX_QUOTE_ID with
        every value represented once. This checks that each id is unique"""
        self.assertEquals(MAX_QUOTE_ID, len(set(sheet_data.quoteID)))

    def test_that_all_quote_ids_are_integers(self):
        for i in sheet_data.quoteID:
            self.assertTrue(isinstance(i, np.int64), "%s is not an integer" % i)

    def test_that_quote_ids_have_no_gaps(self):
        """Quote ids should be integers from 0 to MAX_QUOTE_ID with
        every value represented once"""
        for i in range(1, MAX_QUOTE_ID):
            self.assertTrue(i in list(sheet_data.quoteID), "assertion failed for %s" % i)



class VerifyIntegrityOfImport(unittest.TestCase):
    """Checks that data imported correctly"""

    def setUp(self):
        self.table_data = pd.read_sql_table('iom_testimony', engine)

    def test_expected_count_in_iom_testimony(self):
        self.assertEquals(MAX_QUOTE_ID, len(self.table_data.quote_id))

    def test_that_quote_ids_have_no_gaps(self):
        """Quote ids should be integers from 0 to MAX_QUOTE_ID with
        every value represented once"""
        for i in range(1, MAX_QUOTE_ID):
            self.assertTrue(i in list(self.table_data.quote_id), "assertion failed for %s" % i)

    def test_that_numerical_data_values_match(self):
        """Checks that quote id, respondent id, and question number
        are consistent between the sheets and db"""
        for i, row in sheet_data.iterrows():
            table_row = self.table_data[self.table_data.quote_id == row.quoteID]
            self.assertEquals(row.quoteID, table_row.quote_id.values[0])
            self.assertEquals(row.respondentID, table_row.respondent_id.values[0])
            self.assertEquals(row.questionNumber, table_row.question_number.values[0])


    def test_that_text_data_matches(self):
        """Checks that quote id, respondent id, and question number
        are consistent between the sheets and db"""
        for i, row in sheet_data.iterrows():
            table_row = self.table_data[self.table_data.quote_id == row.quoteID]
            self.assertEquals(row.quoteText, table_row.quote_text.values[0], "error for %s" % row.quoteID)


if __name__ == '__main__':
    unittest.main()
