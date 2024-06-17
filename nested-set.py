import warnings
import time
import pandas as pd
import numpy as np

from enum import Enum

print('Booting up...\n')

# start timer
start = time.time()

# define headers
class Headers(Enum):
    # must have
    EMPLOYEE_ID = 'Emp34Id'
    # must have
    EMPLOYEE_LAST_NAME = 'EmpLastName'
    # must have 
    EMPLOYEE_FIRST_NAME = 'EmpFirstName' 
    EMPLOYEE_EMAIL = 'EmpEmailAddress' 
    EMPLOYEE_POSITION_DESCRIPTION = 'EmpPositionDesc'
    EMPLOYEE_LOCATION_CODE = 'EmpLocationCode'
    EMPLOYEE_LOCATION_DESCRIPTION = 'EmpLocationDesc'
    # must have
    MANAGER_ID = 'Mgr34Id'
    # must have
    MANAGER_NAME = 'MgrName'
    MANAGE_TITLE = 'MgrTitle'
    MANAGER_EMAIL = 'MgrEmailAddress'
    EMPLOYEE_ANNIVERSARY = 'EmpAnnivDate'
    # must have
    EMPLOYEE_IS_SUPER = 'EmpPositionIsSuper'
    # will be set
    TIER = 'Tier'
    # will be set
    LEFT = 'Left'
    # will be set
    RIGHT = 'Right'

# suppress dataframe warnings
warnings.filterwarnings("ignore")

# define csv path
# csv_path = 'orgchart_faux.csv'
csv_path = input("What is the name of the file you're trying to analyze? (Include the file extension.)\n")
output_dir = input('What would you like to call the output file? (Do not include the file extension.)\n')

# read in dataset, optionally test
df = pd.read_csv(csv_path)
# print(df.head())

# drop unnecessary columns
unnecessary_columns = [
    Headers.EMPLOYEE_EMAIL.value,
    Headers.EMPLOYEE_POSITION_DESCRIPTION.value,
    Headers.EMPLOYEE_LOCATION_CODE.value,
    Headers.EMPLOYEE_LOCATION_DESCRIPTION.value,
    Headers.EMPLOYEE_ANNIVERSARY.value,
    Headers.MANAGE_TITLE.value,
    Headers.MANAGER_EMAIL.value
]

df = df.drop(unnecessary_columns, axis=1)

# optionally print column headers to console
# keys = df.keys()
# print(keys)

# determine top of hierarchy, optionally test
ceo = df[df[Headers.MANAGER_ID.value].isna()]
# print(ceo)

# check if there is only one CEO in the dataset, otherwise quit
ceo_id_raw = ceo[Headers.EMPLOYEE_ID.value]
if len(ceo_id_raw) != 1:
    raise ValueError('More than one CEO in dataset.')

# get the CEO ID
ceo_id = ceo_id_raw.values[0]
print(f'\nTop employee ID: {ceo_id}\n')

# initialize dataframe that will be used to set each employee's "tier", or steps down from the CEO
# e.g., given that the CEO is tier 1, the highest tier, an employee with tier 3 is 2 steps down from the CEO
tiered_df = pd.DataFrame()

# initialize variables used for the following loop
# how many employees are in each tier
number_of_employees_in_tier = 1
# the ids of employees in each tier
employee_ids_in_tier = ceo_id_raw
# tier counter used by loop
tier_iterator = 1
# set the tier of the first employee
ceo.loc[:, Headers.TIER.value] = tier_iterator
# add the first employee to the new dataframe
tiered_df = pd.concat([tiered_df, ceo])
# optional tracker for tier boundaries
# tier_boundaries = [(0,0)]

print('Setting employee tiers...')

while number_of_employees_in_tier < len(df):
    # get a dataframe of all the employees in a tier
    temporary_df = df[df[Headers.MANAGER_ID.value].isin(employee_ids_in_tier)]

    # if the dataframe is empty, there are no more employees to iterate through
    if len(temporary_df) == 0:
        break

    # set the tier
    tier_iterator += 1

    # optionally set the tier boundaries
    # tier_boundaries.append((number_of_employees, number_of_employees + len(tempDf) - 1))

    # extrat the employee ids from the dataframe
    employee_ids_in_tier = temporary_df[Headers.EMPLOYEE_ID.value]

    # set the employee's tier level in the temporary dataframe
    temporary_df.loc[:, Headers.TIER.value] = tier_iterator

    # add the temporary dataframe to the new dataframe
    tiered_df = pd.concat([tiered_df, temporary_df])

    # increment the number of employees
    number_of_employees_in_tier += len(temporary_df)

    print(f'On tier {tier_iterator - 1}, {len(temporary_df)} employees were added. There are now {len(tiered_df)} employees.')

