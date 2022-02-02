import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import Counter
import re

class DataInterpreter:
    def __init__(self,dataset):
        self.dataset_raw=dataset
        self.dataset=self.removeEmptyObservations(self.dataset_raw)
        self.district_counts=self.getDistrictCounts(self.dataset)
        self.array_of_sums_of_opening_hours_spans=self.getArrayOfSumsOfOpeningHoursSpans(self.dataset)
        self.categorical_data_counts_dict=self.getCategoricalDataCounts(self.dataset)
        self.number_of_phones_counts=self.getNumberOfPhonesCounts(self.dataset)
        self.email_providers_counts=self.getEmailProvidersCounts(self.dataset)

    def removeEmptyObservations(self,df):
        indic=[column for column in df.columns if column not in ['name','ratings','review_count']] #Name, ratings, and review count always have a value (ratings and review count usually 0). But if a restaurant has only these three values (a review count is zero), it is of no use to us => we drop it
        for i in range(len(df)): #Check each observation
            if (sum(pd.isna(df.loc[i,indic]))==12) & (df.review_count[i]==0): #If values in all other columns are missing and there are no reviews, drop the observation
                df.drop(i,inplace=True)
            else:
                pass
        return df
    
    def getDistrictCounts(self,df):
        district_counts=df.district.value_counts() #Compute value counts
        district_counts.drop('Not found',inplace=True) #Do not include the 'Not found' values. In these cases, only street is provided in the address so we cannot easily extract the district
        return district_counts

    def plotDistrictCounts(self,plot_type='pie'):
        if plot_type=='pie':
            plt.figure(figsize=(7,7)) #Increase figure size for readability
            self.district_counts.plot.pie(labeldistance=None, autopct='%1.2f%%') #Make a pie chart with percentage values
            plt.title('Number of restaurants by districts') #Add a title
            plt.ylabel('') #Remove obsolete y label
            plt.legend() #Add a legend containg the districts
        elif plot_type=='bar':
            self.district_counts.plot.barh(color='orange').invert_yaxis()
            plt.title('Number of restaurants by districts')
        else:
            raise ValueError('Please specify the plot_type as "pie" or "bar"')

    def getArrayOfSumsOfOpeningHoursSpans(self,df):
        list_of_sums_of_opening_hours_spans=[]
        for dict in df.opening_hours_span: #For each observation extract the opening hours dictionary
            if pd.isna(dict): #If there is no dictionary, set value to NaN (we do not disregard it to keep the list length the same as in the data set)
                value=np.NaN
            else:
                value=sum(filter(None,list(dict.values()))) #we make a list from the dicts values, filter out the None values and sum it
            list_of_sums_of_opening_hours_spans.append(value)
        array_of_sums_of_opening_hours_spans=np.array(list_of_sums_of_opening_hours_spans) #Convert to a numpy array for easier handling
        array_of_sums_of_opening_hours_spans[array_of_sums_of_opening_hours_spans==0]=np.nan #If the sum is zero, the restaurant is either closed or the opening hours are not available => we replace it with NaN
        return array_of_sums_of_opening_hours_spans
    
    def interpretOpeningHoursDurations(self,plot_hist=True):
        print(f'Opening hours available for {sum([not i for i in pd.isna(self.dataset.opening_hours)])} out of {len(self.dataset)} restaurants')
        print(f'Maximum value: {max(self.array_of_sums_of_opening_hours_spans)} ({np.sum(self.array_of_sums_of_opening_hours_spans==max(self.array_of_sums_of_opening_hours_spans))} restaurants)')
        print(f'Minimum value: {min(self.array_of_sums_of_opening_hours_spans)} ({self.dataset.name[self.array_of_sums_of_opening_hours_spans==min(self.array_of_sums_of_opening_hours_spans)].values[0]} restaurant)')
        print(f'Mean: {np.around(np.mean(self.array_of_sums_of_opening_hours_spans,where=[not i for i in np.isnan(self.array_of_sums_of_opening_hours_spans)]),2)}') #Computing the mean while excluding the NaN values
        print(f'Median: {np.around(np.median(self.array_of_sums_of_opening_hours_spans[[not i for i in np.isnan(self.array_of_sums_of_opening_hours_spans)]]),2)}')
        if plot_hist:
            plt.hist(self.array_of_sums_of_opening_hours_spans)
            plt.title('Histogram of weekly opening hours durations')

    def interpretReviewsAndRatings(self,plot_hist=True):
        print(f'Number of restaurants with at least one review: {sum(self.dataset.review_count!=0)}')
        print(f'Highest number of reviews: {max(self.dataset.review_count)} ({np.sum(self.dataset.review_count==max(self.dataset.review_count))} restaurants)')
        available_ratings=self.dataset.ratings[self.dataset.review_count!=0] #Filtering out ratings with zero reviews
        print(f'Mean average of available ratings: {np.around(np.mean(available_ratings),2)} out of 100')
        print(f'Lowest rating: {min(available_ratings)} ({np.sum(self.dataset.ratings==min(available_ratings))} restaurants)')
        print(f'Highest rating: {max(available_ratings)} ({np.sum(self.dataset.ratings==max(available_ratings))} restaurants)')
        if plot_hist:
            plt.hist(available_ratings,color='red')
            plt.title('Histogram of ratings')

    def getCategoricalDataCounts(self,dataset):
        categorical_data_dict={} #Creating a dictionary with 'payment_methods','products', 'services', and 'marks' as keys and with list containing respective values from each column as values
        for column in ['payment_methods', 'products', 'services', 'marks']: #Take each column
            demo_list=[] #Create a demo list to temporarily store the values
            for value in dataset[column]: #For each observation
                if type(value)==type([]): #If it is a list, we need to unpack it
                    demo_list.extend(value)
                elif pd.isna(value): #If it is a nan, we do not need it
                    pass
                else:
                    demo_list.append(value) #If it is a string, we append it
            demo_list_lowercase=[value.lower() for value in demo_list] #Convert the values to lowercase to avoid duplicates
            categorical_data_dict[column]=demo_list_lowercase #Put the values into the prepared dictionary
        categorical_data_counts_dict={key:Counter(value) for key, value in categorical_data_dict.items()} #Computing value counts for each category
        categorical_data_counts_dict_sorted={} #Creating a new dictionary with values sorted from highest to lowest
        for column in categorical_data_counts_dict:
            values_sorted=sorted(categorical_data_counts_dict[column].items(),key=lambda x:x[1]) #Sorting the values in the dictionary (returns a list of tuples)
            categorical_data_counts_dict_sorted[column]={key:value for key, value in values_sorted} #Creating a new dictionary from the list of tuples (key and value)
        return categorical_data_counts_dict_sorted

    def interpretCategoricalDataCounts(self,categories=['payment_methods', 'products', 'services', 'marks'],threshold=10):
        if type(categories)==type(''): #If category is a single string, convert it to a list fro easier handling
            categories=[categories]
        try: #Make sure that threshold is numeric
            threshold=float(threshold)
        except:
            raise ValueError('Please specify a numeric threshold')
        for category in categories:
            if category in ['payment_methods', 'products', 'services', 'marks']: #Check that the input is valid
                dict_of_counts={key:value for key, value in self.categorical_data_counts_dict[category].items() if value>=threshold} #Filter out values based on the threshold
                plt.figure(figsize=(7,7)) #Make sure each plot is in a different window and also that it is big enough
                plt.barh(list(dict_of_counts.keys()),dict_of_counts.values(),color='darkgreen')
                plt.title(category.replace('_',' ').capitalize()) #Make a tidy title
            else:
                print(f'{category} is not a valid input. Please specify one or more options from the following list: ["payment_methods", "products", "services", "marks"]')

    def getNumberOfPhonesCounts(self,dataset):
        number_of_phones=[]
        for phones_dict in dataset['phones']:
            number_of_phones.append(len(phones_dict))
        number_of_phones_counts=Counter(number_of_phones)
        return number_of_phones_counts
    
    def plotNumberOfPhonesCounts(self,plot_type='bar'):
        if plot_type=='bar':
            plt.barh(list([str(key) for key in self.number_of_phones_counts.keys()]),self.number_of_phones_counts.values(),color='pink')
            plt.gca().invert_yaxis() #To sort it from highest to lowest
            plt.title('Number of phones available by restaurant')
        elif plot_type=='pie':
            plt.figure(figsize=(7,7))
            plt.pie(self.number_of_phones_counts.values(),labels=self.number_of_phones_counts.keys(),labeldistance=None, autopct='%1.2f%%')
            plt.legend()
            plt.title('Number of phones available by restaurant')
        else:
            raise ValueError('Please specify the plot_type as "bar" or "pie"')

    def getEmailProvidersCounts(self,dataset):
        email_providers=[]
        for email in dataset.email_address:
            if pd.isna(email): #If the email is missing, pass
                pass
            else:
                try: #Try to find the domain
                    value=re.search('@.*\.',email).group(0)
                    provider=value[1:len(value)-1] #Return only the domain without at and dot
                    email_providers.append(provider)
                except ValueError: #If there is no domain, pass
                    pass
        email_providers_counts=Counter(email_providers) #Get counts
        email_providers_counts['Own domain']=list(email_providers_counts.values()).count(1) #If there is only one occurence of a domain, we assume it is restaurant's own domain
        values_sorted=sorted(email_providers_counts.items(),key=lambda x:x[1]) #Sorting the values in the dictionary (returns a list of tuples)
        email_providers_counts_sorted={key:value for key, value in values_sorted}
        return email_providers_counts_sorted

    def plotEmailProvidersCounts(self,threshold=10,plot_type='bar'):
        try: #Make sure that threshold is numeric
            threshold=float(threshold)
        except:
            raise ValueError('Please specify a numeric threshold')
        dict_of_counts={key:value for key, value in self.email_providers_counts.items() if value>=threshold} #Filter out values based on the threshold
        if plot_type=='bar':
            plt.barh(list(dict_of_counts.keys()),dict_of_counts.values(),color='brown')
            plt.title('Email providers')
        elif plot_type=='pie':
            plt.figure(figsize=(7,7))
            plt.pie(dict_of_counts.values(),labels=dict_of_counts.keys(),labeldistance=None, autopct='%1.2f%%')
            plt.legend()
        else:
            raise ValueError('Please specify the plot_type as "bar" or "pie"')


