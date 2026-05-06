import pandas as pd

class UserAccounts:
    def list_csv():
        Jar = pd.read_csv("UserAccounts.csv")
        print(Jar.head(2))

UserAccounts.list_csv()