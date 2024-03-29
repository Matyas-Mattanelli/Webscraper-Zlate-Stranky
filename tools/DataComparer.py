import pandas as pd
import ast
import matplotlib.pyplot as plt

class DataComparer:
    """
    A class that compares data extracted from zlatestranky.cz and Google Places API, identifies which restaurants have been matched exactly and provides insight to information contained in Places data

    ...

    Attributes
    ----------
    df_ZS : pandas.DataFrame
        A data set generated by DatasetCompiler.py enriched with  the "exact_match" variable

    df_API : pandas.DataFrame
        A data set generated by GooglePlacesCompiler.py enriched with  the "exact_match" variable

    Methods
    -------
    compareDatasets(df_ZS, df_API)
        A function that identifes, whether an exact match in phone number between zlatestranky.cz and Places API was found. It adds the "exact_match" column into both datasets, whis equal to None in case no restaurant foundy by API, True in case of exact match, and False in not-exact match.
    
    summaryOfDatasets()
        A function that prints various statistics about Places API dataset

    plotReviews(outlier=5000)
        A function that prints histogram depicting number of reviews on restaurants retrieved from Places API. Parameter outlier can be set to chnage the range of the displayed data.

    plotRatings()
         A function that prints histogram depicting the values of ratings retrieved from Places API

    printRatingStatistics()
        A function that prints various information about ratings of restaurants retrieved from Places API

    showRows(no_of_rows=1)
        A function to show a specified number of rows from the top or from the bottom of the data set
    """

    def __init__(self, restaurants_zlatestranky, restaurants_Places_API):
        '''
        Creates an object of the class DataComparer and specifies its atributes

        Parameters
        ----------
        restaurants_zlatestranky : pandas.DataFrame
            Data set generated by DatasetCompiler      

        restaurants_Places_API : pandas.DataFrame
            Data set generated by GooglePlacesCompiler  
        '''
        self.df_ZS = self.compareDatasets(restaurants_zlatestranky, restaurants_Places_API)["df_ZS"]
        self.df_API = self.compareDatasets(restaurants_zlatestranky, restaurants_Places_API)["df_API"]

    def compareDatasets(self, df_ZS, df_API):
        '''
        A function that identifes, whether an exact match in phone number between zlatestranky.cz and Places API was found. It adds the "exact_match" column into both datasets, whis equal to None in case no restaurant foundy by API, True in case of exact match, and False in not-exact match.

        Parameters
        ----------
        df_ZS : pd.DataFrame
            Data set generated by DatasetCompiler

        df_API : pandas.DataFrame
            Data set generated by GooglePlacesCompiler  

        Returns
        -------
        dict_of_df : dict
            Dictionary containg both datasets, enriched by the "exact_match" variable
        '''
        #adding empty column to df_ZS
        empty_list = []
        for i in df_ZS.index:
            empty_list.append(None)
        df_ZS["exact_match"] = empty_list

        #comparison loop
        for i in df_ZS.index:
            if df_ZS["name"][i] == "Céleste":  #assigns None in case of this outiler
                celeste_exception = None
                df_ZS.exact_match.iat[i] = celeste_exception

            elif pd.isna(df_API["name"][i]):   #assigns None is case of no resaurant found by Google API
                df_ZS.exact_match.iat[i] = None
                
            else:                              #assigns true in case of match and False in case of no match
                zs_phones_dict = ast.literal_eval(df_ZS["phones"][i])
                
                zs_phones_list = []
                for n in zs_phones_dict:
                    net_number = zs_phones_dict[n][5:]
                    zs_phones_list.append(net_number)

                if df_API["formatted_phone_number"][i] in zs_phones_list:
                    df_ZS.exact_match.iat[i] = True
                else:
                    df_ZS.exact_match.iat[i] = False

        df_API["exact_match"] = df_ZS["exact_match"]   
        
        dict_of_df = {"df_ZS": df_ZS, "df_API": df_API}
        return dict_of_df


    def summaryOfDatasets(self):
        '''
        A function that prints various statistics about Places API dataset

        Parameters
        ----------

        Returns
        -------

        '''
        print("Total restaurants found on zlatestranky.cz:", self.df_ZS.name.count())
        print("Restaurants found by Google API search querry for the phone numbers from zlatestranky:", self.df_ZS.exact_match.count())
        print("Out of that, the number of exactly matched phone numbers:", self.df_ZS.exact_match.sum())
        print("This leaves us with", self.df_ZS.exact_match.count() - self.df_ZS.exact_match.sum(), "restaurants found by Google API, not matching to respective restaurants from zs., and", self.df_ZS.name.count() - self.df_ZS.exact_match.count(), "restaurants that could not be found at all based on the phone number from zs.")

    def plotReviews(self,outlier=5000):
        '''
        A function that prints histogram depicting number of reviews on restaurants retrieved from Places API. Parameter outlier can be set to chnage the range of the displayed data.

        Parameters
        ----------
        outlier : int
            Number specifying the value over which the number of reviews won't be considered. Defaults to 5000

        Returns
        -------

        '''
        if type(outlier) == int:
            df_API_exact_match = self.df_API[self.df_API["exact_match"] == True]
            df_API_outlier = df_API_exact_match[df_API_exact_match["user_ratings_total"] < outlier]
            df_API_hist = df_API_outlier["user_ratings_total"]
            plt.hist(df_API_hist,color='red', bins=12)
            plt.title('Number of ratings')
        else:
            raise ValueError('Invalid input. Please specify outlier as integer')

    def plotRatings(self):
        '''
        A function that prints histogram depicting the values of ratings retrieved from Places API

        Parameters
        ----------

        Returns
        -------

        '''
        plt.hist(self.df_API[self.df_API["exact_match"] == True]["rating"],color='green', bins=12)
        plt.title('Rating')

    def printRatingStatistics(self):
        '''
        A function that prints various information about ratings of restaurants retrieved from Places API

        Parameters
        ----------

        Returns
        -------

        '''
        #Number of restaurants with at least one review
        num_of_ratings = []
        for i in self.df_API[self.df_API["exact_match"] == True]["user_ratings_total"]:
            if (pd.isna(i) == False):
                num_of_ratings.append(True)
            else:
                num_of_ratings.append(False)

        print("Number of restaurants with at least one review:", num_of_ratings.count(True))

        #Highest number of reviews
        max_rev = self.df_API[self.df_API["exact_match"] == True]["user_ratings_total"].max()
        max_df = self.df_API[self.df_API["user_ratings_total"] == max_rev]
        max_name = max_df.iloc[0]["name"]
        max_address = max_df.iloc[0]["formatted_address"]

        print("Highest number of reviews:", max_rev, f"({max_name}, located at {max_address})")    

        #Mean average of available ratings
        mean_ratings = self.df_API[self.df_API["exact_match"] == True]["rating"].mean()

        print("Mean average of available ratings (rounded):", round(mean_ratings, 2))     

        #Lowest rating

        lowest_rating = self.df_API[self.df_API["exact_match"] == True]["rating"].min()
        df_exact_match = self.df_API[self.df_API["exact_match"] == True]
        num_of_lowest = df_exact_match[df_exact_match["rating"] == lowest_rating].count()["name"]
        lowest_name = df_exact_match[df_exact_match["rating"] == lowest_rating].iloc[0]["name"]
        lowest_address = df_exact_match[df_exact_match["rating"] == lowest_rating].iloc[0]["formatted_address"]
        if num_of_lowest == 1:
            print("Lowest rating:", lowest_rating, f"({lowest_name}, located at {lowest_address})")
        else:
            print("Lowest rating:", lowest_rating, f"({num_of_lowest} restaurants)")    

        #Highest rating

        highest_rating = self.df_API[self.df_API["exact_match"] == True]["rating"].max()
        df_exact_match = self.df_API[self.df_API["exact_match"] == True]
        num_of_highest = df_exact_match[df_exact_match["rating"] == highest_rating].count()["name"]
        highest_name = df_exact_match[df_exact_match["rating"] == highest_rating].iloc[0]["name"]
        highest_address = df_exact_match[df_exact_match["rating"] == highest_rating].iloc[0]["formatted_address"]
        if num_of_highest == 1:
            print("highest rating:", highest_rating, f"({highest_name}, located at {highest_address})")
        else:
            print("highest rating:", highest_rating, f"({num_of_highest} restaurants)")     


    def showRows(self,no_of_rows=1):
        """
        A function to show a specified number of rows from the top or from the bottom of the data set

        Parameters
        ----------
        no_of_rows : int or str
            An integer specifying the number of rows to return. Positive number shows rows from the top, negative from the bottom. Defaults to 1.
        
        Returns
        -------
        dataset : pandas.DataFrame
            A dataset with a specified number of rows
        """
        try:
            no_of_rows=int(no_of_rows)
        except:
            raise ValueError('Please specify the number of rows as an integer')
        if no_of_rows>=0:
            dataset=self.df_API.head(no_of_rows)
        else:
            dataset=self.df_API.tail(abs(no_of_rows))
        return dataset                                

