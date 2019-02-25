import numpy as np
import xarray as xr
import re

def distance(val, ref):
    return abs(ref - val)
vectDistance = np.vectorize(distance)

def getClosest(sortedMatrix, column, val):
    while len(sortedMatrix) > 3:
        half = int(len(sortedMatrix) / 2)
        sortedMatrix = sortedMatrix[-half - 1:] if sortedMatrix[half, column] < val else sortedMatrix[: half + 1]
    if len(sortedMatrix) == 1:
        result = sortedMatrix[0].copy()
        result[column] = val
        return result
    else:
        safecopy = sortedMatrix.copy()
        safecopy[:, column] = vectDistance(safecopy[:, column], val)
        minidx = np.argmin(safecopy[:, column])
        safecopy = safecopy[minidx, :].A1
        safecopy[column] = val
        return safecopy

def convert(column, samples, matrix):
    return np.matrix([getClosest(matrix, column, t) for t in samples])

def valueOrEmptySet(k, d):
    return (d[k] if isinstance(d[k], set) else {d[k]}) if k in d else set()

def mergeDicts(d1, d2):
    """
    Creates a new dictionary whose keys are the union of the keys of two
    dictionaries, and whose values are the union of values.

    Parameters
    ----------
    d1: dict
        dictionary whose values are sets
    d2: dict
        dictionary whose values are sets

    Returns
    -------
    dict
        A dict whose keys are the union of the keys of two dictionaries,
    and whose values are the union of values

    """
    res = {}
    for k in d1.keys() | d2.keys():
        res[k] = valueOrEmptySet(k, d1) | valueOrEmptySet(k, d2)
    return res

def extractCoordinates(filename):
    """
    Scans the header of an Alchemist file in search of the variables.

    Parameters
    ----------
    filename : str
        path to the target file
    mergewith : dict
        a dictionary whose dimensions will be merged with the returned one

    Returns
    -------
    dict
        A dictionary whose keys are strings (coordinate name) and values are
        lists (set of variable values)

    """
    with open(filename, 'r') as file:
        regex = re.compile(' (?P<varName>[a-zA-Z]+) = (?P<varValue>[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?),?')
        dataBegin = re.compile('\d')
        for line in file:
            match = regex.findall(line)
            if match:
                return {var : float(value) for var, value in match}
            elif dataBegin.match(line[0]):
                return {}

def extractVariableNames(filename):
    """
    Gets the variable names from the Alchemist data files header.

    Parameters
    ----------
    filename : str
        path to the target file

    Returns
    -------
    list of list
        A matrix with the values of the csv file

    """
    with open(filename, 'r') as file:
        dataBegin = re.compile('\d')
        lastHeaderLine = ''
        for line in file:
            if dataBegin.match(line[0]):
                break
            else:
                lastHeaderLine = line
        if lastHeaderLine:
            regex = re.compile(' (?P<varName>\S+)')
            return regex.findall(lastHeaderLine)
        return []

def openCsv(path):
    """
    Converts an Alchemist export file into a list of lists representing the matrix of values.

    Parameters
    ----------
    path : str
        path to the target file

    Returns
    -------
    list of list
        A matrix with the values of the csv file

    """
    regex = re.compile('\d')
    with open(path, 'r') as file:
        lines = filter(lambda x: regex.match(x[0]), file.readlines())
        return [[float(x) for x in line.split()] for line in lines]

if __name__ == '__main__':
    # CONFIGURE SCRIPT
    directory = 'data'
    pickleOutput = 'data_summary'
    experiments = ['vienna', 'corridor']
    floatPrecision = '{: 0.2f}'
    seedVars = ['seed']
    timeSamples = 600
    minTime = 0
    maxTime = 600
    timeColumnName = 'time'
    logarithmicTime = False
    
    # Setup libraries
    np.set_printoptions(formatter={'float': floatPrecision.format})
    # Read the last time the data was processed, reprocess only if new data exists, otherwise just load
    import pickle
    import os
    newestFileTime = max(os.path.getmtime(directory + '/' + file) for file in os.listdir(directory))
    try:
        lastTimeProcessed = pickle.load(open('timeprocessed', 'rb'))
    except:
        lastTimeProcessed = -1
    shouldRecompute = newestFileTime != lastTimeProcessed
    if not shouldRecompute:
        try:
            means = pickle.load(open(pickleOutput + '_mean', 'rb'))
            stdevs = pickle.load(open(pickleOutput + '_std', 'rb'))
        except:
            shouldRecompute = True
    if shouldRecompute:
        timefun = np.logspace if logarithmicTime else np.linspace
        means = {}
        stdevs = {}
        for experiment in experiments:
            # Collect all files for the experiment of interest
            import fnmatch
            allfiles = filter(lambda file: fnmatch.fnmatch(file, experiment + '_*.txt'), os.listdir(directory))
            allfiles = [directory + '/' + name for name in allfiles]
            allfiles.sort()
            # From the file name, extract the independent variables
            dimensions = {}
            for file in allfiles:
                dimensions = mergeDicts(dimensions, extractCoordinates(file))
            dimensions = {k: sorted(v) for k, v in dimensions.items()}
            # Add time to the independent variables
            dimensions[timeColumnName] = range(0, timeSamples)
            # Compute the matrix shape
            shape = tuple(len(v) for k, v in dimensions.items())
            # Prepare the Dataset
            dataset = xr.Dataset()
            for k, v in dimensions.items():
                dataset.coords[k] = v
            if len(allfiles) == 0:
                print("WARNING: No data for experiment " + experiment)
            else:
                varNames = extractVariableNames(allfiles[0])
                for v in varNames:
                    if v != timeColumnName:
                        novals = np.ndarray(shape)
                        novals.fill(float('nan'))
                        dataset[v] = (dimensions.keys(), novals)
                # Compute maximum and minimum time, create the resample
                timeColumn = varNames.index(timeColumnName)
                allData = { file: np.matrix(openCsv(file)) for file in allfiles }
                computeMin = minTime is None
                computeMax = maxTime is None
                if computeMax:
                    maxTime = float('-inf')
                    for data in allData.values():
                        maxTime = max(maxTime, data[-1, timeColumn])
                if computeMin:
                    minTime = float('inf')
                    for data in allData.values():
                        minTime = min(minTime, data[0, timeColumn])
                timeline = timefun(minTime, maxTime, timeSamples)
                # Resample
                for file in allData:
                    allData[file] = convert(timeColumn, timeline, allData[file])
                # Populate the dataset
                for file, data in allData.items():
                    dataset[timeColumnName] = timeline
                    for idx, v in enumerate(varNames):
                        if v != timeColumnName:
                            darray = dataset[v]
                            experimentVars = extractCoordinates(file)
                            darray.loc[experimentVars] = data[:, idx].A1
                # Fold the dataset along the seed variables, producing the mean and stdev datasets
                means[experiment] = dataset.mean(seedVars)
                stdevs[experiment] = dataset.std(seedVars)
        # Save the datasets
        pickle.dump(means, open(pickleOutput + '_mean', 'wb'), protocol=-1)
        pickle.dump(stdevs, open(pickleOutput + '_std', 'wb'), protocol=-1)
        pickle.dump(newestFileTime, open('timeprocessed', 'wb'))

    # Prepare the charting system
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.cm as cmx
    matplotlib.rcParams.update({'axes.titlesize': 12})
    matplotlib.rcParams.update({'axes.labelsize': 10})
