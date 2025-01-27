# PopGen 1.1 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand
# Copyright (C) 2009, Arizona State University
# See PopGen/License

import MySQLdb
import numpy
import adjusting_sample_joint_distribution
import drawing_households
import psuedo_sparse_matrix
import psuedo_sparse_matrix_nogqs
import time

def prepare_data_nogqs(db, project, state=None):

    if state == None:
	stateFilterStr = ""
    else:
	stateFilterStr = " where state = %s" %(state)

    dbc = db.cursor()
    scenarioDatabase = '%s%s%s' %(project.name, 'scenario', project.scenario)
    projectDatabase = project.name

    try:
        dbc.execute('drop table %s.hhld_sample' %(scenarioDatabase))
        dbc.execute('drop table %s.person_sample' %(scenarioDatabase))
        dbc.execute('drop table %s.hhld_marginals' %(scenarioDatabase))
        dbc.execute('drop table %s.person_marginals' %(scenarioDatabase))
        if project.sampleUserProv.defSource == 'ACS 2005-2007':
            dbc.execute('drop table %s.serialcorr' %(scenarioDatabase))
    except:
        pass

    dbc.execute('create table %s.hhld_sample select * from %s.hhld_sample %s'
                %(scenarioDatabase, projectDatabase, stateFilterStr))
    dbc.execute('alter table %s.hhld_sample add index(serialno)' %(scenarioDatabase))
    
    dbc.execute('create table %s.person_sample select * from %s.person_sample %s'
                %(scenarioDatabase, projectDatabase, stateFilterStr))
    dbc.execute('alter table %s.person_sample add index(serialno, pnum)' %(scenarioDatabase))

    if project.selVariableDicts.hhldMargsModify:
        dbc.execute('create table %s.hhld_marginals select * from %s.hhld_marginals_modpgq'
                    %(scenarioDatabase, projectDatabase))
    else:
        dbc.execute('create table %s.hhld_marginals select * from %s.hhld_marginals'
                    %(scenarioDatabase, projectDatabase))


    if project.sampleUserProv.defSource == 'ACS 2005-2007':
        dbc.execute('create table %s.serialcorr select * from %s.serialcorr'
                    %(scenarioDatabase, projectDatabase))

    try:
        dbc.execute('create table %s.person_marginals select * from %s.person_marginals'
                    %(scenarioDatabase, projectDatabase))
    except Exception, e:
        print e
        pass


#    Processes/ methods to be called at the beginning of the pop_synthesis process

# Identifying the number of housing units to build the Master Matrix
    dbc.execute('select * from hhld_sample')
    hhld_units = dbc.rowcount

    ti = time.clock()
# Identifying the control variables for the households, and persons
    hhld_control_variables = project.hhldVars
    person_control_variables = project.personVars

# Identifying the number of categories within each control variable for the households, and persons
    hhld_dimensions = project.hhldDims
    person_dimensions = project.personDims

    print '------------------------------------------------------------------'
    print 'Preparing Data for the Synthesizer Run'
    print '------------------------------------------------------------------'
    print 'Dimensions and Control Variables in %.4f' %(time.clock()-ti)
    ti = time.clock()

    update_string = adjusting_sample_joint_distribution.create_update_string(db, hhld_control_variables, hhld_dimensions)
    adjusting_sample_joint_distribution.add_unique_id(db, 'hhld_sample', 'hhld', update_string)
    update_string = adjusting_sample_joint_distribution.create_update_string(db, person_control_variables, person_dimensions)
    adjusting_sample_joint_distribution.add_unique_id(db, 'person_sample', 'person', update_string)

    print 'Uniqueid\'s in %.4fs' %(time.clock()-ti)
    ti = time.clock()

# Populating the Master Matrix
    populated_matrix = psuedo_sparse_matrix_nogqs.populate_master_matrix(db, 99999, hhld_units, hhld_dimensions,
                                                                   person_dimensions)
    print 'Populated in %.4fs' %(time.clock()-ti)
    ti = time.clock()

# Sparse representation of the Master Matrix
    ps_sp_matrix = psuedo_sparse_matrix.psuedo_sparse_matrix(db, populated_matrix, 99999, project)
    print 'Psuedo Sparse Matrix in %.4fs' %(time.clock()-ti)
    ti = time.clock()
#______________________________________________________________________
#Creating Index Matrix
    index_matrix = psuedo_sparse_matrix.generate_index_matrix(db, 99999)
    print 'Index Matrix in %.4fs' %(time.clock()-ti)
    ti = time.clock()
    dbc.close()

#______________________________________________________________________
# creating synthetic_population tables in MySQL
    drawing_households.create_synthetic_attribute_tables(db)

# creating performance_statistics table in MySQL
    drawing_households.create_performance_table(db)

# Total PUMS Sample x composite_type adjustment for hhld
    adjusting_sample_joint_distribution.create_joint_dist(db, 'hhld', hhld_control_variables, hhld_dimensions, 0, 0, 0)

# Total PUMS Sample x composite_type adjustment for person
    adjusting_sample_joint_distribution.create_joint_dist(db, 'person', person_control_variables, person_dimensions, 0, 0, 0)


if __name__ == '__main__':


    db = MySQLdb.connect(user = 'root', passwd = '1234', db = 'aacog')
    prepare_data(db)
    db.commit()
    db.close()

