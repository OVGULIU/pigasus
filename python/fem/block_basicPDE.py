# -*- coding: UTF-8 -*-
#! /usr/bin/python

# ...
import numpy                as np
from pigasus.fem.basicPDE import *
from pigasus.utils.blockdata import *

# ...
class block_basicPDE():

    def __init__(self, size, dict_testcases, geometry=None, same_space=True):
        """
        a block of basicPDEs. size must a list of two integers, describing the
        number of rows and columns of the block PDEs
        """
        # TODO PDEs with different spaces
        if not same_space:
            print "block_basicPDE: NOT YET IMPLEMENTED when same_space=False"
        self._size          = size
        self._dict_PDE      = {}
        self._list_PDE      = []
        self._system        = None
        self._dict_system   = {}
        self._list_rhs      = []
        self._list_unknown  = []
        self._dict_testcases= dict_testcases

        # ... first, we create PDEs correponsing to the testcases dictionary
        #     the result is also a dictionary of PDEs
        iteration = 0
        V = None
        for keys, tc in dict_testcases.iteritems():
            i = keys[0] ; j = keys[1]
            if (iteration == 0):
                PDE = basicPDE(geometry=geo, testcase=tc)
                V   = PDE.V
            else:
                PDE = basicPDE(geometry=geo, testcase=tc, V=V)
            self._dict_PDE[i,j] = PDE
            iteration += 1
        # ...

        # ... second, we create a list of PDEs, and initialize all PDE to None
        for i in range(0,self.size[0]):
            line = []
            for j in range(0,self.size[1]):
                line.append(None)
            self._list_PDE.append(line)
        # ...

        # ... then, initialize the PDEs (double) list with the PDEs dictionary
        for keys, PDE in self._dict_PDE.iteritems():
            i = keys[0] ; j = keys[1]
            self._list_PDE[i][j] = PDE
        # ...

        # ... finally, we treate the None PDEs as a zero matrix
        #     TODO
        # ...


        # ... create the list of rhs and unknowns
        for i in range(0,self.size[0]):
            # in case where a PDE is None, we have to use the transposed PDE
            # [i][j] <-> [j][i]
            try:
                PDE = self._list_PDE[i][0]
                U   = PDE.unknown
                rhs = PDE.rhs
            except:
                PDE = self._list_PDE[0][i]
                U   = PDE.unknown
                rhs = PDE.rhs

            self._list_unknown.append(U)
            self._list_rhs.append(rhs)
        # ...

    @property
    def size(self):
        return self._size

    def assembly(self):
        # TODO take into account the case where a PDE is not specified and we
        # have to put a zero matrix
        self._dict_system = {}
        for keys, PDE in self._dict_PDE.iteritems():
            print ">>> Assembly PDE ", keys
            PDE.assembly()
            i = keys[0] ; j = keys[1]
            self._dict_system[i,j] = PDE.system

        matrices = []
        for i in range(0,self.size[0]):
            line = []
            for j in range(0,self.size[1]):
                line.append(None)
            matrices.append(line)

        for keys, system in self._dict_system.iteritems():
            i = keys[0] ; j = keys[1]
            matrices[i][j] = system.get()

        list_rhs = [rhs.get() for rhs in self._list_rhs]

        # ... create block matrix
#        print ">>> create block matrix"
        self._system = BlockMatrix(matrices)
#        print "<<< done."
#        print ">>> assembly block matrix"
        self._system.assembly()
#        print "<<< done."

        # ... create block vector
#        print ">>> create block vector"
        self._rhs= BlockVector(list_rhs)
#        print "<<< done."
#        print ">>> assembly block vector"
        self._rhs.assembly()
#        print "<<< done."

    def free(self):
        for keys, PDE in self._dict_PDE.iteritems():
            PDE.free()

    @property
    def system(self):
        return self._system

    @property
    def rhs(self):
        return self._rhs




if __name__ == "__main__":
    from caid.cad_geometry import square as domain
    nx = 7 ; ny = 7
    px = 2 ; py = 2
    geo = domain(n=[nx,ny],p=[px,px])


    #-----------------------------------
    def testcase():
        # implicit part
        tc = {}

        tc['b']  = lambda x,y : [1.]
        tc['f']  = lambda x,y : [1.]

        tc['AllDirichlet'] = True

        return tc
    #-----------------------------------

    size = [2,2]

    dict_testcases = {}
    dict_testcases[0,0] = testcase()
    dict_testcases[0,1] = testcase()
    dict_testcases[1,0] = testcase()
    dict_testcases[1,1] = testcase()

    PDEs = block_basicPDE(size, dict_testcases, geometry=geo)
    PDEs.assembly()

    rhs = PDEs.rhs.get()
    system = PDEs.system
    matrix = system.get()

    Y = matrix.dot(rhs)
    print Y.shape

    PDEs.free()