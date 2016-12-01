"""
Some basic tests for SFR checker (not super rigorous)
need to add a test case that has elevation input by reach
"""

#import sys
#sys.path.append('/Users/aleaf/Documents/GitHub/flopy3')
import os
import flopy
from flopy.modflow.mfsfr2 import check

tpth = os.path.abspath(os.path.join('temp', 't010'))
# make the directory if it does not exist
if not os.path.isdir(tpth):
    os.makedirs(tpth)

if os.path.split(os.getcwd())[-1] == 'flopy3':
    path = os.path.join('examples', 'data', 'mf2005_test')
    cpth = os.path.join('py.test/temp')
else:
    path = os.path.join('..', 'examples', 'data', 'mf2005_test')
    cpth = os.path.join(tpth)

sfr_items = {0: {'mfnam': 'test1ss.nam',
                 'sfrfile': 'test1ss.sfr'},
             1: {'mfnam': 'test1tr.nam',
                 'sfrfile': 'test1tr.sfr'},
             2: {'mfnam': 'testsfr2_tab.nam',
                 'sfrfile': 'testsfr2_tab_ICALC1.sfr'},
             3: {'mfnam': 'testsfr2_tab.nam',
                 'sfrfile': 'testsfr2_tab_ICALC2.sfr'},
             4: {'mfnam': 'testsfr2.nam',
                 'sfrfile': 'testsfr2.sfr'},
             5: {'mfnam': 'UZFtest2.nam',
                 'sfrfile': 'UZFtest2.sfr'},
             }


def load_check_sfr(i, mfnam, model_ws, checker_output_path):

    #print('Testing {}\n'.format(mfnam) + '='*100)
    m = flopy.modflow.Modflow.load(mfnam, model_ws=model_ws)
    m.model_ws = checker_output_path
    checker_outfile = os.path.join(tpth, 'SFRcheck_{}.txt'.format(m.name))
    
    chk = m.sfr.check(checker_outfile, level=1)

    if i == 1:
        assert 'overlapping conductance' in chk.warnings
    if i == 2:
        assert 'segment elevations vs. model grid' in chk.warnings

    return


def test_sfrcheck():

    m = flopy.modflow.Modflow.load('test1tr.nam', model_ws=path, verbose=False)

    # run level=0 check
    m.model_ws= cpth
    fpth = 'SFRchecker_results.txt'
    m.sfr.check(fpth, level=0)
    
    # test checks without modifications
    chk = check(m.sfr)
    chk.numbering()
    assert 'continuity in segment and reach numbering' in chk.passed
    chk.routing()
    assert 'circular routing' in chk.passed
    chk.overlapping_conductance()
    assert 'overlapping conductance' in chk.warnings # this example model has overlapping conductance
    chk.elevations()
    for test in ['segment elevations', 'reach elevations', 'reach elevations vs. grid elevations']:
        assert test in chk.passed
    chk.slope()
    assert 'minimum slope' in chk.passed
    
    # create gaps in segment numbering
    m.sfr.segment_data[0]['nseg'][-1] += 1
    m.sfr.reach_data['ireach'][3] += 1
    
    # create circular routing instance
    m.sfr.segment_data[0]['outseg'][1] = 1
    m.sfr.segment_data[0]['outseg']
    
    chk = check(m.sfr)
    chk.numbering()
    assert 'continuity in segment and reach numbering' in chk.errors
    chk.routing()
    assert 'circular routing' in chk.errors
    

def test_sfrloadcheck():
    for i, case in sfr_items.items():
        yield load_check_sfr, i, case['mfnam'], path, cpth



if __name__ == '__main__':
    test_sfrcheck()
    for i, case in sfr_items.items():
        test_sfrloadcheck(i, case['mfnam'], path, cpth)
