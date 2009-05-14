# Running IPF on Person and Household data

import synthesizer_algorithm.heuristic_algorithm
import synthesizer_algorithm.psuedo_sparse_matrix
import synthesizer_algorithm.drawing_households
import synthesizer_algorithm.adjusting_sample_joint_distribution
import synthesizer_algorithm.ipf
from gui.file_menu.newproject import Geography
import scipy
import scipy.stats
import numpy
import MySQLdb
import time
import sys
import pp
import pickle

#def configure_and_run(fileLoc, index_matrix=None, p_index_matrix=None, geo=None, varCorrDict=None):
def configure_and_run(fileLoc, geo, varCorrDict, dbList, index_matrix, p_index_matrix):


    index_matrix = numpy.asarray(index_matrix)
    p_index_matrix = numpy.asarray(p_index_matrix)


    f = open(fileLoc, 'rb')
    project = pickle.load(f)
    f.close()


    state, county, pumano, tract, bg = geo.state, geo.county, geo.puma5, geo.tract, geo.bg

    print '------------------------------------------------------------------'
    print 'Geography: PUMA ID- %s, Tract ID- %0.2f, BG ID- %s' \
                                                                         %(pumano, float(tract)/100, bg)
    print '------------------------------------------------------------------'

    db = MySQLdb.connect(host = dbList[0], user = dbList[1],
                         passwd = dbList[2], db = dbList[3])
    dbc = db.cursor()

    ti = time.clock()

# Identifying the number of housing units in the disaggregate sample
# Make Sure that the file is sorted by hhid
    dbc.execute('select hhid, serialno from gq_sample')
    gq_sample = numpy.asarray(dbc.fetchall())
    gq_units = dbc.rowcount

    dbc.execute('select hhid, serialno from hhld_sample')
    hhld_sample = numpy.asarray(dbc.fetchall())
    hhld_units = dbc.rowcount

    dbc.execute('select hhid, serialno, pnum, personuniqueid from person_sample')
    person_sample = numpy.asarray(dbc.fetchall())

    housing_sample = numpy.vstack((hhld_sample, gq_sample))
    housing_units = gq_units + hhld_units

# Identifying the control variables for the households, gq's, and persons
    hhld_control_variables = project.hhldVars
    gq_control_variables = project.gqVars
    person_control_variables = project.personVars

# Identifying the number of categories within each control variable for the households, gq's, and persons
    hhld_dimensions = project.hhldDims
    gq_dimensions = project.gqDims
    person_dimensions = project.personDims


# Reading the parameters 
    parameters = project.parameters


#______________________________________________________________________
# Creating the sparse array
    dbc.execute('select * from sparse_matrix1_%s' %(0))
    sp_matrix = numpy.asarray(dbc.fetchall())

#______________________________________________________________________
# Running IPF for Households
    print 'Step 1A: Running IPF procedure for Households... '
    hhld_objective_frequency, hhld_estimated_constraint = synthesizer_algorithm.ipf.ipf_config_run(db, 'hhld', hhld_control_variables, varCorrDict, hhld_dimensions, county, pumano, tract, bg, parameters)
    print 'IPF procedure for Households completed in %.2f sec \n'%(time.clock()-ti)
    ti = time.clock()

# Running IPF for GQ
    print 'Step 1B: Running IPF procedure for Gqs... '
    gq_objective_frequency, gq_estimated_constraint = synthesizer_algorithm.ipf.ipf_config_run(db, 'gq', gq_control_variables, varCorrDict, gq_dimensions, county, pumano, tract, bg, parameters)
    print 'IPF procedure for GQ was completed in %.2f sec \n'%(time.clock()-ti)
    ti = time.clock()

# Running IPF for Persons
    print 'Step 1C: Running IPF procedure for Persons... '
    person_objective_frequency, person_estimated_constraint = synthesizer_algorithm.ipf.ipf_config_run(db, 'person', person_control_variables, varCorrDict, person_dimensions, county, pumano, tract, bg, parameters)
    print 'IPF procedure for Persons completed in %.2f sec \n'%(time.clock()-ti)
    ti = time.clock()

    
#______________________________________________________________________
# Creating the weights array
    print 'Step 2: Running IPU procedure for obtaining weights that satisfy Household and Person type constraints... '
    dbc.execute('select rowno from sparse_matrix1_%s group by rowno'%(0))
    result = numpy.asarray(dbc.fetchall())[:,0]
    weights = numpy.ones((1,housing_units), dtype = float)[0] * -99
    weights[result]=1

#______________________________________________________________________
# Creating the control array
    total_constraint = numpy.hstack((hhld_estimated_constraint[:,0], gq_estimated_constraint[:,0], person_estimated_constraint[:,0]))

#______________________________________________________________________
# Running the heuristic algorithm for the required geography
    iteration, weights, conv_crit_array, wts_array = synthesizer_algorithm.heuristic_algorithm.heuristic_adjustment(db, 0, index_matrix, weights, total_constraint, sp_matrix, parameters)

    print 'IPU procedure was completed in %.2f sec\n'%(time.clock()-ti)
    ti = time.clock()
    

#_________________________________________________________________
    print 'Step 3: Creating the synthetic households and individuals...'
