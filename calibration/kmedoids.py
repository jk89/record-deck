from pyspark.sql import functions as F
import numpy as np
import sys

def seed_clusters(data, k, metric): 
    centeroids = list(np.random.choice(data.shape[0], 1, replace=False)) 
    for _ in range(k - 1):
        distances = []
        for i in range(data.shape[0]): 
            point = data[i, :] 
            min_distance = sys.maxsize
            for j in range(len(centeroids)): 
                distance = metric(point, data[centeroids[j]]) 
                min_distance = min(min_distance, distance) 
            distances.append(min_distance) 
        distances = np.array(distances) 
        centeroids.append(np.argmax(distances)) 
        distances = [] 
    return centeroids

def nearest_centeroid(data_id_value, centeroid_id_values, metric):
    import numpy as np
    data_id, data_value = data_id_value
    data_np = np.asarray(data_value)
    distances = []
    for centeroid_id_value in centeroid_id_values:
        centeroid_id, centeroid_value = centeroid_id_value
        centeroid_np = np.asarray(centeroid_value)
        distance = metric(data_np, centeroid_np)
        distances.append(distance)
    distances = np.asarray(distances)
    closest_centeroid = np.argmin(distances)
    return int(closest_centeroid)

def optimise_cluster_membership_spark(data, data_frame, n, metric, intitalClusterIndices=None):
    dataShape = data.shape
    data_rdd = data_frame.rdd
    lengthOfData = dataShape[0]
    if intitalClusterIndices is None:
        index = np.random.choice(lengthOfData, n, replace=False)
    else:
        index = intitalClusterIndices
    listIndex = [int(i) for i in list(index)]
    centeroid_id_values = [(i,data[index[i]]) for i in range(len(index))]
    data_rdd = data_rdd.filter(lambda data_id_value: int(data_id_value["id"]) not in listIndex)
    associatedClusterPoints = data_rdd.map(lambda data_id_value: (data_id_value[0],nearest_centeroid(data_id_value, centeroid_id_values, metric)))
    clusters = associatedClusterPoints.toDF(["id", "bestC"]).groupBy("bestC").agg(F.collect_list("id").alias("cluster"))
    return index, clusters

def cost_kernel(data, test_centeroid, cluster_data, metric):
    cluster = np.asarray(cluster_data)
    len_cluster = cluster.shape[0]
    len_feature = data.shape[1]
    test_centeroid_column = np.zeros(shape=(len_cluster, len_feature), dtype=data.dtype)
    new_cluster_column = np.zeros(shape=(len_cluster, len_feature), dtype=data.dtype)
    for i in range(0, len_cluster):
        new_cluster_column[i] = data[cluster[i]]
        test_centeroid_column[i] = data[int(test_centeroid)] 
    pairwise_distance = metric(new_cluster_column, test_centeroid_column)
    cost = np.sum(pairwise_distance)
    return float(cost)

def optimise_centroid_selection_spark(data, data_frame, centeroids, clusters_frames, metric):
    data_rdd = data_frame.rdd
    dataShape = data.shape
    newcenteroid_ids = []
    total_cost = 0
    for cluster_idx in range(len(centeroids)):
        print("cluster_idx", cluster_idx)
        old_centeroid = centeroids[cluster_idx]
        cluster_frame = clusters_frames.filter(clusters_frames.bestC == cluster_idx).select(F.explode(clusters_frames.cluster))
        cluster_data = cluster_frame.collect()[0]
        cluster = np.asarray(cluster_data)
        cost_data = cluster_frame.rdd.map(lambda point_id: (point_id[0], cost_kernel(data, point_id[0], cluster_data, metric)))
        cost = cost_data.map(lambda point_id_cost: point_id_cost[1]).sum()
        total_cost = total_cost + cost
        best_point = cost_data.sortBy(lambda point_id_cost: point_id_cost[1]).take(1)[0][0]
        newcenteroid_ids.append(best_point)
    return (newcenteroid_ids, total_cost)

def cluster_opt(data, data_frame, n_regions, point_metric, vector_metric):
    # define a routine to keep going until cost stays the same or gets worse
    #get seeds
    seeds = seed_clusters(data, n_regions, point_metric)
    print(seeds)
    last_centeroids, last_clusters = optimise_cluster_membership_spark(data, data_frame, n_regions, vector_metric, seeds)
    last_cost = float('inf')
    iteration = 0
    escape = False
    while not escape:
        iteration = iteration + 1
        current_centeroids, current_cost = optimise_centroid_selection_spark(last_centeroids, last_clusters, data, data_frame, vector_metric)
        current_centeroids, current_clusters = optimise_cluster_membership_spark(data, data_frame, n_regions, vector_metric, current_centeroids)
        print((current_cost<last_cost, current_cost, last_cost, current_cost - last_cost))
        if (current_cost<last_cost):
            print(("iteration",iteration,"cost improving...", current_cost, last_cost))
            last_cost = current_cost
            last_centeroids = current_centeroids
            last_clusters = current_clusters
        else:
            print(("iteration",iteration,"cost got worse or did not improve", current_cost, last_cost))
            escape = True
        print("--------------------")
    return (last_centeroids, last_clusters)

#vector metrics
def hamming_vector(stack1, stack2):
    return (stack1 != stack2).sum() #.sum(axis=1)
def euclidean_vector(stack1, stack2):
    return (np.absolute(stack2-stack1)).sum() #.sum(axis=1)
# point metrics
def euclidean_point(p1, p2): 
    return np.sum((p1 - p2)**2) 
def hamming_point(p1, p2): 
    return np.sum((p1 != p2))

def fit(sc, data, n_regions = 2, metric = "euclidean", seeding = "heuristic"):
    if metric == "euclidean":
        point_metric = euclidean_point
        vector_metric = euclidean_vector
    elif metric == "hamming":
        point_metric = hamming_point
        vector_metric = hamming_vector
    else:
        print("unsuported metric")
        return

    data_n = np.asarray(data)
    seeds = None
    if (seeding == "heuristic"):
        seeds = seed_clusters(data_n, n_regions, point_metric)
    data_frame  = sc.parallelize(data).zipWithIndex().map(lambda xy: (xy[1],xy[0])).toDF(["id", "vector"])
    last_centeroids, last_clusters = optimise_cluster_membership_spark(data_n, data_frame, n_regions, vector_metric, seeds)
    last_cost = float('inf')
    iteration = 0
    escape = False
    while not escape:
        iteration = iteration + 1
        current_centeroids, current_cost = optimise_centroid_selection_spark(data_n, data_frame, last_centeroids, last_clusters, vector_metric)
        current_centeroids, current_clusters = optimise_cluster_membership_spark(data_n, data_frame, n_regions, vector_metric, current_centeroids)
        print((current_cost<last_cost, current_cost, last_cost, current_cost - last_cost))
        if (current_cost<last_cost):
            print(("iteration",iteration,"cost improving...", current_cost, last_cost))
            last_cost = current_cost
            last_centeroids = current_centeroids
            last_clusters = current_clusters
        else:
            print(("iteration",iteration,"cost got worse or did not improve", current_cost, last_cost))
            escape = True
    return (last_centeroids, last_clusters)