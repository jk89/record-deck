import pyspark
import json

with open("package.json") as fin:
    package_data = fin.read()
    package_data = json.loads(package_data)

spark_config = package_data["config"]["spark"]


sc = None
def get_spark_context():
    global sc
    if sc != None: return sc
    # connect to spark master
    sc = pyspark.SparkContext(master=spark_config["master"])

    for dep_file_path in spark_config["project_file_dependencies"]:
        sc.addFile(dep_file_path)
    return sc

print("sc context imported")