# optionally test loop output to ensure each employee has a tier
# print(len(df), len(tiered_df), len(df) == len(tiered_df))
# print(tiered_df.head())

# sort the dataframe by tier, manager id, and employee first name
sorted_df = tiered_df.sort_values([Headers.TIER.value, Headers.MANAGER_ID.value, Headers.EMPLOYEE_FIRST_NAME.value], ascending=True).reset_index()
# optionally test that df was sorted properly
# print(sortedDf.head(70))

# my dataframe has a flag for managers, but it's not completely accurate
# find managers based on flag
managers = sorted_df[sorted_df[Headers.EMPLOYEE_IS_SUPER.value] == "Y"]
# get manager ids based on flag
manager_ids = managers[Headers.EMPLOYEE_ID.value].values
# sort managers alphabetically
manager_ids.sort(axis = 0)
# optionally test that managers were added
# print(managerIds[0:10])

print(f'\nNumber of managers: {len(manager_ids)}\n')

# create dictionaries to store list of direct reports and number of direct reports
# two separate dictionaries to reduce nesting complexity
direct_reports_dict = {}
number_of_direct_reports_dict = {}

# sort the dataframe by manager id to speed up the direct report loop below
new_sorted_df = df.sort_values(Headers.MANAGER_ID.value, ascending=True).reset_index()
# initialize current manager
current_manager = new_sorted_df.loc[0, Headers.MANAGER_ID.value]
# cast as string
current_manager = str(current_manager)
# set the first direct report list
direct_reports_dict[current_manager] = [new_sorted_df.loc[0, Headers.EMPLOYEE_ID.value]]
# set the first direct report count
number_of_direct_reports_dict[current_manager] = 1
# initialize iteration counter
direct_report_iterator = 1
# set upper bound for loop
upper_bound = len(new_sorted_df)

print('Counting direct reports...\n')

for i in range(1, upper_bound):
    # get next employee's manager id
    next_manager = new_sorted_df.loc[i, Headers.MANAGER_ID.value]
    # cast as string
    next_manager = str(next_manager)

    # if the next employee's manager is the same as the last employer's manager...
    if next_manager == current_manager:
        # add the employee to the current manager's direct report list
        direct_reports_dict[current_manager].append(new_sorted_df.loc[i, Headers.EMPLOYEE_ID.value])
        # increment the current manager's direct report count
        number_of_direct_reports_dict[current_manager] += 1
    else:
        # otherwise, set the current manager to the next manager
        current_manager = next_manager
        # add the new manager to the direct reports dictionary and initialize direct report list
        direct_reports_dict[current_manager] = [new_sorted_df.loc[i, Headers.EMPLOYEE_ID.value]]
        # set the new manager's direct report count to 1
        number_of_direct_reports_dict[current_manager] = 1
    
    # optionally show iteration count to keep user informed
    if direct_report_iterator % 10000 == 0:
        print(f'Finished {direct_report_iterator} rows...')

    # increment the iteration counter
    direct_report_iterator += 1

# optimize memory
del(new_sorted_df)
del(df)

print('\nAdding managers with no direct reports...\n')

# compare the list of employees flagged as managers to the list of employees that are actually managers as found in the dataframe
# initialize the iteration counter
manager_iterator = 0

for i in manager_ids:
    # if the manager id is not in the direct reports dictionary, add it with an empty list
    if i not in direct_reports_dict.keys():
        direct_reports_dict[i] = []
        number_of_direct_reports_dict[i] = 0
    
    # increment the iteration counter
    manager_iterator += 1

    # optionally show iteration count to keep user informed
    if manager_iterator % 500 == 0:
        print(f'Finished {manager_iterator} managers...')

# optimize memory
del(manager_ids)

# optionally test that the direct reports dictionary and number of direct reports dictionary are the same length
print()
print(len(direct_reports_dict), len(number_of_direct_reports_dict), len(direct_reports_dict) == len(number_of_direct_reports_dict))

