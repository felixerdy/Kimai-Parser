import os
import argparse
import pandas as pd

parser = argparse.ArgumentParser(
    description='Process CSV data by project and month')
parser.add_argument('filepath', type=str, help='path to the CSV file')
parser.add_argument('projects', type=str, nargs='+',
                    help='list of projects to process')
parser.add_argument('-o', '--output', type=str,
                    default='.', help='output directory')
args = parser.parse_args()

df = pd.read_csv(args.filepath)

# remove unused columns
df = df.drop(columns=["From", "To", "Price", "rate_internal", "User", "Name", "Description", "Exported",
             "Billable", "Tags", "Hourly price", "Fixed price", "Type", "Category", "Account", "VAT-ID", "Order number"])

# convert the 'Date' column to datetime type
df['Date'] = pd.to_datetime(df['Date'])

# create a new DataFrame with all the unique dates in the original DataFrame
all_dates = pd.date_range(start=df['Date'].min(), end=df['Date'].max())

# create a list of dataframes, one for each project
project_dfs = []
for project in args.projects:
    project_df = df[df['Project'] == project]
    daily_project_hours = project_df.groupby(['Date'])['Duration'].sum() / 3600
    # merge with the all_dates DataFrame and fill missing values with 0
    daily_project_hours = pd.merge(daily_project_hours, pd.DataFrame(
        index=all_dates), left_index=True, right_index=True, how='right')
    daily_project_hours = daily_project_hours.fillna(0)
    project_dfs.append(daily_project_hours)

# merge the dataframes on date
daily_merged = pd.concat(project_dfs, axis=1)
daily_merged.columns = [f"{project} Hours" for project in args.projects]


# add a column for the non-project working hours
daily_merged['Other Hours'] = df.groupby(
    ['Date'])['Duration'].sum() / 3600 - daily_merged.sum(axis=1)

# add a column for the total working hours for each day
daily_merged['Total Hours'] = daily_merged.sum(axis=1)

# merge with the all_dates DataFrame and fill missing values with 0
daily_merged = pd.merge(daily_merged, pd.DataFrame(
    index=all_dates), left_index=True, right_index=True, how='right')
daily_merged = daily_merged.fillna(0)

for month, data in daily_merged.groupby(pd.Grouper(freq='M')):
    # create a directory with the name of the month
    directory_name = month.strftime('%b-%Y')
    os.makedirs(os.path.join(args.output, directory_name), exist_ok=True)

    # loop through each project and create a separate CSV file
    for project in args.projects:
        # select only the data for the current project
        project_data = data[[f"{project} Hours", "Other Hours", "Total Hours"]]

        # calculate the other hours for the current project
        other_hours = project_data["Other Hours"] + \
            data[[f"{p} Hours" for p in args.projects if p != project]].sum(
                axis=1)

        # add the other hours to the project data
        project_data["Other Hours"] = other_hours

        # create a CSV file with the name of the project and month
        filename = os.path.join(
            args.output, directory_name, f"{project} - {month.strftime('%b-%Y')}.csv")
        project_data.to_csv(filename, index=True,
                            header=True, decimal=",", sep=";")
        filename = os.path.join(
            args.output, directory_name, f"{project} - {month.strftime('%b-%Y')}.xlsx")
        project_data.T.to_excel(filename)