#    colormap = cmx.viridis

    # Prepare selected charts
    # Evaluation of the backoff parameter
    def makechart(xdata, ydata, title = None, ylabel = None, xlabel = None, colors = None, figure_size = (6, 4)):
        fig = plt.figure(figsize = figure_size)
        ax = fig.add_subplot(1, 1, 1)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
#        ax.set_ylim(0)
        ax.set_xlim(min(xdata), max(xdata))
        index = 0
        for (label, data) in ydata.items():
            ax.plot(xdata, data, label=label, color=colors(index / (len(ydata) - 1)) if colors else None)
            index += 1
        return (fig, ax)
    
    # Corridor
    chartseriesdata = means['corridor']
    xdata = chartseriesdata['time']
    mixcolormap = lambda x: cmx.winter(x * 2) if x < 0.5 else cmx.YlOrRd((x - 0.5) * 2 * 0.6 + 0.3)
    divergingmixcolormap = lambda x: cmx.winter(1 - x * 2) if x < 0.5 else cmx.YlOrRd((x - 0.5) * 2 * 0.6 + 0.3)
    for errtype in ['d', 't']:
        metric = 'time' if errtype == 't' else 'distance'
        for testtype in ['single', 'stack']:
            kinds = ['broadcast', 'collection', 'distance']
            (fig, ax) = makechart(
                title = testtype + ' computations, error in ' + metric,
                xdata = xdata,
                ydata = { algo + '-' + kind : chartseriesdata[label] for
                     algo in ['rep', 'share'] for
                     kind in kinds for
                     label in [ errtype + 'err-' + testtype + '-' + kind + '-' + algo + '[Mean]'] 
                },
                ylabel = metric + " error",
                xlabel = 'simulated time (s)',
                figure_size = (6, 3),
                colors = divergingmixcolormap
            )
            ax.set_xlim(0, 300)
            ax.set_yscale('symlog')
            ax.set_ylim(0, ax.get_ylim()[1])
            if metric == 'time' and testtype == 'stack':
                ax.legend(ncol = 2, loc='lower right')
            fig.tight_layout()
            fig.savefig('corridor-' + errtype + testtype + '.pdf')
#            for kind in kinds:
#                (fig, ax) = makechart(
#                    title = kind + ' computation, ' + testtype + '. Y: ' + metric + ' error. X: simulated time (s).',
##                    ylabel = metric + " error",
#                    xdata = xdata,
#                    ydata = { algo : chartseriesdata[label] for
#                         algo in ['rep', 'share'] for
#                         label in [ errtype + 'err-' + testtype + '-' + kind + '-' + algo + '[Mean]'] 
#                    },
#                    figure_size = (6, 1.5)
#                )
##                ax.legend(ncol = 1, bbox_to_anchor=(1, 0.5))
#                ax.set_xlim(0, 300)
#                fig.tight_layout()
#                fig.savefig(errtype + testtype + kind + '.pdf')
    
    # Vienna
    chartseriesdata = means['vienna']
    for metric in ['distance', 'leader']:
        what = 'distance error' if metric == 'distance' else 'leaders count'
        (fig, ax) = makechart(
#            title = what ,
            ylabel = what,
            xlabel = 'simulated time (s)',
            xdata = xdata,
            ydata = { algo : chartseriesdata[label] for
                 algo in ['rep', 'share'] for
                 label in [ metric + '-' + algo + ('[Mean]' if metric == 'distance' else '[CountDistinct]')] 
            },
            colors = mixcolormap,
            figure_size = (6, 3)
        )
        ax.legend()
#        ax.set_xlim(0, 500 if metric == 'distance' else 200)
        ax.set_yscale('symlog')
        fig.tight_layout()
        fig.savefig('vienna-' + metric + '.pdf')
        
        