if len(direct_reports_dict) != len(number_of_direct_reports_dict):
    raise ValueError("Dictionaries have different number of keys.")

# optionally test that a random manager has the same number of direct reports and direct reports list length
# print('\nFinding first manager to test with...\n')
# first_manager_index = -1
# for i in direct_reports_dict.keys():
#     if number_of_direct_reports_dict[i] > 0:
#         first_manager_index = np.where(manager_ids == i)[0][0]
#         break

# print(direct_reports_dict[manager_ids[first_manager_index]])
# print(number_of_direct_reports_dict[manager_ids[first_manager_index]])

# optionally test that the dictionaries were correctly populated by testing the CEO's direct reports
print('\nPrinting CEO direct reports...\n')
print(direct_reports_dict[str(ceo_id)], number_of_direct_reports_dict[str(ceo_id)], len(direct_reports_dict[str(ceo_id)]) == number_of_direct_reports_dict[str(ceo_id)])

if len(direct_reports_dict[str(ceo_id)]) != number_of_direct_reports_dict[str(ceo_id)]:
    raise ValueError("Dictionaries have inconsistent values.")

# optionally test that the dictionaries were correctly populated, 
# making sure the number of employees in the dictionaries is the same as the length of the dataframe
print('\nHow many employees accounted for as direct reports?\n')

# initialize total sum
sum = 0

for i in number_of_direct_reports_dict.keys():
    # add number of direct reports to total sum
    sum += number_of_direct_reports_dict[i]

print(sum)

if sum != len(sorted_df):
    raise ValueError("Number of direct reports does not equal number of employees.")

# optionally show the first 10 items of each dictionary
# print(dict(list(directReportsDict.items())[:10]))
# print(dict(list(number_of_direct_reports_dict.items())[:10]))

# function to set the left and right values for each employee
def set_count(left: bool = False, right: bool = False, employee: int = -1, count: int = -1) -> int:
    # test that all arguments were provided
    if count == -1 or employee == -1 or (not left and not right):
        raise ValueError('set_count function was called incorrectly.')
    
    # set the left value
    if left:
        sorted_df.loc[employee, Headers.LEFT.value] = count

    # set the right value
    elif right:
        sorted_df.loc[employee, Headers.RIGHT.value] = count

    # increment the count
    count += 1

    return count

# initialize history list, which will be used as a hierarchy tracker for the algorithm
history = []

