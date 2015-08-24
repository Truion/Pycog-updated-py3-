#! /usr/bin/env python
"""
Sample script for performing common tasks.

"""
from __future__ import division

import argparse
import imp
import os
import shutil
import subprocess
import sys
import time

from pycog.utils import mkdir_p

#=========================================================================================
# Command line
#=========================================================================================

p = argparse.ArgumentParser()
p.add_argument('model_file', help="model specification")
p.add_argument('action', nargs='?', default='check')
p.add_argument('args', nargs='*')
p.add_argument('-p', '--ppn', type=int, default=1)
p.add_argument('-g', '--gpus', type=int, default=0)
p.add_argument('-s', '--seed', type=int, default=100)
a = p.parse_args()

modelfile = os.path.abspath(a.model_file)
if not modelfile.endswith('.py'):
    modelfile += '.py'

action = a.action
args   = a.args
seed   = a.seed
ppn    = a.ppn
gpus   = a.gpus

print("MODELFILE: " + str(modelfile))
print("ACTION:    " + str(action))
print("ARGS:      " + str(args))
print("SEED:      " + str(seed))

#=========================================================================================
# Setup paths
#=========================================================================================

# Location of script
here   = os.path.dirname(os.path.realpath(__file__))
prefix = here.split('/')[-1]

# Name to use
name = os.path.splitext(modelfile.split('/')[-1])[0]

# Scratch
scratchroot = os.environ.get('SCRATCH', '{}/scratch'.format(os.environ['HOME']))
scratchpath = '{}/work/{}/{}'.format(scratchroot, prefix, name)

# Theano
theanopath = scratchpath + '/theano'

# Paths
workpath   = here + '/work'
datapath   = workpath + '/data/' + name
figspath   = workpath + '/figs/' + name
trialspath = scratchpath + '/trials'

# Create necessary directories
for path in [datapath, figspath, scratchpath, trialspath]:
    mkdir_p(path)

# File to store model in
savefile = '{}/{}.pkl'.format(datapath, name)

#=========================================================================================
# Check log file
#=========================================================================================

if action == 'check':
    try:
        action = args[0]
    except IndexError:
        action = 'train'

    jobname = name
    if action != 'train':
        jobname += '_' + action

    logfile = '{}/{}.log'.format(scratchpath, name)
    try:
        with open(logfile, 'r') as f:
            shutil.copyfileobj(f, sys.stdout)
    except IOError:
        print("Couldn't open {}".format(logfile))
        sys.exit()
    print("")

#=========================================================================================
# Clean
#=========================================================================================

elif action == 'clean':
    from glob import glob

    # Data files
    base, ext = os.path.splitext(savefile)
    fnames = glob(base + '*' + ext)
    for fname in fnames:
        os.remove(fname)
        print("Removed {}".format(fname))

    # Theano compile directories
    fnames = glob('{}/{}-*'.format(theanopath, name))
    for fname in fnames:
        shutil.rmtree(fname)
        print("Removed {}".format(fname))

#=========================================================================================
# Submit jobs
#=========================================================================================

elif action == 'submit':
    from pycog import pbstools

    if len(args) > 0:
        action = args[0]
        args   = args[1:]
    else:
        action = 'train'

    jobname = name
    if action != 'train':
        jobname += '_' + action

    if len(args) > 0:
        sargs = ' ' + ' '.join(args)
    else:
        sargs = ''

    cmd = ''
    if gpus > 0:
        cmd = 'THEANO_FLAGS=device=gpu,nvcc.fastmath=True '

    cmd     += 'python {}/master.py {} {}{}'.format(here, modelfile, action, sargs)
    pbspath  = workpath + '/pbs'

    jobfile = pbstools.write_jobfile(cmd, jobname, pbspath, scratchpath, 
                                     ppn=ppn, gpus=gpus)
    subprocess.call(['qsub', jobfile])

#=========================================================================================
# Train
#=========================================================================================

elif action == 'train':
    from pycog import Model

    # Model specification
    model = Model(modelfile=modelfile)

    # Avoid locks on the cluster
    compiledir = '{}/{}-{}'.format(theanopath, name, int(time.time()))

    # Train
    model.train(savefile, seed=seed, compiledir=compiledir)

#=========================================================================================
# Test spontaneous state
#=========================================================================================

elif action == 'spontaneous':
    import numpy as np

    from pycog import RNN

    rnn = RNN(savefile, {'dt': 0.5}, verbose=True)
    rnn.run(1000)

    mean = np.mean(rnn.u, axis=1)
    std  = np.std(rnn.u, axis=1)
    print(mean, std)

    from pycog.figtools import Figure

    fig  = Figure()
    plot = fig.add()

    plot.plot(rnn.t, rnn.u[0], color=Figure.colors('blue'))

    fig.save(path=figspath, name=name+'_'+action)
    fig.close()

#=========================================================================================
# Plot network structure
#=========================================================================================

elif action == 'structure':
    from pycog import RNN

    # Create RNN
    if 'init' in args:
        print("* Initial network.")
        base, ext = os.path.splitext(savefile)
        savefile_init = base + '_init' + ext
        rnn = RNN(savefile_init, verbose=True)
    else:
        rnn = RNN(savefile, verbose=True)

    # Sort order for recurrent units
    sortby = None
    if len(args) > 0:
        if args[0] == 'selectivity':
            filename = '{}/{}_selectivity.txt'.format(datapath, name)
        else:
            filename = os.path.abspath(args[0])

        if os.path.isfile(filename):
            sortby = filename

    # Create figure
    fig = rnn.plot_structure(sortby=sortby)
    fig.save(path=figspath, name=name+'_'+action)
    fig.close()

#=========================================================================================
# Plot costs history
#=========================================================================================

elif action == 'costs':
    from pycog import RNN

    # Create RNN
    rnn = RNN(savefile, verbose=True)

    # Create figure
    fig = rnn.plot_costs()
    fig.save(path=figspath, name=name+'_'+action)
    fig.close()

#=========================================================================================
# Run analysis
#=========================================================================================

elif action == 'run':
    if len(args) > 0:
        runfile = args[0]
        if not runfile.endswith('.py'):
            runfile += '.py'

        # Load analysis module
        try:
            r = imp.load_source('analysis', runfile)
        except IOError:
            print("Couldn't load analysis module from {}".format(runfile))
            sys.exit()

        # Load model
        try:
            m = imp.load_source('model', modelfile)
        except IOError:
            print("Couldn't load model module from {}".format(modelfile))
            sys.exit()

        # Reset args
        args = args[1:]
        if len(args) > 0:
            action = args[0]
            args   = args[1:]
        else:
            action = None
            args   = []

        params = {
            'seed':       seed,
            'model':      m,
            'savefile':   savefile,
            'name':       name,
            'datapath':   datapath,
            'figspath':   figspath,
            'trialspath': trialspath,
            'dt':         0.5,
            'dt_save':    2
            }
        r.do(action, args, params)

#=========================================================================================

else:
    print("Unrecognized action \'{}\'.".format(action))