import csv
import numpy as np
import scipy.stats
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import argparse
import glob
import sys
from scipy.spatial.distance import pdist, squareform
from sklearn import datasets
from scipy.cluster.hierarchy import linkage
import tadanalysisutil as tad

newpalette = ['#8dd3c7','#58508d','#bc5090','#003f5c','#ff6361']
sns.set(style='whitegrid',palette=sns.color_palette(newpalette),color_codes=False,font='Ubuntu')

def readHiCRepFile(filename):
    hicrepvals = {}
    tissuedonors = []
    smtissues = ['SkelMuscleM54','SkelMuscleM37','SkelMuscleF53','SkelMuscleF51']
    tctissues = ['TransColonM54','TransColonM37','TransColonF53','TransColonF51']
    othertissues = ['Lung','Psoas','Pancreas','Spleen']
    with open(filename,'rb') as f:
        freader = csv.reader(f,delimiter=' ')
        for line in freader:
            if len(line) < 2 or line[0] == line[1]: continue
            if (line[0] in smtissues and line[1] in smtissues) or (line[0] in tctissues and line[1] in tctissues) or (line[0][:-1] == line[1][:-1] and any(tissue in line[0] for tissue in othertissues)):
                tissuedonors.extend([float(line[2])])
            elif line[0] in smtissues+tctissues or line[1] in smtissues+tctissues: 
                continue 
            elif line[0][:3] != 'set' and line[0][:2] != 'no' and (line[1],line[0]) not in hicrepvals:
                hicrepvals[(line[0],line[1])] = float(line[2])
    return hicrepvals,tissuedonors

def resFragAnalysis(hicrepvals,measure,outputloc):

    resfragdata = [['hESC_DpnII_rep', 'hESC_HindIII', 'hESC_NcoI'], ['HFF-hTERT_DpnII', 'HFF-hTERT_HindIII_beads', 'HFF-hTERT_HindIII_plate', 'HFF-hTERT_MboI', 'HFF-hTERT_NcoI']]
    resfragscores = [[],[]]
    background = []
    for key, score in hicrepvals.iteritems():
        if (key[0] in resfragdata[0] and key[1] in resfragdata[0]):
            resfragscores[0].extend([score])
            #print key, score
        elif (key[0] in resfragdata[1] and key[1] in resfragdata[1]):
            resfragscores[1].extend([score])
            #print key, score
        else:
            background.extend([score])

    tad.plotResFragResults(resfragscores, background, measure, outputloc+'hicrep_resfragboxplot_violin.pdf')

def acrossLabAnalysis(hicrepvals,hicrepvals_rep,measure,outputloc):

    acrosslabdata = [['hESC_Dixon2015','hESC_FP','hESC_HindIII','hESC_Jin','hESC'],['IMR90dixon', 'IMR90rao', 'IMR90_normal', 'IMR90_RI']]
    acrosslabscores = [[],[]]
    background = []
    for key,score in hicrepvals.iteritems():
        if (key[0] in acrosslabdata[0] and key[1] in acrosslabdata[0]):
            acrosslabscores[0].extend([score])
            #print key, acrosslabscores[0][-1]
        elif (key[0] in acrosslabdata[1] and key[1] in acrosslabdata[1]):
            acrosslabscores[1].extend([score])
            #print key,acrosslabscores[1][-1]
        else:
            background.extend([score])

    tad.plotAcrossLabResults(acrosslabscores, background, hicrepvals_rep.values(), measure, outputloc+'hicrep_acrosslabboxplot_violin.pdf')