# recursive function to set the left and right values for each employee (only works for datasets with less than 500 rows)
def nested_set_algorithm_recursive(emp_id: str, count: int, tier: int, emp_colleagues: int, going_up: bool = False, mgr_id: str = '', mgr_colleagues: int = 0) -> None:
    # optionally show args
    print(f"\n{emp_id = }, {count = }, {tier = }, {emp_colleagues = }, {going_up = }, {mgr_id = }, {mgr_colleagues = }")

    # optionally inform the user
    if count % 100 == 0:
        print('Done 100 iterations...')

    # figure out who the current employee is
    employee = sorted_df[sorted_df[Headers.EMPLOYEE_ID.value] == emp_id]

    # check if the employee was found, and employee is unique
    if len(employee) != 1:
        raise ValueError('Employee not found in dataset.')
    
    # figure out current employee's index
    employee_index = employee.index

    # check if the current employee's tier is correct
    employee_tier = sorted_df.loc[employee_index, Headers.TIER.value]
    # if not, the function is not working properly
    if employee_tier.values[0] != tier:
        print(employee_tier.values[0], tier)
        raise ValueError('Not moving up or down hierarchy properly.')
    
    
    # if the current employee has been done before, set the right value
    if going_up:
        count = set_count(right = True, employee = employee_index, count = count)
    # otherwise, set the left value
    else:
        count = set_count(left = True, employee = employee_index, count = count) 

    # function has small bug where it will increment value more than once...probably fencepost error with logic below

    # check if the current employee has a manager 
    if mgr_id == '':
        # first, double_check that the mgr value should be blank
        # when the function is called with going_up = True, mgr_id will always be blank, so it will need to be set
        # this is because we don't keep track of an employee's manager's manager
        mgr_id = sorted_df.loc[employee_index, Headers.MANAGER_ID.value].values[0]

        # if the employee does have a manager id, how many colleagues do they have?
        if emp_id != str(ceo_id) and mgr_id != str(ceo_id):
            # optionally show that the employee's manager needed to be populated
            print('Populating manager...')
            # find the manager
            manager = sorted_df[sorted_df[Headers.EMPLOYEE_ID.value] == mgr_id]
            # get the manager's index
            manager_index = manager.index
            # get the manager's manager's id
            managers_mgr_id = sorted_df.loc[manager_index, Headers.MANAGER_ID.value]
            # set the number of colleagues the manager's manager has
            mgr_colleagues = int(number_of_direct_reports_dict.get(managers_mgr_id.values[0])) - 1

        # if the employee does not have a manager, then the employee is the CEO, and end the recursive loop
        elif int(sorted_df.loc[employee_index, Headers.RIGHT.value].values[0]) != 0 and emp_id == str(ceo_id):
            # set the right value
            count = set_count(right = True, employee = employee_index, count = count)
            # optionally print the final count
            print('\nDone!')
            print('Final count:', count)
            print(count - 1)
            return
                
    # optionally show the current employee of interest
    print(f"Employee Name: {employee[Headers.EMPLOYEE_FIRST_NAME.value].values[0] + ' ' + employee[Headers.EMPLOYEE_LAST_NAME.value].values[0]}, Manager Name: {employee[Headers.MANAGER_NAME.value].values[0]}, Left: {count}")

    # get the current employee's direct reports and number of direct reports
    directReports : list = direct_reports_dict.get(emp_id)
    numberOfDirectReports : int = number_of_direct_reports_dict.get(emp_id)
    # optionally show the number of direct reports
    print(f'Employee has {numberOfDirectReports} direct reports.')
    
    # if the current employee has direct reports, the number of direct reports is more than 0, and we're not currently moving up the hierarchy, go down the chain once
    if numberOfDirectReports and directReports and numberOfDirectReports > 0 and len(directReports) > 0 and not going_up:
        # update history tracker
        history.append(emp_id)

        # optionally show the tier we're moving down to
        print(f'Going down to tier {tier + 1}...')
        # the next employee (the current employee's first direct report) will need to have...
        nested_set_algorithm_recursive(directReports[0], count, tier + 1, len(directReports) - 1, False, emp_id, emp_colleagues)

    # if the current employee has no direct reports but has colleagues, go right once
    # condition may be slightly redundant
    elif (going_up and emp_colleagues > 0) or (not going_up and emp_colleagues > 0):

        # if the current employee is in the manager dictionaries, remove them
        # this is how we keep track of who has been counted and who hasn't
        if emp_id in direct_reports_dict.keys() and emp_id in number_of_direct_reports_dict.keys():
            direct_reports_dict.pop(emp_id)
            number_of_direct_reports_dict.pop(emp_id)

        # determine who the employee's colleague is by looking at their manager's direct reports
        colleagues : list = direct_reports_dict.get(mgr_id)
        # pop the current employee off their manager's direct report list
        # this is how we keep track of who has been counted and who hasn't
        if colleagues:
            colleagues.remove(emp_id)
        # if there were no colleagues returned, then there's a problem with the function
        else:
            raise ValueError('Employee has no colleagues.')
        
        # set the current employee's manager's direct report list to the new list
        direct_reports_dict[mgr_id] = colleagues
        # set the current employee's manager's number of direct reports to the new list length
        number_of_direct_reports_dict[mgr_id] = len(colleagues)
        
        # set the right count
        count = set_count(right = True, employee = employee_index, count = count)

        # optionally show that we're moving right
        print(f'Going right because employee has {len(colleagues) - 1} colleagues...')
        # the next employee (the current employee's first colleague) will need to have...
        nested_set_algorithm_recursive(colleagues[0], count, tier, len(colleagues) - 1, False, mgr_id, mgr_colleagues)

    # if the current employee has no direct reports and no colleagues, go up the chain once
    else:
        # set the right count
        count = set_count(right = True, employee = employee_index, count = count)

        # if the employee has a manager, update the hierarchy tracker
        if len(history) > 0:
            history.pop()

        # if the hierarchy tracker is already empty, then the algorithm is complete
        else:
            print('\nDone!')
            print(f'Ended at: {count}')
            return

        # optionally show that we're moving up
        print(f"Going up to tier {tier - 1}...")
        # the next employee (the current employee's manager) will need to have...
        nested_set_algorithm_recursive(mgr_id, count, tier - 1, mgr_colleagues, True)

    # if the function makes it down here, then either the recursive loop is over, or there's a problem
    return