# creating whole marginal values
    hhld_order_dummy = synthesizer_algorithm.adjusting_sample_joint_distribution.create_aggregation_string(hhld_control_variables)
    hhld_frequencies = synthesizer_algorithm.drawing_households.create_whole_frequencies(db, 'hhld', hhld_order_dummy, pumano, tract, bg)

    gq_order_dummy = synthesizer_algorithm.adjusting_sample_joint_distribution.create_aggregation_string(gq_control_variables)
    gq_frequencies = synthesizer_algorithm.drawing_households.create_whole_frequencies(db, 'gq', gq_order_dummy, pumano, tract, bg)

    frequencies = numpy.hstack((hhld_frequencies[:,0], gq_frequencies[:,0]))
#______________________________________________________________________
# Sampling Households and choosing the draw with the best match with with the objective distribution

    hhidRowDict = synthesizer_algorithm.drawing_households.hhid_row_dictionary(housing_sample) # row in the master matrix - hhid
    rowHhidDict = synthesizer_algorithm.drawing_households.row_hhid_dictionary(p_index_matrix) # hhid - row in the person index matrix


    p_value = 0
    max_p = 0
    min_chi = 1e10
    draw_count = 0
    while(p_value < parameters.synPopPTol and draw_count < parameters.synPopDraws):
        draw_count = draw_count + 1
        synthetic_housing_units = synthesizer_algorithm.drawing_households.drawing_housing_units(db, frequencies, weights, index_matrix, sp_matrix, 0)

# Creating synthetic hhld, and person attribute tables

        synthetic_housing_attributes, synthetic_person_attributes = synthesizer_algorithm.drawing_households.synthetic_population_properties(db, geo, synthetic_housing_units, p_index_matrix, housing_sample, person_sample, hhidRowDict, rowHhidDict)



        synth_person_stat, count_person, person_estimated_frequency = synthesizer_algorithm.drawing_households.checking_against_joint_distribution(person_objective_frequency,
                                                                                                                                    synthetic_person_attributes, person_dimensions,
                                                                                                                                     pumano, tract, bg)
        stat = synth_person_stat
        dof = count_person - 1

        p_value = scipy.stats.stats.chisqprob(stat, dof)
        if p_value > max_p or stat < min_chi:
            max_p = p_value
            max_p_housing_attributes = synthetic_housing_attributes
            max_p_person_attributes = synthetic_person_attributes
            min_chi = stat

    if draw_count >= parameters.synPopDraws:
        print ('Max Iterations (%d) reached for drawing households with the best draw having a p-value of %.4f' 
               %(parameters.synPopDraws, max_p))
    else:
        print 'Population with desirable p-value of %.4f was obtained in %d iterations' %(max_p, draw_count)


    synthesizer_algorithm.drawing_households.storing_synthetic_attributes(db, 'housing', max_p_housing_attributes, county, tract, bg)

    synthesizer_algorithm.drawing_households.storing_synthetic_attributes(db, 'person', max_p_person_attributes, county, tract, bg)

    

    values = (int(state), int(county), int(tract), int(bg), min_chi, max_p, draw_count, iteration, conv_crit_array[-1])
    synthesizer_algorithm.drawing_households.store_performance_statistics(db, geo, values)

    dbc.execute('select childpresence1 + childpresence2 from hhld_marginals where county = %s and tract = %s and bg = %s'%(county, tract, bg))
    hhld_total = dbc.fetchall()[0][0]

    dbc.execute('select groupquarter1 + groupquarter2 from gq_marginals where county = %s and tract = %s and bg = %s'%(county, tract, bg))
    gq_total = dbc.fetchall()[0][0]


    dbc.execute('select gender1 + gender2 from person_marginals where county = %s and tract = %s and bg = %s'%(county, tract, bg))
    persontotal = dbc.fetchall()[0][0]

    print 'Number of Synthetic Household - %d, and given Household total from the Census SF - %d' %(sum(max_p_housing_attributes[:,-2]), hhld_total + gq_total)
    print 'Number of Synthetic Persons - %d and given Person total from the Census SF - %d' %(sum(max_p_person_attributes[:,-2]), persontotal)
    print 'Synthetic households created for the geography in %.2f\n' %(time.clock()-ti)



    db.commit()
    dbc.close()
    db.close()

def run_parallel(project, geoIds, indexMatrix, pIndexMatrix, dbList, varCorrDict):

    fileLoc = "%s/%s/%s.pop" %(project.location, project.name, project.filename)

    start = time.time()
    ppservers = ()
    if len(sys.argv) > 1:
        ncpus = int(sys.argv[1])
        job_server = pp.Server(ncpus, ppservers = ppservers)
    else:
        job_server = pp.Server(ppservers=ppservers)

    print 'Number of geographies is %s'%(len(geoIds))
    modules = ('synthesizer_algorithm.heuristic_algorithm',
               'synthesizer_algorithm.drawing_households',
               'synthesizer_algorithm.adjusting_sample_joint_distribution',
               'synthesizer_algorithm.ipf',
               'pickle', 
               'scipy',
               'numpy',
               'pylab',
               'MySQLdb',
               'time',
               'scipy.stats')
    print 'Using %d cores on the processor' %(job_server.get_ncpus())
    
    geoIds = [Geography(geo[0], geo[1], geo[3], geo[4], geo[2]) for geo in geoIds]


    jobs = [(geo, job_server.submit(configure_and_run, (fileLoc,
                                                        geo,
                                                        varCorrDict,
                                                        dbList, 
                                                        indexMatrix, 
                                                        pIndexMatrix), (), modules)) for geo in geoIds]

    for geo, job in jobs:
        print job()
    job_server.print_stats()

    print ' Total time for puma - %.2f, Timing per geography - %.2f' %(time.time()-start, (time.time()-start)/len(geoIds))