def insituDilutionAnalysis(hicrepvals,hicrepvals_rep,measure,outputloc):

    dil = ['A549','Caki2','G401','LNCaP-FGC','NCI-H460','Panc1','RPMI-7951','SKMEL5','SKNDZ','SKNMC','T47D','IMR90dixon','hESC','hESC_HindIII','HFF-hTERT_HindIII_techreps','HG00733','HG00732','HG00731','HG00514','HG00513','HG00512','GM19238','GM19239','GM19240','hESC_Jin','IMR90_flav','IMR90_normal','IMR90_tnfa','hESC_Dixon2015','GM20431','BrainMicroEndo','AstrocyteCerebellum','AstrocyteSpinalCord','DLD1','BrainPericyte','EndomMicroEndoth','HepSin','ACHN','IMR90_RI','hESC_FP','Adrenal','Bladder','DPC','Hippocampus','Lung','Ovary','Pancreas','Psoas','RightVentricle','SmallBowel','Spleen']
    insitu = ['HFF-hTERT_HindIII_beads','HFF-hTERT_HindIII_plate', 'IMR90rao','GM12878','HMEC','HUVEC','K562rao','KBM7','NHEK','HFF-hTERT_MboI','SkelMuscle','TransColon','hESC_NcoI','HFF-hTERT_NcoI','hESC_DpnII', 'hESC_DpnII_rep','HFF-hTERT_DpnII','HFF-c6']

    ispairs = []
    dilpairs = []
    isdil = []
    samecelltypediffexp = []
    samecelltypesameexp = [[],[]] # 1 list for in situ, 1 for dilution
    for key,score in hicrepvals.iteritems():
        if (key[0] in dil and key[1] in dil):
            dilpairs.extend([score])
            if '_flav' in key[0] or '_flav' in key[1] or '_tnfa' in key[0] or '_tnfa' in key[1]: continue
            if ('IMR90' in key[0] and 'IMR90' in key[1]) or ('hESC' in key[0] and 'hESC' in key[1]) or ('HFF-hTERT' in key[0] and 'HFF-hTERT' in key[1]):
                samecelltypesameexp[1].extend([score])
        elif key[0] in insitu and key[1] in insitu:
            ispairs.extend([score])
            if '_flav' in key[0] or '_flav' in key[1] or '_tnfa' in key[0] or '_tnfa' in key[1]: continue
            if ('IMR90' in key[0] and 'IMR90' in key[1]) or ('hESC' in key[0] and 'hESC' in key[1]) or ('HFF-hTERT' in key[0] and 'HFF-hTERT' in key[1]):
                samecelltypesameexp[0].extend([score])
        else:
            isdil.extend([score])
            if '_flav' in key[0] or '_flav' in key[1] or '_tnfa' in key[0] or '_tnfa' in key[1]: continue
            if ('IMR90' in key[0] and 'IMR90' in key[1]) or ('hESC' in key[0] and 'hESC' in key[1]) or ('HFF-hTERT' in key[0] and 'HFF-hTERT' in key[1]):
                samecelltypediffexp.extend([score])

    diffcelltype = []
    for key,score in hicrepvals.iteritems():
        ct1split = key[0].split('_')
        ct2split = key[1].split('_')
        if ct1split[0] != ct2split[0]:
            diffcelltype.extend([score])

    tad.plotISDilPairs(ispairs,dilpairs,isdil,measure,outputloc+'hicrep_protocolpairboxplot_violin.pdf')
    tad.plotSameCellTypeBoxplots(samecelltypediffexp, samecelltypesameexp, diffcelltype, measure, outputloc+'hicrep_samecelltype_protocol_comparison_violin.pdf')

    dilreps = []
    isreps = []
    for key,score in hicrepvals_rep.iteritems():
        celltypename = key[0].split('_')[:-1]
        celltypename = '_'.join(celltypename)
        if celltypename in dil:
            dilreps.extend([score])
        elif celltypename in insitu:
            isreps.extend([score])
    print 'total number of dilution replicate pairs =', len(dilreps)
    print 'total number of in situ replicate pairs =', len(isreps)
    tad.protocolRepBoxplots(isreps,dilreps,measure,outputloc+'hicrep_protocolrepboxplot_violin.pdf')

def tissueAnalysis(hicrepvals,hicrepvals_donor,hicrepvals_rep,measure,outputloc):

    withintissue = hicrepvals_donor
    acrosstissue = []
    background = []
    replicates = []
    tissuesamps = ['SkelMuscle','TransColon','Adrenal','Bladder','DPC','Hippocampus','Lung','Ovary','Pancreas','Psoas','RightVentricle','SmallBowel','Spleen']
    for key,score in hicrepvals.iteritems():
        if key[0] in tissuesamps and key[1] in tissuesamps:
            acrosstissue.extend([score])
        else:
            background.extend([score])
    for key,score in hicrepvals_rep.iteritems():
        if key[0] in ['Lung_rep1','Pancreas_rep1','Psoas_rep1','Spleen_rep1']:
            withintissue.extend([score])
        else:
            replicates.extend([score])
    tad.plotTissueBoxplots(withintissue, acrosstissue, replicates, background, measure, outputloc+'hicrep_tissueboxplots_violin.pdf')

