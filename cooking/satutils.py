
"""
    Clause: a tuple of the form (x,y,z,...). Each member of the tuple
    represents a term in the CNF clause; it must be a non-zero integer.
    Negative numbers represent negated variables, while positive numbers
    represent the same variables, non-negated.
    
    
    CNF: a list or set of clauses.
"""

def normalize_clause(clause):
    """
    
    Returns an ordered-normalized-copy of clause-tuple.
    
    * Orders the variables in a clause-tuple so that the clause is
    "normalized".
    * Removes duplicate terms, but not duplicate variables. For example,
        if one term is the negated variable of another term, they will
        both remain in the clause. In this case the negated variable
        will come first.
    """
    
    # remove duplicate terms, by dumping the terms into a set.
    result = list(set(clause))

    def compare_variables(a,b):
        """
        A term comparator that first sorts by variable. If two terms have
        the same variable, then the negated variable comes first.
        """
        if abs(a) == abs(b):
            if a < 0 and b > 0:
                return -1
            if b > 0 and a < 0:
                return 1
        return abs(a) - abs(b)

    result.sort(cmp=compare_variables)

    return tuple(result)


def normalized_clause_comparison(x,y):
    """
    A comparator that sorts clauses with the following priorities:
    
    * First by clause-length.
    * Next, by the lexicographic ordering of the variables (absolute
        terms) of the clause.
    * Finally, by the lexicograph ordering of the terms of the clause.
    """
    if len(y) < len(x):
        return -1
    if len(x) < len(y):
        return 1

    for i in range(len(x)):
        if abs(x[i]) < abs(y[i]):
            return -1
        if abs(y[i]) < abs(x[i]):
            return 1

    if x < y:
        return -1
    if y < x:
        return 1
    return 0

def normalize_cnf(cnf):
    """
    Returns a copy of the CNF, as a list.
    
    * Normalizes each clause first.
    * Duplicate clauses are removed.
    * The list is sorted using the normalized_clause_comparison()
        comparator.
    """
    
    
    result_set = set()

    for clause in cnf:
        result_set.add(normalize_clause(clause))


    result_cnf = list(result_set)
    result_cnf.sort(cmp=normalized_clause_comparison)

    return result_cnf


def find_all_variables_in_cnf(cnf):
    """
    Returns a set of all variables in the CNF.
    """
    all_vars = set()
    for clause in cnf:
        for term in clause:
            variable = abs(term)
            all_vars.add(variable)
    return all_vars

def calc_term2ci(cnf_list):
    """
    Returns a dictionary, of the form {term => {clause-integer-index}}.
    
    This is essentially an index of the terms in the CNF, to find which
    clauses in the CNF that contain each term.
    
    This is useful for unit propagation (see
    http://en.wikipedia.org/wiki/Unit_propagation#Complexity)
    among other things.
    
    The input must be a list-type, as sets have no ordering, and thus
    the clauses contained within a set cannot be given an integer-index
    within the CNF.
    """

    # to obtain all terms, we first obtain all variables
    all_variables = find_all_variables_in_cnf(cnf_list)

    # the resulting dictionary
    term2ci = {}

    # we get every term by looping through the variables
    for variable in all_variables:
        for term in [variable,-variable]:
            # default to an empty set of clause-indices
            term2ci[term] = set()

    for ci,clause in enumerate(cnf_list):
        for term in clause:
            term2ci[term].add(ci)

    return term2ci


