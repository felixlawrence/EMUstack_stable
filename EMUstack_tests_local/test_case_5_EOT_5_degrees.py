"""
Test simulation Extraordinary Optical Transmission replicating 
Fig 2 of Lie, H - Microscopic theory of the extraordinary optical transmission
doi:10.1038/nature06762
"""

import time
import datetime
import numpy as np
import sys
# from multiprocessing import Pool
sys.path.append("../EMUstack_backend/")

import objects
import materials
import plotting
from stack import *
import testing
from numpy.testing import assert_allclose as assert_ac
from numpy.testing import assert_equal
import testing

    ################ Simulation parameters ################


# Number of CPUs to use im simulation
# num_cores = 1

def setup_module(module):  
    # Remove results of previous simulations
    # plotting.clear_previous('.txt')
    # plotting.clear_previous('.pdf')
    # plotting.clear_previous('.log')

    ################ Light parameters #####################
    wl_1     = 1.11*940
    wl_2     = 1.15*940
    no_wl_1  = 1
    # Set up light objects
    wavelengths = np.linspace(wl_1, wl_2, no_wl_1)
    light_list  = [objects.Light(wl, max_order_PWs = 4, theta = 5.0, phi = 0.0) for wl in wavelengths]
    light = light_list[0]


    #period must be consistent throughout simulation!!!
    period = 940
    diam1 = 266
    NHs = objects.NanoStruct('NW_array', period, diam1, height_nm = 200, 
        inclusion_a = materials.Air, background = materials.Au, loss = True,
        square = True,    
        make_mesh_now = True, force_mesh = True, lc_bkg = 0.05, lc2= 5.0, lc3= 3.0)#lc_bkg = 0.08, lc2= 5.0)

    cover  = objects.ThinFilm(period = period, height_nm = 'semi_inf',
        material = materials.Air, loss = False)
    sub = objects.ThinFilm(period = period, height_nm = 'semi_inf',
        material = materials.Air, loss = False)

    num_BM = 100
    ################ Evaluate each layer individually ##############
    sim_NHs = NHs.calc_modes(light, num_BM = num_BM)
    sim_cover  = cover.calc_modes(light)
    sim_sub    = sub.calc_modes(light)

    stack = Stack((sim_sub, sim_NHs, sim_cover))
    stack.calc_scat(pol = 'TM')
    module.stack_list = [stack]


    # # # # SAVE DATA AS REFERENCE
    # # # # Only run this after changing what is simulated - this
    # # # # generates a new set of reference answers to check against
    # # # # in the future
    # # num_pw_per_pol = stack_list[0].layers[0].structure.num_pw_per_pol
    # # Rnet = stack_list[0].R_net[num_pw_per_pol,num_pw_per_pol]
    # # print Rnet
    # testing.save_reference_data("case_5", stack_list)


def test_stack_list_matches_saved(casefile_name = 'case_5'):
    rtol = 1e-4
    atol = 1e-4
    ref = np.load("ref/%s.npz" % casefile_name)
    yield assert_equal, len(stack_list), len(ref['stack_list'])
    for stack, rstack in zip(stack_list, ref['stack_list']):
        yield assert_equal, len(stack.layers), len(rstack['layers'])
        lbl_s = "wl = %f, " % stack.layers[0].light.wl_nm
        for i, (lay, rlay) in enumerate(zip(stack.layers, rstack['layers'])):
            lbl_l = lbl_s + "lay %i, " % i
            yield assert_ac, lay.R12, rlay['R12'], rtol, atol, lbl_l + 'R12'
            yield assert_ac, lay.T12, rlay['T12'], rtol, atol, lbl_l + 'T12'
            yield assert_ac, lay.R21, rlay['R21'], rtol, atol, lbl_l + 'R21'
            yield assert_ac, lay.T21, rlay['T21'], rtol, atol, lbl_l + 'T21'
            yield assert_ac, lay.k_z, rlay['k_z'], rtol, atol, lbl_l + 'k_z'
            #TODO: yield assert_ac, lay.sol1, rlay['sol1']
        yield assert_ac, stack.R_net, rstack['R_net'], rtol, atol, lbl_s + 'R_net'
        yield assert_ac, stack.T_net, rstack['T_net'], rtol, atol, lbl_s + 'T_net'
