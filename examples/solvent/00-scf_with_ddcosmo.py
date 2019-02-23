#!/usr/bin/env python
#
# Author: Qiming Sun <osirpt.sun@gmail.com>
#

'''
A simple example of using solvent model in the mean-field calculations.
'''

from pyscf import gto, scf, dft
from pyscf import solvent

mol = gto.M(atom='''
C        0.000000    0.000000             -0.542500
O        0.000000    0.000000              0.677500
H        0.000000    0.9353074360871938   -1.082500
H        0.000000   -0.9353074360871938   -1.082500
            ''',
            verbose = 4)
mf = scf.RHF(mol)
solvent.ddCOSMO(mf).run()

mf = dft.UKS(mol)
mf.xc = 'b3lyp'
solvent.ddPCM(mf).run()

# Once solvent module is imported, PySCF-1.6.1 and newer supports the .DDCOSMO
# and .DDPCM methods to create solvent model.
from pyscf import solvent
mf = mf.DDCOSMO()
mf.run()