def unit_propagate(cnf0,keep_units = True):
    """
    Returns a copy of the CNF, after propagating the unit-clauses.
    
    Runs in linear time of the total size of the CNF.
    
    See (http://en.wikipedia.org/wiki/Unit_propagation#Complexity).
    
    Parameters:
    
    * `cnf0`, the input CNF.
    * `keep_units`, whether to keep the unit clauses.
    
    Returns a tuple `(cnf,units,eliminations)`.
    
    * `cnf` is the resulting CNF
    * `units` is a set of the unit-clauses collected
    * `eliminations` is a set of variables eliminated; these can be
        values true or false without affecting the satisfiability of the
        CNF
    
    Notes:
    
    * If contradictory unit-clauses are found, they will both be
        included in the resulting CNF, regardless of whether
        `keep_units` is set to False.
    * Units-clauses are not duplicated in the resulting formula - even
        if they were in the input formula.
    
    """
    cnf_list = list(cnf0)

    # obtain the term-to-clause index
    term2ci = calc_term2ci(cnf_list)


    unit_2_clause = {}
    unit_terms = set()
    for ci,clause in enumerate(cnf_list):
        if len(clause) == 1:
            term, = clause
            if term not in unit_2_clause:
                unit_2_clause[term] = ci
            unit_terms.add(term)

    
    
    unit_terms_to_propogate = set(unit_terms)

    while len(unit_terms_to_propogate) != 0:
        
        # take one unit-term left to propagate
        unit_term = unit_terms_to_propogate.pop()


        for ci in term2ci[unit_term]:
            # for all the clauses that contain the term,
            # we will remove the clause
            
            # get the clause
            clause = cnf_list[ci]
            
            assert unit_term in clause
            
            # The clause is being removed, so we must update the term2ci
            # index with all the removed terms. In other words, we must
            # remove ci from term2ci.
            for term in clause:
                # for each term in the clause,
                
                # we don't remove the index of the unit-term, because
                # that would modify term2ci[unit_term] while we are
                # iterating it. We will remove those afterward.
                if term == unit_term:
                    
                    continue
                
                # remove ci from the index
                term2ci[term].remove(ci)
                
                
            # remove the clause from the list; we will use empty clauses
            # as place-holders
            cnf_list[ci] = tuple()
        
        
        clause_refs_to_remove = set()
        for ci in term2ci[-unit_term]:
            # for all clauses that contain the negation of the term,
            # we must remove the negated term from the clause.
            
            # get the clause
            clause = cnf_list[ci]

            assert -unit_term in clause

            if len(clause) == 1:
                # don't remove the clause if it itself is a unit clause:
                # it is a contradicting unit-clause, and we leave it in.
                continue
            
            
            # duplicate the clause,
            new_clause = list(clause)

            # remove the negated term from the clause
            new_clause.remove(-unit_term)

            assert -unit_term not in new_clause

            
            if len(new_clause) == 1:
                # if the new clause is now a newly made unit-clause,
                # we must add it to the unit_terms_to_propogate set.
                
                a, = new_clause
                unit_terms_to_propogate.add(a)
                unit_terms.add(a)
                unit_2_clause[a] = ci
            
            # reinsert the clause into the CNF
            cnf_list[ci] = tuple(new_clause)
            clause_refs_to_remove.add(ci)
            
        
        term2ci[ unit_term] = set()
        
        for ci in clause_refs_to_remove:
            term2ci[-unit_term].remove(ci)

    
    eliminated_variables = set()
    for term in term2ci.iterkeys():
        if len(term2ci[term]) == 0 and len(term2ci[-term]) == 0 \
            and term not in unit_terms and -term not in unit_terms:
        
            eliminated_variables.add(abs(term))
    

    
    
    def compare_term2ci(term2ci0,term2ci1):
        for term in term2ci1.iterkeys():
            if len(term2ci1[term]) == 0:
                assert term not in term2ci0 or len(term2ci0[term]) == 0
            else:
                assert term in term2ci0 or len(term2ci1[term])
        
        return True
    
    assert compare_term2ci(term2ci, calc_term2ci(cnf_list))
    assert compare_term2ci(calc_term2ci(cnf_list), term2ci)



    contradictory_units = set()
    for unit_term in unit_terms:
        if -unit_term in unit_terms:
            contradictory_units.add(unit_term)
    
    units_to_keep = set()
    units_to_keep |= contradictory_units


    if keep_units:
        units_to_keep |= unit_terms
    
    
    # we reinsert the unit-clauses into the CNF
    for unit_term in units_to_keep:
        
        ci = unit_2_clause[unit_term]
        
        assert cnf_list[ci] == tuple()
        
        cnf_list[ci] = (unit_term,)
    
    
    # now reconstruct the remaining clauses into a new CNF
    
    result_cnf = []
    result_unit_clauses = set()

    for clause in cnf_list:
        if len(clause) == 0:
            continue
        
        result_cnf.append(clause)
    
    return result_cnf,unit_terms,eliminated_variables





import unittest

class Test_unit_propagate(unittest.TestCase):

    def setUp(self):
        pass

        
    def test_unit_propagate_duplicate_units_keep(self):
        cnf = [(1,2,-3), (2,), (2,)]
        expected_cnf = [(2,)]
        expected_units = set([2])
        expected_eliminated = set([1,3])
        expected_result = expected_cnf,expected_units,expected_eliminated
        
        result = unit_propagate(cnf,keep_units=True)
        self.assertEqual(result,expected_result)
    def test_unit_propagate_duplicate_units_nokeep(self):
        cnf = [(1,2,-3), (2,), (2,)]
        expected_cnf = []
        expected_units = set([2])
        expected_eliminated = set([1,3])
        expected_result = expected_cnf,expected_units,expected_eliminated
        
        result = unit_propagate(cnf,keep_units=False)
        self.assertEqual(result,expected_result)
    
    def test_unit_propagate_remove_clause_nokeep(self):
        
        cnf = [(1,2,-3), (2,)]
        expected_cnf = []
        expected_units = set([2])
        expected_eliminated = set([1,3])
        expected_result = expected_cnf,expected_units,expected_eliminated
        
        result = unit_propagate(cnf,keep_units=False)
        self.assertEqual(result,expected_result)
    
    def test_unit_propagate_remove_clause_keep(self):
        cnf = [(1,2,-3), (2,)]
        expected_cnf = [(2,)]
        expected_units = set([2])
        expected_eliminated = set([1,3])
        expected_result = expected_cnf,expected_units,expected_eliminated
        
        result = unit_propagate(cnf,keep_units=True)
        self.assertEqual(result,expected_result)
    
    def test_unit_propagate_contra_units_keep(self):
        cnf = [(-2,), (2,)]
        expected_cnf = [(-2,), (2,)]
        expected_units = set([2,-2])
        expected_eliminated = set()
        expected_result = expected_cnf,expected_units,expected_eliminated
        
        result = unit_propagate(cnf,keep_units=True)
        self.assertEqual(result,expected_result)
    def test_unit_propagate_contra_units_nokeep(self):
        cnf = [(-2,), (2,)]
        expected_cnf = [(-2,), (2,)]
        expected_units = set([2,-2])
        expected_eliminated = set()
        expected_result = expected_cnf,expected_units,expected_eliminated
        
        result = unit_propagate(cnf,keep_units=False)
        self.assertEqual(result,expected_result)
    


if __name__ == '__main__':
    unittest.main()


