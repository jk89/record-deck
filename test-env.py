import traceback
try:
    import pandas
except:
    print("An import error occurred:")
    #traceback.print_exc()
    #print("------------------------------")
    print("This indicates that your python virtual environment is not established properly.")
    print("Please activate or install your virtual environment.")
    print("See the 'Install/activate frameworks and environment' section of ./GETTING-STARTED.md.")
