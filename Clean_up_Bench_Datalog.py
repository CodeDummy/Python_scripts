import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os , time
import glob
import pathlib
import re
list_of_files_raw_noext=[]
#list_of_files_raw = glob.glob('C:/Datafiles/AMC1300/*.txt') 
No_of_files_processed=0
No_of_files_skipped=0
#PATH_FOR_CLEAN_DATALOG= 'C:/Datafiles/AMC1300/Cleanedup/'
#PATH_FOR_RAW_DATALOG= 'C:/Datafiles/AMC1300/'

#Get list of files in datalog folder
list_of_files_raw = glob.glob('//Dtfr-ctpb1h43b/amc1300/*.txt')

#initialize paths
PATH_FOR_CLEAN_DATALOG= '//Dtfr-ctpb1h43b/amc1300/Cleanedup/'
PATH_FOR_RAW_DATALOG= '//Dtfr-ctpb1h43b/amc1300/'
##BASE_FILE_TIME = 1519948481.7437975


#//Dtfr-ctpb1h43b/amc1300
#AMC13XX (file://Dtfr-ctpb1h43b/amc13xx/)
#Cleanedup (file://Dtfr-ctpb1h43b/amc13xx/Cleanedup)
list_of_files_clean = glob.glob('//Dtfr-ctpb1h43b/amc1300/Cleanedup/*.csv') # * means all if need specific format then *.csv
latest_file = max(list_of_files_clean, key=os.path.getctime)
#print ('Latest clean file is ' + latest_file)
BASE_FILE_TIME = os.path.getmtime(latest_file)

for file in list_of_files_raw:
    
    re_search_bak = re.search('..bak', file) # search for .bak in filename
    file_noext =os.path.basename(file[:-4]) #remove .ext from file name
    list_of_files_raw_noext.append(file)
    path = pathlib.Path(PATH_FOR_CLEAN_DATALOG+file_noext+'.csv')
    
    
    re_search = re.search('..Temporary..', file_noext)
    
    if (path.is_file() == False and re_search==None and re_search_bak==None and os.path.getmtime(file)> BASE_FILE_TIME ):
        
        print("Processing file..."+os.path.basename(file))
        #print("last modified: %s" % time.ctime(os.path.getmtime(file)))
        #print("last modified: %s" % os.path.getmtime(file))
        #Read the file
        df = pd.read_csv(PATH_FOR_RAW_DATALOG+file_noext+'.txt',sep='\t',delimiter='\t')
        
        #set Meas_Name as the DF index
        #df=df.set_index('Device Descriptor')
        df['index_col'] = df.index
        #Rows to be removed (dropped), row 0 and 1
        df=df.drop([0,1])
      
         #columns to be removed (dropped)

        df=df.drop(['Sweep Version', 'Test Area','Package Type','Product Revision','Test_Parameter',
            'Block ID','Channel','Test Type','Station Name','SCM',
            'Upper Limit','Lower Limit','Nominal Value','End Time','Execution Duration (ms)',
            'Loop Count','Run Mode Name','UserID','Comment'],axis=1)
        #df = df.rename(columns={col: col.split('(')[0] for col in df.columns})
        
        
        type_row=[]    
        for column in df:
            #print(column)
            #print(df[column].unique())
            #print('Column index is',df.columns.get_loc(column))
            Column_idx=df.columns.get_loc(column)
            for unique_val in df[column].unique():
                if(pd.isnull(unique_val)==True):
                #print("this element is NaN")
                  pass
                else:
                    try:
                        float(unique_val)
                        isnumber= True
                        type_row.append(3.05) #just insert a real num in the first row so that spotfire detects it
                        #print(column ,'is a Number')
                        break 
                    except:
                        Isnumber = False   
                        type_row.append('STRING')
                        #print( column,'is a String')
                        break       
        
        try:
            #Make a data frame with df.columns as index and type_row as column
            df2 = pd.Series(type_row, index=[df.columns])
            #append df2 transposed to df, gets type_as the last row
            df2 = df.append(df2, ignore_index=True)
            #swap last row(type row ) and first row
            last_row, first_row = df2.iloc[-1].copy(), df2.iloc[0].copy()
            df2.iloc[-1],df2.iloc[0] = first_row,last_row
        
            df2.to_csv(PATH_FOR_CLEAN_DATALOG+file_noext+'.csv')
            
        except:
            print("Not a valid file "+file_noext+'.txt')