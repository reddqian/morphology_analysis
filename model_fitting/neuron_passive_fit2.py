#!/usr/bin/env python

from lims_orca_utils import *
from neuron import h
import numpy as np
import argparse
import matplotlib.pyplot as plt

# Load the morphology

def load_morphology(filename):
    swc = h.Import3d_SWC_read()
    swc.input(filename)
    imprt = h.Import3d_GUI(swc, 0)
    h("objref this")
    imprt.instantiate(h.this)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='analyze cap check sweep')
    parser.add_argument('specimen')
    parser.add_argument('down_lim', type=float)
    parser.add_argument('up_lim', type=float)
    parser.add_argument('-p', dest='plot', action='store_true')

    args = parser.parse_args()
    
    up_data = np.loadtxt("/home/nathang/analysis/passive_props/data/" + args.specimen + '_upbase.dat')
    down_data = np.loadtxt("/home/nathang/analysis/passive_props/data/" + args.specimen + '_downbase.dat')

    specimen_name, ephys_roi_result_id, specimen_id = get_specimen_info_from_lims(args.specimen)
    swc_filename, swc_path = get_swc_from_lims(specimen_id)

    h.load_file("stdgui.hoc")
    h.load_file("import3d.hoc")
    load_morphology(swc_path)
    
    for sec in h.allsec():
        sec.insert('pas')
        for seg in sec:
            seg.pas.e = 0
    
    h.load_file("passive_props/fixnseg.hoc")
    h.load_file("passive_props/iclamp.ses")
    h.load_file("passive_props/params.hoc")
    h.load_file("passive_props/mrf2.ses")

    h.v_init = 0
    h.tstop = 100
    
    fit_start = 4.0025
    
    v_rec = h.Vector()
    t_rec = h.Vector()
    v_rec.record(h.soma[0](0.5)._ref_v)
    t_rec.record(h._ref_t)
    
    mrf = h.MulRunFitter[0]
    gen0 = mrf.p.pf.generatorlist.object(0)
    gen0.toggle()
    fit0 = gen0.gen.fitnesslist.object(0)
    
    up_t = h.Vector(up_data[:, 0])
    up_v = h.Vector(up_data[:, 1])   
    fit0.set_data(up_t, up_v)
    fit0.boundary.x[0] = fit_start
    fit0.boundary.x[1] = args.up_lim
    fit0.set_w()
    
    gen1 = mrf.p.pf.generatorlist.object(1)
    gen1.toggle()
    fit1 = gen1.gen.fitnesslist.object(0)
    
    down_t = h.Vector(down_data[:, 0])
    down_v = h.Vector(down_data[:, 1])
    fit1.set_data(down_t, down_v)
    fit1.boundary.x[0] = fit_start
    fit1.boundary.x[1] = args.down_lim
    fit1.set_w()
   
    minerr = 1e12
    for i in range(3):
        h.Ri = 100
        h.Cm = 1
        h.Rm = 10000
        mrf.randomize()
        mrf.prun()
        if mrf.opt.minerr < minerr:
            fit_Ri = h.Ri
            fit_Cm = h.Cm
            fit_Rm = h.Rm
            minerr = mrf.opt.minerr
            
    h.region_areas()
    print "Ri ", fit_Ri
    print "Cm ", fit_Cm
    print "Rm ", fit_Rm
    print "Final error ", minerr
    
    if args.plot:
        plt.style.use('ggplot')
        plt.figure()
        plt.plot(up_data[:, 0], up_data[:, 1])
        plt.plot(down_data[:, 0], -1 * down_data[:, 1])
        plt.plot(t_rec, -1 * np.array(v_rec), color='black')
        plt.axvline(fit_start, color='gray')
        plt.axvline(args.up_lim, color='gray')
        plt.axvline(args.down_lim, color='gray')
        plt.title("{:s} - Ri: {:.2f}, Rm: {:.2f}, Cm: {:.2f}".format(args.specimen, h.Ri, h.Rm, h.Cm))
        plt.xlim(0, 75)
        plt.savefig(args.specimen + "_pasfit2.png", bbox_inches='tight')
        plt.show()