# iterative function to set the left and right values for each employee
# python isn't very good at recursive problems, so for large datasets, we need to use loops
# for the most part, the process is the same as the recursive function, as is the documentation
# refer to comments above
def nested_set_algorithm_iterative(emp_id: str, ceo_id: str) -> None:
    # initialize the stack with the CEO
    # 'stack' is a list of tuples, and each tuple has the same arguments as the recursive function above
    # emp_id, count, tier, emp_colleagues, going_up, mgr_id, mgr_colleagues
    stack = [(emp_id, 1, 1, 0, False, '', 0)]
    # initialize history tracker
    history = []
    # initialize iteration counter
    count = 1
    
    while stack:
        # pop the last tuple off the stack
        emp_id, count, tier, emp_colleagues, going_up, mgr_id, mgr_colleagues = stack.pop()
        
        # optionally inform the user
        if count % 1000 >= 0 and count % 1000 <= 1:
            print(f'Done {count} iterations...')

        # figure out who the current employee is
        employee = sorted_df[sorted_df[Headers.EMPLOYEE_ID.value] == emp_id]
        if len(employee) != 1:
            raise ValueError('Employee not found in dataset.')
        
        # figure out current employee's index
        employee_index = employee.index

        # check if the current employee's tier is correct
        employee_tier = sorted_df.loc[employee_index, Headers.TIER.value]
        if employee_tier.values[0] != tier:
            # print(employeeTier.values[0], tier)
            raise ValueError('Not moving up or down hierarchy properly.')

        # if the current employee has been done before, we'll set right, otherwise set left
        if going_up:
            count = set_count(right=True, employee=employee_index, count=count)
        else:
            count = set_count(left=True, employee=employee_index, count=count)

        # check if the current employee has a manager: if so, how many colleagues do they have; if not, then we're at the end of the recursive loop
        if mgr_id == '':
            mgr_id = sorted_df.loc[employee_index, Headers.MANAGER_ID.value].values[0]
            if emp_id != str(ceo_id) and mgr_id != str(ceo_id):
                # print('Populating manager...')
                manager = sorted_df[sorted_df[Headers.EMPLOYEE_ID.value] == mgr_id]
                manager_index = manager.index
                managers_mgr_id = sorted_df.loc[manager_index, Headers.MANAGER_ID.value]
                mgr_colleagues = int(number_of_direct_reports_dict.get(managers_mgr_id.values[0])) - 1
            elif int(sorted_df.loc[employee_index, Headers.RIGHT.value].values[0]) != 0 and emp_id == str(ceo_id):
                count = set_count(right=True, employee=employee_index, count=count)
                print('\nDone!')
                print('Final count:', count - 1)
                continue

        # get the current employee's direct reports and number of direct reports
        direct_reports: list = direct_reports_dict.get(emp_id)
        number_of_direct_reports: int = number_of_direct_reports_dict.get(emp_id)
        
        # if the current employee has direct reports and the number of direct reports is more than 0, go down the chain once
        if number_of_direct_reports and direct_reports and number_of_direct_reports > 0 and len(direct_reports) > 0 and not going_up:
            history.append(emp_id)
            stack.append((direct_reports[0], count, tier + 1, len(direct_reports) - 1, False, emp_id, emp_colleagues))

        # if the current employee has no direct reports but has colleagues, go right once
        elif (going_up and emp_colleagues > 0) or (not going_up and emp_colleagues > 0):
            if emp_id in direct_reports_dict.keys() and emp_id in number_of_direct_reports_dict.keys():
                direct_reports_dict.pop(emp_id)
                number_of_direct_reports_dict.pop(emp_id)

            colleagues: list = direct_reports_dict.get(mgr_id)
            if colleagues:
                colleagues.remove(emp_id)
            else:
                raise ValueError('Employee has no colleagues.')

            direct_reports_dict[mgr_id] = colleagues
            number_of_direct_reports_dict[mgr_id] = len(colleagues)
            count = set_count(right=True, employee=employee_index, count=count)
            stack.append((colleagues[0], count, tier, len(colleagues) - 1, False, mgr_id, mgr_colleagues))

        # if the current employee has no direct reports and no colleagues, go up the chain once
        else:
            count = set_count(right=True, employee=employee_index, count=count)
            if history:
                history.pop()
            else:
                print('\nDone!')
                print('Final count:', count)
                continue
            stack.append((mgr_id, count, tier - 1, mgr_colleagues, True, '', 0))

