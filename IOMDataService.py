import shelve
"""
Currently unused. All mysql queries are now done via IomDataModels.
May be resurrected to help with shelve and pickles
"""


from USCProjectDAOs import IOMProjectDAO


class IOMService(IOMProjectDAO):
    """
    This handles interactions with the IOM data database and storage files.
    All user applications should work off of this
    """

    def __init__(self):
        """
        Will hold the identifiers for records
        """
        self.names = []
        """
        Will hold the positive sentiment scores
        """
        self.posSent = []
        """
        Will hold the negative sentiment scores
        """
        self.negSent = []
        """
        Will hold the net sentiment scores
        """
        self.netSent = []
        """
        Will hold the sums of the absolute values of the sentiment scores
        """
        self.absumSent = []

    def connect_to_mysql(self, test):
        """
        Test should be boolean
        """
        IOMProjectDAO.__init__(self, test, 'true')

    def get_sentiment_data_from_file(self, datafile):
        """
        This is the generic file data loader.
        datafile shold be a path to file
        """
        # Open data file and push into lists
        db = shelve.open(datafile)
        self.keys = list(db.keys())
        for k in self.keys:
            s = db[k]
            self.names.append(s['quote_id'])
            self.posSent.append(s['avgPos'])
            self.negSent.append(s['avgNeg'])
            self.netSent.append(s['netSent'])
            self.absumSent.append(abs(s['avgPos']) + abs(s['avgNeg']))
        db.close()

    def save_sentiment_data_to_file(self, datafile, label):
        """
        This is a generic file data saver.
        datafile should be a path to file
        @param datafile: The path to the datafile
        @type datafile: C{string}


        """
        # try:
        db = shelve.open(datafile)
        db[label] = self.to_save
        db.close()
        print(self.to_save)
        return self.to_save

        # Check whether the problem was there not being a dictionary availble to save

    #except:
    #	try:
    #		self.to_save
    #		print ('Problem saving')
    #	except:
    #		print ('No variable self.to_save set')

#     def get_data_from_database(self, query, val):
#         """
#         This executes a parameterized query of the mysql database, stores the results in a list  of dictionaries called self.dbdata.
#
#         @return Also returns dbdata
#
#         @param query A mysql query with %s in place of all substitution variables
#         @type query string
#         @param val A list containing all substition parameters or empty if no substitutions are needed
#         @type val list
#
#         TODO Should have something to check whether a connection exists
#         """
#         self.connect_to_mysql('false')
#         self.query = query
#         self.val = val
#         self.returnAll()
#         self.dbdata = list(self.results)
#
#
# class QueryShell(IOMService):
#     """
#     This is just a shell to easily run queries on the database and get the results as a list of dictionaries
#
#     @return Returns list of dictionaries
#     """
#
#     def __init__(self):
#         IOMService.__init__(self)
#
#     def query(self, query, val):
#         self.get_data_from_database(query, val)
#         return self.dbdata
#
#
# class DHShell(IOMService):
#     """
#     This is a shell for use in public events to avoid cluttering up the page with each step of the query
#     It resets all its values after returning an array of dictionaries and thus need not be reinvoked.
#     Note that These queries are not parameterized
#
#     @return Returns list of dictionaries
#     """
#
#     def __init__(self, query_string):
#         """
#         @param query_string The query string
#         @type string
#         """
#         IOMService.__init__(self)
#         self.q(query_string)
#
#     def q(self, query_string):
#         # Get rid of previous queries
#         #		self.results = []
#         #		self.dbdata = None
#         #These queries are not parameterized
#         val = []
#         self.get_data_from_database(query_string, val)
#         return self.dbdata


class ShelveDataHandler(IOMService):
    def __init__(self):
        import shelve

        self.datafolder = 'storedData/'

    def openData(self, file_name):
        """
        Opens shelve file and returns the list
        """
        db = shelve.open(self.datafolder + file_name)
        list_to_populate = list(db.values())
        db.close()
        return list_to_populate[0]

    def bagSaver(self, list_to_save, file_name):
        """
        Saves a list of raw data into a shelve file.

        @param list_to_save A list of items to be saved into shelf file
        @type list_to_save list
        @param file_name The name of the file into which the items should be saved
        @type string
        """
        try:
            label = file_name
            to_save = list_to_save
            db = shelve.open(self.datafolder + file_name)
            db[label] = to_save
            db.close()
        except:
            print('Error saving to shelve file %s' % file_name)
        else:
            print('Successfully saved to shelve file %s ' % file_name)