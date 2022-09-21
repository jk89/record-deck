import pyspark
from pyspark.conf import SparkConf
import json
import os
import socket
import netifaces as ni

with open("package.json") as fin:
    package_data = fin.read()
    package_data = json.loads(package_data)

spark_config = package_data["config"]["spark"]

sc = None
def get_spark_context():
    global sc
    if sc != None: return sc

    # get socket matches
    matches = [i[1] for i in socket.if_nameindex() if i[1]==spark_config["local-interface"]]
    if len(matches) != 1:
        raise "No interface called..." + spark_config["local-interface"]
    match = matches[0]
    ip = ni.ifaddresses(match)[ni.AF_INET][0]['addr']

    conf = SparkConf()
    conf.setMaster(spark_config["master"]).setAppName("Record-deck")
    conf.set("spark.executor.instances", "4")
    conf.set("spark.executor.cores", "4")
    # .set("spark.executor.instances", "4")
    #conf.get("spark.master")
    #conf.get("spark.app.name")
    #conf.set("spark.driver.host", "10.0.0.109")
    #conf.set("spark.driver.bindAddress", "10.0.0.109")

    os.environ["SPARK_LOCAL_IP"] = ip# "10.0.0.109"

    #print("conf.spark.app.name",conf.get("spark.app.name"))
    #print("spark.driver.host",conf.get("spark.driver.host"))
    #print("spark.driver.bindAddress",conf.get("spark.driver.bindAddress"))

    # connect to spark master
    sc = pyspark.SparkContext(conf=conf)

    for dep_file_path in spark_config["project_file_dependencies"]:
        sc.addFile(dep_file_path)
    return sc

print("sc context imported")