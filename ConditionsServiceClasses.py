import inspect

from IOMDataService import IOMService


class LoadException(Exception):
    # def __init__(self, message, Errors):
    print(inspect.stack()[0][3])


class ConditionsService(IOMService):
    """
    This implements a set of functions finding the associtions between quotes, respondents, and conditions, when given the id of one
    This performs queries for use in tasks looking at words denoting conditions.

    """

    def __init__(self, test):
        IOMService.__init__(self)
        self.connect_to_mysql(test)
        self.query_string = "SELECT %s FROM %s WHERE %s = %%s"
        # self.conditions = []
        #self.condition_quote_vectors = []
        #self.respondent_main_vectors = []

        self.load_conditions()

    def load_all(self):
        """
        Shortcut to execute all of the condition load commands
        """
        self.load_aliases()
        self.all_assoc_for_respondents()
        self.all_assoc_for_patients()
        self.all_assoc_for_quotes()
        self.all_assoc_for_patient_quotes()
        ##load_respondents_x_conditions()
        # self.load_patients_x_conditions()
        self.load_testimonials_x_conditions()

        # self.load_conditions()

    def load_conditions(self):
        """
        Get all conditions
        """
        try:
            query = "SELECT condition_name, condition_id FROM conditions"
            val = []
            self.get_data_from_database(query, val)
            self.conditions = self.dbdata
        except Exception as e:
            print(inspect.stack()[0][3], e)
        else:
            print("A list comprising all condition names and ids has been loaded as self.conditions")

    def load_aliases(self):
        """
        Get all aliases
        """
        try:
            query = "SELECT aliasID, conditionAlias, condition_id FROM conditionAliases"
            val = []
            self.get_data_from_database(query, val)
            self.aliases = self.dbdata
        except Exception as e:
            print(e)
        else:
            print("A list comprising all aliases and ids has been loaded as self.aliases")

    def load_testimonials_x_conditions(self):
        """
        Get associations between conditions as they occur in all testimonials
        """
        try:
            query = "SELECT x.quote_id, x.condition_id, c.condition_name FROM conditionsXtestimonials x INNER JOIN conditions c USING(condition_id)"
            val = []
            self.get_data_from_database(query, val)
            self.mainxcond = self.dbdata
        except Exception as e:
            print(inspect.stack()[0][3], e)
        else:
            print("A list of which conditions are mentioned in each testimonial has been loaded as self.mainxcond")

    def all_assoc_for_respondents(self):
        """
        Loads all respondents and all conditions
        """
        try:
            query = """SELECT DISTINCT t.respondent_id, cxt.condition_id, c.condition_name
			FROM testimony_all t
			INNER JOIN conditionsXtestimonials cxt ON t.quote_id = cxt.quote_id
			INNER JOIN conditions c ON c.condition_id = cxt.condition_id;"""
            self.get_data_from_database(query, [])
            self.respondentsXconditions = self.dbdata
        except LoadException:
            pass
        #as e:
        #	print inspect.stack()[0][3], e
        else:
            print("A list of which respondents correspond to which conditions has been loaded as self.respondentsXconditions")

    def all_assoc_for_patients(self):
        """
        Get associations between respondent_id and conditions where respondents are patients
        """
        try:
            query = """SELECT DISTINCT p.respondent_id, cxt.condition_id, c.condition_name
			FROM conditionsXpatients cxt INNER JOIN testimony_all t ON cxt.quote_id = t.quote_id
			INNER JOIN classify_patients p ON t.respondent_id = p.respondent_id
			INNER JOIN conditions c ON c.condition_id = cxt.condition_id"""
            self.get_data_from_database(query, [])
            self.patientsXconditions = self.dbdata
        except Exception as e:
            print(inspect.stack()[0][3], e)
        else:
            print("A list of all respondents identified as patients and their conditions has been loaded as self.patientsXconditions")

    def all_assoc_for_quotes(self):
        """
        Get associations between quote_id and condition for all quotes
        """
        try:
            query = """SELECT x.quote_id, x.condition_id, c.condition_name
			FROM conditionsXtestimonials x
			INNER JOIN conditions c ON x.condition_id = c.condition_id"""
            self.get_data_from_database(query, [])
            self.quotesXconditions = self.dbdata
        except Exception as e:
            print(inspect.stack()[0][3], e)
        else:
            print('A list of conditions associated with each quote has been loaded as self.quotesXconditions')

    def all_assoc_for_patient_quotes(self):
        """
        Get associations between quote_id and conditions for quotes from presumed patients
        """
        try:
            query = """SELECT DISTINCT t.quote_id, cxt.condition_id, c.condition_name
			FROM conditionsXpatients cxt
			INNER JOIN testimony_all t ON cxt.quote_id = t.quote_id
			INNER JOIN classify_patients p ON t.respondent_id = p.respondent_id
			INNER JOIN conditions c ON c.condition_id = cxt.condition_id;"""
            self.get_data_from_database(query, [])
            patient_quotesXconditions = self.dbdata
        except Exception as e:
            print(inspect.stack()[0][3], e)
        else:
            print("A list of associations for quotes from patients has been loaded as self.patient_quotesXconditions")

    ##########################################################################
    #                                                                        #
    # The ones below this are for getting associations for a requested item  #
    #                                                                        #
    ##########################################################################

    def for_respondent(self, identifier):
        """
        Given a respondent id, this will return a dictionary containing a list of their quoteIDs and a list of their associated conditionIDs
        @param identifier The respondent ID
        @type identifier integer
        """
        #Get the conditions associated with respondent
        query = self.query_string % ('condition_id', 'conditionsXrespondents', 'respondent_id')
        self.get_data_from_database(query, [identifier])
        conditionIDs = self.dbdata
        #Get the respondent's quoteIDs
        query = self.query_string % ('quote_id', 'testimony', 'respondent_id')
        self.get_data_from_database(query, [identifier])
        quoteIDs = self.dbdata

        d = {'conditionIDs': conditionIDs, 'quoteIDs': quoteIDs}
        return d

    def for_condition(self, identifier):
        """
        Given a condition id, this will return a dictionary containing a list of the quoteIDs where it is mentioned and a list of respondents who mentione it
        @param identifier The condition ID
        @type identifier integer
        """
        #Get the respondents associated with the condition
        query = """SELECT DISTINCT t.respondent_id
		FROM testimony t
		INNER JOIN conditionsXtestimony cxt ON t.quote_id = cxt.quote_id
		WHERE cxt.condition_id = %s"""
        self.get_data_from_database(query, [identifier])
        respondentIDs = self.dbdata

        #Get the quoteIDs for testimonials in which the condition is mentioned
        query = self.query_string % ('quote_id', 'conditionsXtestimony', 'condition_id')
        self.get_data_from_database(query, [identifier])
        quoteIDs = self.dbdata

        d = {'respondentIDs': respondentIDs, 'quoteIDs': quoteIDs}
        return d

    def for_condition_patients(self, identifier):
        """
        RETURNS A SUBSET OF ALL RESPONDENTS
        Given a condition id, returns a dictionary containing a list of the quoteIDs where it is mentioned by patients and a list of patients who mention it
        @param identifier The condition ID
        @type identifier int
        """
        #Get the patients associated with the condition
        query = """SELECT cp.respondent_id
		FROM conditionsXrespondents cxr INNER JOIN patients cp ON cxr.respondent_id = cp.respondent_id
		WHERE condition_id = %s"""
        self.get_data_from_database(query, [identifier])
        respondentIDs = self.dbdata

        #Get the quoteIDs for testimonials in which the condition is mentioned limited to patients
        query = """SELECT DISTINCT t.quote_id
		FROM conditionsXtestimony cxt INNER JOIN testimony t ON cxt.quote_id = t.quote_id
		INNER JOIN patients p ON t.respondent_id = p.respondent_id
		WHERE condition_id = %s"""
        self.get_data_from_database(query, [identifier])
        quoteIDs = self.dbdata

        d = {'respondentIDs': respondentIDs, 'quoteIDs': quoteIDs}
        return d

    def for_quote(self, identifier):
        """
        Given a quote_id, this returns dictionary with list of unique condition ids mentioned in it,
        a list of conditionNames, and a list containing the respondent id as the only item
        @param identfier Quote ID to find associations for
        @type identifier int
        """
        #Get conditionIDs
        #query = "SELECT DISTINCT condition_id FROM conditionsXtestimony WHERE quote_id = %s"
        #query = "SELECT DISTINCT condition_id, condition_name FROM conditionsXtestimony NATURAL JOIN conditions WHERE quote_id = %s"
        query = "SELECT DISTINCT condition_id, condition_name FROM conditionsXtestimonials INNER JOIN conditions USING(condition_id) WHERE quote_id = %s"
        self.get_data_from_database(query, [identifier])
        conditionIDs = []
        conditionNames = []
        [conditionIDs.append(i['condition_id']) for i in self.dbdata]
        [conditionNames.append(i['condition_name']) for i in self.dbdata]

        #Get quote's author
        #query = """SELECT respondent_id FROM testimony WHERE quote_id = %s"""
        query = """SELECT respondent_id FROM testimony_all WHERE quote_id = %s"""

        self.get_data_from_database(query, [identifier])
        quoteIDs = self.dbdata

        #Get condition names
        query = "SELECT DISTINCT condition_name FROM conditions WHERE condition_id = %s"
        self.get_data_from_database
        d = {'conditionIDs': conditionIDs, 'conditionNames': conditionNames, 'respondentIDs': quoteIDs[0]}
        return d

    ############################################################################################
    #                                                                                          #
    # These are for making vectors                                                             #
    #                                                                                          #
    ############################################################################################
    def make_vectors(self):
        """
        This makes vectors of quotes and vectors of respondents for each condition.
        The list 'edges' has been pruned to have only one occurance of each id since we don't care how many times the person mentioned the condition
        """
        self.respondent_vectors = []
        self.testimonial_vectors = []
        self.patient_vectors = []
        for c in self.conditions:
            condition = str(c['condition_name'])
            #Make vectors by respondent (undifferentiated)
            try:
                rtemp = []
                [rtemp.append(rxc['respondent_id']) for rxc in self.respondentsXconditions if
                 str(rxc['condition_name']) == condition]
                self.respondent_vectors.append({'condition_name': c['condition_name'], 'edges': list(set(rtemp))})
            except Exception as e:
                print("Error making respondent vectors : %s" % e)
            #Make vectors by testimonial
            try:
                qtemp = []
                [qtemp.append(qxc['quote_id']) for qxc in self.quotesXconditions if
                 str(qxc['condition_name']) == condition]
                self.testimonial_vectors.append({'condition_name': c['condition_name'], 'edges': list(set(qtemp))})
            except Exception as e:
                print("Error making testimonial vectors: %s" % e)
            #Make vectors by patients
            try:
                ptemp = []
                [ptemp.append(pxc['respondent_id']) for pxc in self.patientsXconditions if
                 str(pxc['condition_name']) == condition]
                self.patient_vectors.append({'condition_name': c['condition_name'], 'edges': list(set(ptemp))})
            except Exception as e:
                print("Error making patient vectors : %s " % e)
                #
                #self.quote_vectors = []
                #self.respondent_vectors =[]
                #for c in self.conditions:
                #	t  = self.for_condition(c['condition_id'])
                #	qids = t['quoteIDs']
                #	qtemp = []
                #	[qtemp.append(g['quote_id']) for g in qids]
                #	qtemp = list(set(qtemp))
                #	self.quote_vectors.append({'condition_id' : c['condition_id'], 'condition_name' : c['condition_name'], 'edge' : qtemp })
                #	#Repeat for respondents
                #	rids = t['respondentIDs']
                #	rtemp = []
                #	[rtemp.append(g['respondent_id']) for g in rids]
                #	rtemp = list(set(rtemp))
                #	self.respondent_vectors.append({'condition_id' : c['condition_id'], 'condition_name' : c['condition_name'], 'edge' : rtemp })
                #
                #	#Now do for patients
                #	#All quotes
                #	#t  = self.for_condition_patients(c['condition_id'])
                #	#qids = t['quoteIDs']
                #	#qtemp = []
                #	#[qtemp.append(g['quote_id']) for g in qids]
                #	#qtemp = list(set(qtemp))
                #	#self.patient_quote_vectors.append({'condition_id' : c['condition_id'], 'condition_name' : c['condition_name'], 'edge' : qtemp })
                #	#Repeat for respondents
                #	rids = t['respondentIDs']
                #	rtemp = []
                #	[rtemp.append(g['respondent_id']) for g in rids]
                #	rtemp = list(set(rtemp))
                #	self.patient_respondent_vectors.append({'condition_id' : c['condition_id'], 'condition_name' : c['condition_name'], 'edge' : rtemp })
                #
                #
                #