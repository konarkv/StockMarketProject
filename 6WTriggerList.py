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
    parser.add_argument('-n', '--names-list', default=[], help="List of stock market codes to process")
    args = parser.parse_args(args)
    
    metric_list = []
    for name in args.names_list.split():
        # get filename to process
        ifname = name + "_WEEKLY.csv"
        
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
        # print("Total number of samples: " + str(len(df.index)))
        # print("Number of triggers: " + str(len(trigger_list)))
        trigger_ratio = len(trigger_list)*100/len(df.index)
        # print("Trigger ratio(with Volume Average condition): " + str(trigger_ratio))

        # print()

        # checks whether close > open for t + 1
        cl_gt_op = 0
        for i in trigger_list:
            if (df.at[i+1,"Close"] > df.at[i+1,"Open"]):
                cl_gt_op += 1
        
        # print("Close is greater than open for the week after " + str(cl_gt_op) + " out of " + str(len(trigger_list)) + " weeks, which is " + str(cl_gt_op*100/len(trigger_list)) + "% of the time.")
        
        print()
        # checks whether low of next 5 weeks violates trigger low
        low_vios_w1 = 0
        low_vios_w2 = 0
        low_vios_w3 = 0
        low_vios_w4 = 0
        for i in trigger_list:
            if (df.at[i,"Low"] > df.at[i+1,"Low"]):
                low_vios_w1+=1
            elif (df.at[i,"Low"] > df.at[i+2,"Low"]):
                low_vios_w2+=1
            elif (df.at[i,"Low"] > df.at[i+3,"Low"]):
                low_vios_w3+=1
            elif (df.at[i,"Low"] > df.at[i+4,"Low"]):
                low_vios_w4+=1
        if len(trigger_list) > 0:
            low_w1_perc = round(low_vios_w1*100/len(trigger_list), 4)
            low_w2_perc = round(low_vios_w2*100/len(trigger_list), 4)
            low_w3_perc = round(low_vios_w3*100/len(trigger_list), 4)
            low_w4_perc = round(low_vios_w4*100/len(trigger_list), 4)

        close_vios_w1 = 0
        close_vios_w2 = 0
        close_vios_w3 = 0
        close_vios_w4 = 0
        for i in trigger_list:
            if (df.at[i,"Close"] > df.at[i+1,"Close"]):
                close_vios_w1+=1
            elif (df.at[i,"Close"] > df.at[i+2,"Close"]):
                close_vios_w2+=1
            elif (df.at[i,"Close"] > df.at[i+3,"Close"]):
                close_vios_w3+=1
            elif (df.at[i,"Close"] > df.at[i+4,"Close"]):
                close_vios_w4+=1
        if len(trigger_list) > 0:
            close_w1_perc = round(close_vios_w1*100/len(trigger_list), 4)
            close_w2_perc = round(close_vios_w2*100/len(trigger_list), 4)
            close_w3_perc = round(close_vios_w3*100/len(trigger_list), 4)
            close_w4_perc = round(close_vios_w4*100/len(trigger_list), 4)


        # # checks for high violations
        # high_vios = 0
        # for i in trigger_list:
        #     if (df.at[i,"High"] > df.iloc[i-5:i]["High"].min()):
        #         high_vios+=1
        
        # # checks for close violation percentage
        # close_vios = 0
        # for i in trigger_list:
        #     if (df.at[i,"Close"] > df.iloc[i+5:i]["Close"].min()):
        #         close_vios+=1        
        if len(trigger_list) > 0:
            metric_list.append([name, trigger_ratio, cl_gt_op*100/len(trigger_list), low_w1_perc, low_w2_perc, low_w3_perc, low_w4_perc, close_w1_perc, close_w2_perc, close_w3_perc, close_w4_perc])
    metric_df = pd.DataFrame(metric_list, columns = ['Code', 'Trigger Ratio', 'Close > Open Percentage', 'Low Violation 1 week', 'Low Violation 2 week', 'Low Violation 3 week', 'Low Violation 4 week', 'Close Violation 1 week', 'Close Violation 2 week', 'Close Violation 3 week', 'Close Violation 4 week'])
    start = args.names_list.split()[0]
    end = args.names_list.split()[-1]
    save_name = start + "_to_" + end + "_metrics.csv"
    metric_df.to_csv(save_name)
if __name__ == "__main__":
    main()