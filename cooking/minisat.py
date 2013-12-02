
import os
import subprocess

from cnfparser import unparseDIMACS,parseSAT
from tempfile import NamedTemporaryFile


class minisat_solver:
    def __init__(self,executable_path):
        self.executable_path = executable_path

    def solve(self,cnf):
        with NamedTemporaryFile() as cnf_file:


            cnf_file.write(unparseDIMACS(cnf))

            cnf_file.flush()

            with NamedTemporaryFile() as sat_file:

                startupinfo = None
                
                # I *think* this might be necessary for windows
                """
                if subprocess.STARTUPINFO != None:
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                """

                p = subprocess.Popen([self.executable_path, cnf_file.name,sat_file.name],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      startupinfo=startupinfo,
                                      shell=False)

                out, err = p.communicate()

                sat_result = sat_file.read()
                #print sat_result
                
                
                return parseSAT(sat_result)






def main():
    cnf = [ (1,2,3), (2,3,4), (3,4,5),
            (1,2,3),
            (-1,2,3), (1,-2,3), (1,2,-3),
            (1,-2,-3), (-1,2,-3), (-1,-2,3),
            #(-1,-2,-3),
            (1,2,4), (1,2,6), (-1,2,-4),
            (3,-4,-6), (2,4,-6)]
    # FIXME: use arg for path
    solver = minisat_solver(minisat_path)

    print solver.solve(cnf)

if __name__ == '__main__':
    main()

