import calibration.spark_context as spark_context
from pyspark.sql import SparkSession
import kmedoids2

# connect to spark master
sc = spark_context.get_spark_context()
spark = SparkSession(sc)

# if nessesary: pip install pyclustering 
from pyclustering.cluster import cluster_visualizer
from pyclustering.utils import read_sample
from pyclustering.samples.definitions import FCPS_SAMPLES
from pyclustering.samples.definitions import SIMPLE_SAMPLES

# use pyclustering datasets for a sanity check
sample = read_sample(FCPS_SAMPLES.SAMPLE_GOLF_BALL) #SAMPLE_ENGY_TIME
best_centroids, best_clusters = kmedoids2.fit(sc, sample, 8) # SAMPLE_GOLF_BALL 4 8 20 (good checks), SAMPLE_ENGY_TIME 20 fun
print(best_centroids)
visualizer = cluster_visualizer()
visualizer.append_clusters(best_clusters, sample)
visualizer.show()