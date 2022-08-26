# (c) 2020 Jonathan Kelsey
# This code is licensed under MIT license
from pyspark.sql import functions as F
import pyspark
import numpy as np
import sys

def seedKernel(dataB, dataIdValue, centeroids, k, metric):
    data = dataB.value
    print("hello????")
    print(dataB)
    print(dataB)
    print(dataB)
    point = dataIdValue[1]
    minD = sys.maxsize 
    for j in range(len(centeroids)): 
        distance = metric(point, data[centeroids[j]]) 
        minD = min(minD, distance)
    return int(minD)

def seedClusters(dataB, dataFrame, k, metric):
    data = dataB.value
    centeroids = list(np.random.choice(data.shape[0], 1, replace=False))
    for i in range(k - 1):
        print("clusterSeed", i)
        distances = []
        mK = dataFrame.rdd.map(lambda dataIdValue: seedKernel(dataB, dataIdValue, centeroids, k, metric))
        mK_collect = mK.collect()
        distances = np.array(mK_collect) 
        nextCenteroid = np.argmax(distances)
        centeroids.append(nextCenteroid) 
    print(centeroids)
    return centeroids 

def nearestCenteroidKernel(dataIdValue, centeroidIdValues, metric):
    dataId, dataValue = dataIdValue
    dataNp = np.asarray(dataValue)
    distances = []
    for centeroidId, centeroidValue in centeroidIdValues:
        centeroidNp = np.asarray(centeroidValue)
        distance = metric(dataNp, centeroidNp)
        distances.append(distance)
    distances = np.asarray(distances)
    closestCenteroid = np.argmin(distances)
    return int(closestCenteroid)

def optimiseClusterMembershipSpark(data, dataFrame, n, metric, intitalClusterIndices=None):
    dataShape = data.shape
    dataRDD = dataFrame.rdd
    lengthOfData = dataShape[0]
    if intitalClusterIndices is None:
        index = np.random.choice(lengthOfData, n, replace=False)
    else:
        index = intitalClusterIndices
    listIndex = [int(i) for i in list(index)]
    centeroidIdValues = [(i,data[index[i]]) for i in range(len(index))]
    dataRDD = dataRDD.filter(lambda dataIdValue: int(dataIdValue["id"]) not in listIndex)
    associatedClusterPoints = dataRDD.map(lambda dataIdValue: (dataIdValue[0],nearestCenteroidKernel(dataIdValue, centeroidIdValues, metric)))
    clusters = associatedClusterPoints.toDF(["id", "bestC"]).groupBy("bestC").agg(F.collect_list("id").alias("cluster"))
    return index, clusters

def costKernel(dataB, testCenteroid, clusterData, metric):
    data = dataB.value
    cluster = np.asarray(clusterData)
    lenCluster = cluster.shape[0]
    lenFeature = data.shape[1]
    testCenteroidColumn = np.zeros(shape=(lenCluster, lenFeature), dtype=data.dtype)
    newClusterColumn = np.zeros(shape=(lenCluster, lenFeature), dtype=data.dtype)
    for i in range(0, lenCluster):
        newClusterColumn[i] = data[cluster[i]]
        testCenteroidColumn[i] = data[int(testCenteroid)] 
    pairwiseDistance =  metric(newClusterColumn, testCenteroidColumn)# (np.absolute(newClusterColumn-testCenteroidColumn).sum(axis=1))# metric(newClusterColumn, testCenteroidColumn)
    cost = np.sum(pairwiseDistance)
    return float(cost) #newClusterColumn.shape[1]

