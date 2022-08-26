# (c) 2020 Jonathan Kelsey
# This code is licensed under MIT license
from pyspark.sql import functions as F
import pyspark
import numpy as np
import sys

def seed_kernel(data_broadcast, data_id_value, centeroids, k, metric):
    data = data_broadcast.value
    point = data_id_value[1]
    min_distance = sys.maxsize 
    for j in range(len(centeroids)): 
        distance = metric(point, data[centeroids[j]]) 
        min_distance = min(min_distance, distance)
    return min_distance

def seed_clusters(data_broadcast, data_frame, k, metric):
    data = data_broadcast.value
    centeroids = list(np.random.choice(data.shape[0], 1, replace=False))
    for i in range(k - 1):
        print("clusterSeed", i)
        distances = []
        mK = data_frame.rdd.map(lambda data_id_value: seed_kernel(data_broadcast, data_id_value, centeroids, k, metric))
        mK_collect = mK.collect()
        distances = np.array(mK_collect)
        next_centeroid = np.argmax(distances)
        centeroids.append(next_centeroid) 
    print("centeroids", centeroids)
    return centeroids 

def nearest_centeroid_kernel(data_id_value, centeroid_id_values, metric):
    _, data_value = data_id_value
    data_np = np.asarray(data_value)
    distances = []
    for _, centeroid_value in centeroid_id_values:
        centeroid_np = np.asarray(centeroid_value)
        distance = metric(data_np, centeroid_np)
        distances.append(distance)
    distances = np.asarray(distances)
    closest_centeroid = np.argmin(distances)
    return int(closest_centeroid)

def optimise_cluster_membership_spark(data, data_frame, n, metric, intital_cluster_indices=None):
    data_shape = data.shape
    data_rdd = data_frame.rdd
    data_length = data_shape[0]
    if intital_cluster_indices is None:
        index = np.random.choice(data_length, n, replace=False)
    else:
        index = intital_cluster_indices
    list_index = [int(i) for i in list(index)]
    centeroid_id_values = [(i,data[index[i]]) for i in range(len(index))]
    data_rdd = data_rdd.filter(lambda data_id_value: int(data_id_value["id"]) not in list_index)
    associated_cluster_points = data_rdd.map(lambda data_id_value: (data_id_value[0],nearest_centeroid_kernel(data_id_value, centeroid_id_values, metric)))
    clusters = associated_cluster_points.toDF(["id", "bestC"]).groupBy("bestC").agg(F.collect_list("id").alias("cluster"))
    return index, clusters

def cost_kernel(data_broadcast, test_centeroid, cluster_data, metric):
    data = data_broadcast.value
    cluster = np.asarray(cluster_data)
    cluster_length = cluster.shape[0]
    feature_length = data.shape[1]
    test_centeroid_column = np.zeros(shape=(cluster_length, feature_length), dtype=data.dtype)
    new_cluster_column = np.zeros(shape=(cluster_length, feature_length), dtype=data.dtype)
    for i in range(0, cluster_length):
        new_cluster_column[i] = data[cluster[i]]
        test_centeroid_column[i] = data[int(test_centeroid)] 
    pairwise_distance =  metric(new_cluster_column, test_centeroid_column)# (np.absolute(new_cluster_column-test_centeroid_column).sum(axis=1))# metric(new_cluster_column, test_centeroid_column)
    cost = np.sum(pairwise_distance)
    return float(cost) #new_cluster_column.shape[1]

