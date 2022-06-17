import pandas as pd


class CSVCreator:
    def __init__(self, list_of_columns, name):
        self.list_of_columns = list_of_columns
        self.name = name

    def csv_export(self):
        csv_dict = {}
        for i in range(len(self.list_of_columns)):
            csv_dict[self.list_of_columns[i][0]] = self.list_of_columns[i][1]
        df = pd.DataFrame(csv_dict)
        df.to_csv("Regression/csv/" + self.name + ".csv", index=False, header=None)
