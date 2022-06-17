from CSVCreator import CSVCreator
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np


LENGTH = 481

class MultiVariateRegression:
    def __init__(self, metrics, file_name):
        self.metrics = metrics
        self.file_name = file_name


    def Results(self):
        CSVCreator(self.metrics, self.file_name).csv_export()

        df = pd.read_csv("Regression/csv/test.csv", header=None)
        df.head()

        df = pd.concat([pd.Series(1, index=df.index, name='00'), df], axis=1)
        df.head()
        # X = df.drop(columns=[1, 2, 3, 4, 5, 6], axis=1)
        # drop_c = [2]
        drop_c = [2, 3, 4, 6]
        alive_c = [0, 1, 5]
        X = df.drop(columns=drop_c, axis=1, labels=None)
        # X = df
        y = df.iloc[:, 7]
        X.head()
        for i in alive_c:
            X[i] = X[i] / np.max(X[i])
        X.head()
        theta = np.array([0] * len(X.columns), dtype=np.float)
        m = len(df)
        J, j, theta = self.gradientDescent(X, y, theta, 0.05, 10000)
        y_hat = self.hypothesis(theta, X)
        y_hat = np.sum(y_hat, axis=1)
        plt.figure()
        plt.scatter(x=list(range(0, LENGTH)), y=y, color='blue')
        plt.scatter(x=list(range(0, LENGTH)), y=y_hat, color='black')
        plt.show()
        plt.figure()
        plt.scatter(x=list(range(0, 10000)), y=J)
        plt.show()

    def hypothesis(self, theta, X):
        return theta * X

    def computeCost(self, X, y, theta):
        y1 = self.hypothesis(theta, X)
        y1 = np.sum(y1, axis=1)
        return sum(np.sqrt((y1 - y) ** 2)) / (2 * LENGTH)

    def gradientDescent(self, X, y, theta, alpha, i):
        J = []  # cost function in each iterations
        k = 0
        while k < i:
            y1 = self.hypothesis(theta, X)
            y1 = np.sum(y1, axis=1)
            for c in range(0, len(X.columns)):
                theta[c] = theta[c] - alpha * (sum((y1 - y) * X.iloc[:, c])/len(X))
            j = self.computeCost(X, y, theta)
            J.append(j)
            k += 1
        return J, j, theta

