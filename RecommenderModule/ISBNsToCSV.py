
import pandas as pd
from pandas import DataFrame
from IngestISBN import ingest

file_path = ("RecommenderModule/dataset/BX_Books.csv")
data = DataFrame(pd.read_csv(file_path, header=0, encoding= "ISO-8859-1", sep=';'))
        
df_isbn = data.ISBN

df_isbn.to_csv("isbns.csv", index=False)

l = ingest("isbns.csv")