def optimiseCentroidSelectionSpark(dataB, dataFrame, centeroids, clustersFrames, metric):
    data = dataB.value
    dataRDD = dataFrame.rdd
    dataShape = data.shape
    newCenteroidIds = []
    totalCost = 0
    for clusterIdx in range(len(centeroids)):
        print("clusterOpIdx", clusterIdx)
        oldCenteroid = centeroids[clusterIdx]
        clusterFrame = clustersFrames.filter(clustersFrames.bestC == clusterIdx).select(F.explode(clustersFrames.cluster))
        clusterData = clusterFrame.collect()
        if clusterData:
            clusterData = [clusterData[i].col for i in range(len(clusterData))]
        else:
            clusterData = []
        cluster = np.asarray(clusterData)
        costData = clusterFrame.rdd.map(lambda pointId: (pointId[0], costKernel(dataB, pointId[0], clusterData, metric)))
        #print(costData.toDF().show())
        cost = costData.map(lambda pointIdCost: pointIdCost[1]).sum()
        totalCost = totalCost + cost
        pointResult = costData.sortBy(lambda pointId_Cost: pointId_Cost[1]).take(1)
        if (pointResult):
            bestPoint = pointResult[0][0]
        else:
            bestPoint = oldCenteroid
        newCenteroidIds.append(bestPoint)
    return (newCenteroidIds, totalCost)

#vector metrics
def hammingVector(stack1, stack2):
    return (stack1 != stack2).sum(axis=1)
def euclideanVector(stack1, stack2):
    return (np.absolute(stack2-stack1)).sum(axis=1)
# point metrics
def euclideanPoint(p1, p2): 
    return np.sum((p1 - p2)**2) 
def hammingPoint(p1, p2): 
    return np.sum((p1 != p2))

def fit(sc, data, nRegions = 2, metric = "euclidean", seeding = "heuristic"):
    if metric == "euclidean":
        pointMetric = euclideanPoint
        vectorMetric = euclideanVector
    elif metric == "hamming":
        pointMetric = hammingPoint
        vectorMetric = hammingVector
    else:
        print("unsuported metric")
        return

    dataN = np.asarray(data)
    dataB = sc.broadcast(dataN)
    seeds = None
    dataFrame  = sc.parallelize(data).zipWithIndex().map(lambda xy: (xy[1],xy[0])).toDF(["id", "vector"]).cache()
    if (seeding == "heuristic"):
        seeds = list(seedClusters(dataB, dataFrame, nRegions, pointMetric))
    lastCenteroids, lastClusters = optimiseClusterMembershipSpark(dataN, dataFrame, nRegions, pointMetric, seeds)
    lastCost = float('inf')
    iteration = 0
    escape = False
    while not escape:
        iteration = iteration + 1
        currentCenteroids, currentCost = optimiseCentroidSelectionSpark(dataB, dataFrame, lastCenteroids, lastClusters, vectorMetric)
        currentCenteroids, currentClusters = optimiseClusterMembershipSpark(dataN, dataFrame, nRegions, pointMetric, currentCenteroids)
        print((currentCost<lastCost, currentCost, lastCost, currentCost - lastCost))
        if (currentCost<lastCost):
            print(("iteration",iteration,"cost improving...", currentCost, lastCost))
            lastCost = currentCost
            lastCenteroids = currentCenteroids
            lastClusters = currentClusters
        else:
            print(("iteration",iteration,"cost got worse or did not improve", currentCost, lastCost))
            escape = True
    bc = lastClusters.collect()
    unpackedClusters = [bc[i].cluster for i in range(len(bc))]
    return (lastCenteroids, unpackedClusters)



import pyspark
import numpy as np
from pyspark.sql import SparkSession

# connect to spark master
sc = pyspark.SparkContext(master="spark://10.0.0.3:6060")
spark = SparkSession(sc)

from pyclustering.cluster import cluster_visualizer
from pyclustering.utils import read_sample
from pyclustering.samples.definitions import FCPS_SAMPLES
from pyclustering.samples.definitions import SIMPLE_SAMPLES
sample = read_sample(FCPS_SAMPLES.SAMPLE_GOLF_BALL)
bestCentroids, bestClusters = fit(sc, sample, 9)

print (bestCentroids, bestClusters)
visualizer = cluster_visualizer()
visualizer.append_clusters(bestClusters, sample)
visualizer.show()