def trioAnalysis(hicrepvals,hicrepvals_rep,measure,outputloc):

    withintrio = []
    acrosstrio = []
    background = []
    bloodlymph = []
    parentchild = []
    parentparent = []
    children = ['HG00733', 'HG00514', 'GM19240']
    bloodlymphtypes = ['GM12878','GM20431','GM19240','GM19239','GM19238','HG00733','HG00732','HG00731','HG00514','HG00513','HG00512']
    for key,score in hicrepvals.iteritems():
        if key[0][:5] == key[1][:5] and (key[0][:4] == 'HG00' or key[0][:4] == 'GM19'):
            #print 'within trio,',key
            withintrio.extend([score])
            if key[0] in children or key[1] in children:
                parentchild.extend([score])
                #print 'parentchild',key,score
            elif key[0] != key[1]:
                parentparent.extend([score])
                #print 'parentparent',key,score
        elif key[0][:5] != key[1][:5] and (key[0][:4] == 'HG00' or key[0][:4] == 'GM19') and (key[1][:4] == 'HG00' or key[1][:4] == 'GM19'):
            acrosstrio.extend([score])
            bloodlymph.extend([score])
            #print 'across trio,', key
        elif key[0] in bloodlymphtypes and key[1] in bloodlymphtypes:
            #print key
            bloodlymph.extend([score])
        else:
            background.extend([score])
    trioreps = []
    for key,score in hicrepvals_rep.iteritems():
        if key[0][:4] == 'GM19' or key[0][:4] == 'HG00':
            trioreps.extend([score])

    tad.plotTrioBoxplots(parentchild,parentparent,trioreps,bloodlymph,background,measure,outputloc+'hicrep_trioboxplots_byfamily_violin.pdf')


def main(file_hicrep, file_replicates_hicrep, rawcountsfile, outputloc):

    measure = 'HiCRep'

    hicrepvals,hicrep_donors = readHiCRepFile(file_hicrep)
    hicrepvals_rep,moredonors = readHiCRepFile(file_replicates_hicrep)
    hicrep_donors += moredonors

    #check for missing pairs
    #allpairs = []
    #with open('go/testing/allhicsamplepairs.txt','rb') as f:
    #    freader = csv.reader(f,delimiter=' ')
    #    for line in freader:
    #        allpairs.extend([(line[0],line[1])])
    #for pair in allpairs:
    #    if pair not in hicrepvals and (pair[1],pair[0]) not in hicrepvals:
    #        print pair
    #for key in hicrepvals.keys():
    #    if key not in allpairs and (key[1],key[0]) not in allpairs:
    #        print key

    print 'total non-replicate pairs:', len(hicrepvals)
    print 'total replicate pairs:', len(hicrepvals_rep)

    if len(rawcountsfile) > 0:
        rawcontactcounts = tad.readRawCountsFile(rawcountsfile)
        tad.plotSimVContactCounts(rawcontactcounts, hicrepvals_rep, measure, outputloc+'hicrep_rawcountsVrephicrep_sns.pdf')

    tad.generateHeatMap(hicrepvals, measure, outputloc+'hicrep_fullheatmap_sns.png')
    tad.plotReplicateVNonReplicate(hicrepvals_rep.values(), hicrepvals.values(), [], measure, outputloc+'hicrep_replicateVnonreplicate_violin.pdf')

    resFragAnalysis(hicrepvals,measure,outputloc)
    acrossLabAnalysis(hicrepvals,hicrepvals_rep,measure,outputloc)
    insituDilutionAnalysis(hicrepvals,hicrepvals_rep,measure,outputloc)
    tissueAnalysis(hicrepvals, hicrep_donors, hicrepvals_rep, measure, outputloc)
    trioAnalysis(hicrepvals,hicrepvals_rep,measure,outputloc)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('-i', type=str, help='File containing HiCRep results on non-replicates')
    parser.add_argument('-ir', type=str, help='File containing HiCRep results on replicates')
    parser.add_argument('-rcf', type=str, default='', help='Raw count file')
    parser.add_argument('-o', type=str, help='Location for output files')

    args = parser.parse_args()
    main(args.i, args.ir, args.rcf, args.o)
