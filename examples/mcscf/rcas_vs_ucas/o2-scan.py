import numpy
import scipy.linalg
from pyscf import gto
from pyscf import scf
from pyscf import mcscf
from pyscf import lo


def run(b, mo0=None, dm0=None):
    mol = gto.Mole()
    mol.build(
        verbose = 5,
        output = 'o2rhf-%3.2f.out' % b,
        atom = [
            ['O', (0, 0,  b/2)],
            ['O', (0, 0, -b/2)],],
        basis = 'cc-pvdz',
        spin = 2,
    )

    mf = scf.RHF(mol)
    mf.scf(dm0)

    mc = mcscf.CASSCF(mol, mf, 6, (4,2))
    if mo0 is None:
        mc.kernel()
    else:
        #caslst = numpy.argmax(numpy.dot(mo0.T, mf.mo_coeff), 1)
        #print caslst
        #mo = mcscf.sort_mo(mc, mf.mo_coeff, caslst, base=0)
        mo = lo.orth.vec_lowdin(mo0, mf.get_ovlp())
        mc.kernel(mo)
    mc.analyze()
    return mf, mc


def urun(b, mo0=None, dm0=None):
    mol = gto.Mole()
    mol.build(
        verbose = 5,
        output = 'o2uhf-%3.2f.out' % b,
        atom = [
            ['O', (0, 0,  b/2)],
            ['O', (0, 0, -b/2)],],
        basis = 'cc-pvdz',
        spin = 2,
    )

    mf = scf.UHF(mol)
    mf.scf(dm0)

    mc = mcscf.CASSCF(mol, mf, 4, (4,2))
    if mo0 is None:
        mo = mcscf.sort_mo(mc, mf.mo_coeff, [[7,8,12,11],[6,7,9,10]], base=1)
        mc.kernel()
    else:
        mo =(lo.orth.vec_lowdin(mo0[0], mf.get_ovlp()),
             lo.orth.vec_lowdin(mo0[1], mf.get_ovlp()))
        mc.kernel(mo)
    mc.analyze()
    return mf, mc

x = numpy.hstack((numpy.arange(0.9, 2.01, 0.1),
                  numpy.arange(2.1, 4.01, 0.1)))

dm0 = mo0 = None
eumc = []
euhf = []
#s = []
for b in reversed(x):
    mf, mc = urun(b, mo0, dm0)
    mo0 = mc.mo_coeff
    dm0 = mf.make_rdm1()
    #s.append(mc.spin_square()[1])
    euhf.append(mf.hf_energy)
    eumc.append(mc.e_tot)

euhf.reverse()
eumc.reverse()
print x
print euhf
print eumc

dm0 = mo0 = None
ermc = []
erhf = []
for b in x:
    mf, mc = run(b, mo0, dm0)
    mo0 = mc.mo_coeff
    dm0 = mf.make_rdm1()
    erhf.append(mf.hf_energy)
    ermc.append(mc.e_tot)

with open('o2-scan.txt', 'w') as fout:
    fout.write('  ROHF 0.9->4.0   RCAS(6,6)     UHF 4.0->0.9  UCAS(6,6)  \n')
    for i, xi in enumerate(x):
        fout.write('%2.1f  %12.8f  %12.8f  %12.8f  %12.8f\n'
                   % (xi, erhf[i], ermc[i], euhf[i], eumc[i]))

import matplotlib.pyplot as plt
plt.plot(x, erhf, label='ROHF,0.9->4.0')
plt.plot(x, euhf, label='UHF, 4.0->0.9')
plt.plot(x, ermc, label='RCAS(6,6),0.9->4.0')
plt.plot(x, eumc, label='UCAS(6,6),4.0->0.9')
plt.legend()
plt.show()