def optimise_centroid_selection_spark(data_broadcast, data_frame, centeroids, clusters_frames, metric):
    data = data_broadcast.value
    new_centeroid_ids = []
    total_cost = 0
    for cluster_idx in range(len(centeroids)):
        old_centeroid = centeroids[cluster_idx]
        cluster_frame = clusters_frames.filter(clusters_frames.bestC == cluster_idx).select(F.explode(clusters_frames.cluster))
        cluster_data = cluster_frame.collect()
        if cluster_data:
            cluster_data = [cluster_data[i].col for i in range(len(cluster_data))]
        else:
            cluster_data = []
        cost_data = cluster_frame.rdd.map(lambda point_id: (point_id[0], cost_kernel(data_broadcast, point_id[0], cluster_data, metric)))
        cost = cost_data.map(lambda point_id_cost: point_id_cost[1]).sum()
        total_cost = total_cost + cost
        point_result = cost_data.sortBy(lambda point_id_cost: point_id_cost[1]).take(1)
        if (point_result):
            best_point = point_result[0][0]
        else:
            best_point = old_centeroid
        new_centeroid_ids.append(best_point)
    return (new_centeroid_ids, total_cost)


def validate_metric(metric):
    if (metric == "euclidean" or metric == "hamming"):
        return True
    if isinstance(metric, dict) == False:
        return "Metric is not a dictionary. And not a known string 'euclidean' or 'hamming'"
    metric_keys = metric.keys()
    if "point" not in metric_keys or "vector" not in metric_keys:
        return "Metric does not contain a member function for 'point' and/or 'point'."
    if callable(metric["point"]) == False or callable(metric["vector"]) == False:
        return "Metric.point and/or Metric.vector are not callable functions."
    if (metric["point"].__code__.co_argcount != 2 and metric["vector"].__code__.co_argcount != 2):
        return "Metric.point and/or Metric.vector do not both have 2 arguments."
    return True

# pre-defined metrics

#vector metrics
def hamming_vector(stack1, stack2):
    return (stack1 != stack2).sum(axis=1)
def euclidean_vector(stack1, stack2):
    #return (np.absolute(stack2-stack1)).sum(axis=1)
    return ((stack2-stack1)**2).sum(axis=1)

# point metrics
def hamming_point(p1, p2): 
    return np.sum((p1 != p2))
def euclidean_point(p1, p2): 
    return np.sum((p1 - p2)**2) 


def fit(sc, data, n_clusters = 2, metric = "euclidean", seeding = "heuristic"):
    metric_valid = validate_metric(metric)
    if metric_valid == True:
        if metric == "euclidean":
            point_metric = euclidean_point
            vector_metric = euclidean_vector
        elif metric == "hamming":
            point_metric = hamming_point
            vector_metric = hamming_vector
        else:
            point_metric = metric["point"]
            vector_metric = metric["vector"]
    else:
        print(metric_valid)
        return

    data_np = np.asarray(data)
    data_broadcast = sc.broadcast(data_np)
    seeds = None
    data_frame  = sc.parallelize(data).zipWithIndex().map(lambda xy: (xy[1],xy[0])).toDF(["id", "vector"]).cache()
    if (seeding == "heuristic"):
        seeds = list(seed_clusters(data_broadcast, data_frame, n_clusters, point_metric))
    last_centeroids, last_clusters = optimise_cluster_membership_spark(data_np, data_frame, n_clusters, point_metric, seeds)
    last_cost = float('inf')
    iteration = 0
    escape = False
    while not escape:
        iteration = iteration + 1
        current_centeroids, current_cost = optimise_centroid_selection_spark(data_broadcast, data_frame, last_centeroids, last_clusters, vector_metric)
        current_centeroids, current_clusters = optimise_cluster_membership_spark(data_np, data_frame, n_clusters, point_metric, current_centeroids)
        print((current_cost<last_cost, current_cost, last_cost, current_cost - last_cost))
        if (current_cost<last_cost):
            print(("iteration",iteration,"cost improving...", current_cost, last_cost, current_centeroids))
            last_cost = current_cost
            last_centeroids = current_centeroids
            last_clusters = current_clusters
        else:
            print(("iteration",iteration,"cost got worse or did not improve", current_cost, last_cost))
            escape = True
    bc = last_clusters.sort("bestC", ascending=True).collect()
    unpacked_clusters = [bc[i].cluster for i in range(len(bc))]
    return (last_centeroids, unpacked_clusters)