
import pandas as pd
from pandas import DataFrame


def ingest(f=""):
    file_path = f
    data = DataFrame(pd.read_csv(file_path, header=0, encoding= "ISO-8859-1", sep=';'))    
    series = data.ISBN
    return series.to_list()