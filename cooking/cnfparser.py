

from pyparsing import Word, alphas, restOfLine, Literal, nums, LineEnd, Group
from satutils import find_all_variables_in_cnf


zero = '0'
eols = "\r\n"
TERM = ~Word(zero) + Word( nums + '-' ).setParseAction( lambda s,l,t: [ int(t[0]) ] )
EOL = LineEnd().suppress()

CLAUSE = Group(TERM * (0,) + Word(zero).suppress()) + EOL
COMMENT = Word('c') + restOfLine + EOL

EXPRESSION = Group((CLAUSE | COMMENT.suppress()) * (None,))

NUMBER_OF_VARIABLES = Word(nums).setParseAction( lambda s,l,t: [ int(t[0]) ] )
NUMBER_OF_CLAUSES = Word(nums).setParseAction( lambda s,l,t: [ int(t[0]) ] )

METADATA = Group(Literal('p cnf').suppress() + NUMBER_OF_VARIABLES + NUMBER_OF_CLAUSES) + EOL

CNF = (COMMENT*(None,None)).suppress() + METADATA + EXPRESSION









def parseCNF(cnfstr):
    presults = CNF.parseString(cnfstr)
    metadata = presults[0]
    clause_list = presults[1]

    variable_count = metadata[0]
    clause_count = metadata[1]

    #print clause_count
    #print clause_list
    #print len(clause_list)

    if not clause_count == len(clause_list):
        raise Exception("Number of clauses do not match the clause count, in parsing CNF")

    cnf = []
    for clause in clause_list:
        cnf.append(tuple(clause))
    return (variable_count,clause_count,cnf)

def unparseDIMACS(cnf,comment = None):

    if comment != None:
        comment = 'No comment'
    cnf_str_list = []
    cnf_str_list.append('c ' + str(comment) + '\n')

    num_of_vars = len(find_all_variables_in_cnf(cnf))
    num_of_clauses = len(cnf)
    cnf_str_list.append('p cnf ' + str(num_of_vars) + ' ' + str(num_of_clauses) + '\n')

    for clause in cnf:
        for term in clause:
            cnf_str_list.append(str(term) + ' ')

        cnf_str_list.append('0\n')

    cnf_str_list.append('\n')
    return ''.join(cnf_str_list)


SAT = Literal("SAT").suppress() + EOL + CLAUSE
UNSAT = Literal("UNSAT").suppress() + EOL
SATFILE = (UNSAT | SAT)

def parseSAT(sat):
    result = SATFILE.parseString(sat)

    if len(result) == 0:
        return [False,[]]

    return [True,list(result[0])]








def main():
    """
    cnf0 = [ (1,2,3), (2,3,4), (3,4,5),
            (1,2,3),
            (-1,2,3), (1,-2,3), (1,2,-3),
            (1,-2,-3), (-1,2,-3), (-1,-2,3),
            #(-1,-2,-3),
            (1,2,4), (1,2,6), (-1,2,-4),
            (3,-4,-6), (2,4,-6)]
    cnf0_str = unparseDIMACS(cnf0)
    cnf1 = parseCNF(cnf0_str)
    """

    sat_str = "SAT\n1 2 -3 5 -8 0\n"
    print parseSAT(sat_str)
    sat_str = "UNSAT"
    print parseSAT(sat_str)
    sat_str = "UNSAT\n"
    print parseSAT(sat_str)




if __name__ == '__main__':
    main()