print('\nStarting algorithm...\n')

# initialize left and right columns
sorted_df[Headers.LEFT.value] = 0
sorted_df[Headers.RIGHT.value] = 0
# get rid of unnecessary column
sorted_df = sorted_df.drop('index', axis=1)

print('Assigning left and right values...\n')

# if the dataset is small, use the recursive function
if len(sorted_df) < 500:
    nested_set_algorithm_recursive(ceo_id, 1, 1, 0)

# otherwise, use the iterative function
else:
    nested_set_algorithm_iterative(ceo_id, ceo_id)

# optionally show the first 20 rows of the final dataframe to see left and right values
print('\n', sorted_df.head(20))
# test that every employee got a left and right value 
leftsAssigned = sorted_df[sorted_df[Headers.LEFT.value] > 0]
rightsAssigned = sorted_df[sorted_df[Headers.RIGHT.value] > 0]
print(f'\nLefts Assigned: {len(leftsAssigned)}, Rights Assigned: {len(rightsAssigned)}, {len(leftsAssigned) == len(rightsAssigned)}\n')

print('Finally printing to csv...\n')

# set output directory
# output_dir = 'orgchart_faux_transformed.csv'
# output dataframe to csv
sorted_df.to_csv(output_dir + '.csv', index=False)

print(f'Output saved to {output_dir}.\n')

# test

# optionally test random employee
test_id = '418LYIC'
# test_id = input('What is the employee ID you would like to test?\n')


# find employee
test_employee = sorted_df[sorted_df[Headers.EMPLOYEE_ID.value] == test_id]
# extract employee index
test_employee_index = test_employee.index
# extract employee id
test_employee_id = test_employee.loc[test_employee_index,Headers.EMPLOYEE_ID.value].values[0]
# extract employee name
test_employee_name = test_employee.loc[test_employee_index,Headers.EMPLOYEE_FIRST_NAME.value].values[0] + ' ' + test_employee.loc[test_employee_index,Headers.EMPLOYEE_LAST_NAME.value].values[0]
# extract left and right values
test_employee_left = test_employee.loc[test_employee_index,Headers.LEFT.value].values[0]
test_employee_right = test_employee.loc[test_employee_index,Headers.RIGHT.value].values[0]
# extract employee tier
test_employee_tier = test_employee.loc[test_employee_index,Headers.TIER.value].values[0]

# find employee's direct chain of command
superiors = sorted_df[(sorted_df[Headers.RIGHT.value] > int(test_employee_right)) & (sorted_df[Headers.LEFT.value] < int(test_employee_left))]
# find all of employee's direct reports and indirect reports
all_indirect_reports = sorted_df[(sorted_df[Headers.RIGHT.value] < int(test_employee_right)) & (sorted_df[Headers.LEFT.value] > int(test_employee_left))]
# find only employee's direct reports
only_direct_reports = sorted_df[(sorted_df[Headers.RIGHT.value] < int(test_employee_right)) & (sorted_df[Headers.LEFT.value] > int(test_employee_left)) & (sorted_df[Headers.TIER.value] == int(test_employee.loc[test_employee_index,Headers.TIER.value].values[0]) + 1)]

# print test employee
print('Trying test employee...\n')
print(f'{test_employee_id = }, {test_employee_name = }, {test_employee_tier = }, {test_employee_left = }, {test_employee_right = }, \n')
print('Superiors:')
print(superiors)
print('\nReports:')
print(only_direct_reports)
# optionally print manager id
# print(only_direct_reports[Headers.MANAGER_ID.value])
print('\nIndirect Reports:')
# optionally print manager id
print(all_indirect_reports)
# print(all_indirect_reports[Headers.MANAGER_ID.value])

# end timer
end = time.time()

# print time elapsed
print(f'\nTime elapsed: {(end - start) // 3600} hours, {((end - start) % 3600) // 60} minutes, and {(end - start) % 3600} seconds.')

# print completion message
print('\nDone!\n')