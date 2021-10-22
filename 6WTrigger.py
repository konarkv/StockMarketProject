import pandas as pd
import numpy as np
import argparse
import os

# This function gets all the row numbers when value in (i,val_col) is greater than value in (i,other_val_col)
# Used for both checking whether close is greater than open and whether volume is greater than volume average
def val_lt_otherVal(df, val_col, other_val_col):
    val_lt_other = []
    for i, row in df.loc[0:].iterrows():
        if (df.at[i,val_col] > df.at[i,other_val_col]):
            val_lt_other.append(i)
    return val_lt_other

# Returns all row numbers in which the low of that week is less than the lows of the previous n weeks
def low_lt_prevn(df, n=5):
    l_lt_prevn = []
    for i, row in df.loc[59:].iterrows():
        if (df.at[i,"Low"] < df.iloc[i-n:i]["Low"].min()):
            l_lt_prevn.append(i)
    return l_lt_prevn

# Creates a new dataframe from series from another one to get pertinent data
def df_given_rs(df, rows):
    series = []
    for i, row in df.loc[0:].iterrows():
        if i in rows:
            series.append(row)
    final_df = pd.DataFrame(series, columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Vol', 'VolAvg'])
    return final_df
    

def main(args=None):

    # adds argument specifying which file will be processed
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', required=True, type=argparse.FileType('r'),
        help="Name of stock data excel file to process")
    args = parser.parse_args(args)

    # get filename to process
    ifname = args.file.name
    
    # checks how file will be processed
    pd.options.display.float_format = '{:.5f}'.format
    if ifname.endswith(".xls") or ifname.endswith(".xlsx"):
      df = pd.read_excel(ifname)
    else:
      df = pd.read_csv(ifname)
    
    # makes three lists with row numbers satisfying close < open, low < prev 5 lows, and vol < volAvg
    condition1 = val_lt_otherVal(df, "Close", "Open")
    condition2 = low_lt_prevn(df)
    condition3 = val_lt_otherVal(df, "Vol", "VolAvg")
    
    # sorts the row numbers in ascending order then creates a dataframe with all the trigger weeks
    # delete condition3 and the preceding comma from the next line if you don't want volume average to be considered
    trigger_list = sorted(list(set.intersection(*map(set, [condition1, condition2, condition3]))))
    final_df = df_given_rs(df, trigger_list)

    # saves dataframe to a .csv file
    ofname = os.path.splitext(ifname)[0]+"_trigger_weeks.csv"
    final_df.to_csv(ofname)
    print ("Results written to", ofname)

    # calculates trigger ratio
    print("Total number of samples: " + str(len(df.index)))
    print("Number of triggers: " + str(len(trigger_list)))
    trigger_ratio = len(trigger_list)/len(df.index)
    print("Trigger ratio(with Volume Average condition): " + str(trigger_ratio))

    print()

    # checks whether close > open for t + 1
    cl_gt_op = 0
    for i in trigger_list:
        if (df.at[i+1,"Close"] > df.at[i+1,"Open"]):
            cl_gt_op += 1
    
    print("Close is greater than open for the week after " + str(cl_gt_op) + " out of " + str(len(trigger_list)) + " weeks, which is " + str(cl_gt_op*100/len(trigger_list)) + "% of the time.")
    
    print()
    # checks whether low of next 5 weeks violates trigger low
    low_vios = 0
    for i in trigger_list:
        if (df.at[i,"Low"] > df.iloc[i+5:i]["Low"].min()):
            low_vios+=1
    print("Low is violated in next 5 weeks " + str(low_vios) + " out of " + str(len(trigger_list)) + " weeks, which is " + str(low_vios*100/len(trigger_list)) + "% of the time.")
    
if __name__ == "__main__":
    main()


