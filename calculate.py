import pandas as pd

# Function to read instance type data from a CSV file
def read_instance_type_data(csv_file_path):
    df = pd.read_csv(csv_file_path)
    return df

# Function to preprocess pricing values and extract numeric cost
def preprocess_pricing(pricing):
    # Extract numeric cost from the pricing string
    numeric_cost = float(pricing.split()[0])
    return numeric_cost

# Function to calculate required RAM and CPU cores based on the number of users
def calculate_required_resources(num_users):
    # Given resource requirements per user
    ram_per_user = 0.025  # GB
    ram_per_core = 2.5  # GB per CPU core
    storage_per_user = 100  # MB

    # Calculate total resources needed for the given number of users
    total_ram = ram_per_user * num_users  # GB RAM
    total_cores = total_ram / ram_per_core

    # Calculate total storage needed for the given number of users
    total_storage = storage_per_user * num_users  # MB
    # Convert total_storage to GB
    total_storage_gb = total_storage / 1024

    return total_ram, total_cores, total_storage_gb

# Function to calculate the total cost for instances and storage
def calculate_cost(instance_data, instance_type, storage_gb, required_usage):
    instance_cost_per_hour = instance_data.loc[instance_data['Instance type'] == instance_type, 'On-Demand Linux pricing'].values[0]
    storage_cost_per_gb_per_month = 0.08

    # Calculate instance cost per month
    instance_cost_per_month = preprocess_pricing(instance_cost_per_hour) * required_usage * 30

    # Calculate storage cost per month
    storage_cost_per_month = storage_cost_per_gb_per_month * storage_gb / 30 * required_usage

    return storage_cost_per_month, instance_cost_per_month

# Function to find the instances with the lowest cost based on required RAM and CPU
def find_lowest_cost_instance(instance_data, required_ram, required_cpu):
    # Filter instances based on RAM and CPU requirements
    filtered_instances = instance_data[
        (instance_data['Memory (GiB)'] >= required_ram) &
        (instance_data['vCPUs'] >= required_cpu)
    ]

    # Sort instances based on price per hour (you can customize this based on your pricing data)
    sorted_instances = filtered_instances.sort_values('On-Demand Linux pricing', ascending=True)

    # Select the third instance with the lowest cost and desired columns
    selected_columns = ['Instance type', 'vCPUs', 'Cores', 'Memory (GiB)', 'On-Demand Linux pricing']

    lowest_cost_instance = sorted_instances.iloc[2][selected_columns]
    return lowest_cost_instance

def main():
    csv_file_path = 'instancetypes.csv'  # Replace with the actual path to your CSV file
    instance_data = read_instance_type_data(csv_file_path)

    # User input for the number of users
    num_users = int(input("Enter the number of users: "))

    required_usage_option = input("Do you want to specify usage time. Default is 24 hours(y/n)? ").lower() == 'y'
    if required_usage_option:
        required_usage = float(input("Enter required time usage time (hour): "))
    else:
        required_usage= 24


    # Calculate required RAM and CPU cores based on the number of users
    required_ram, required_cpu, required_storage = calculate_required_resources(num_users)

    # Find the instance with the lowest cost based on calculated RAM and CPU
    lowest_cost_instance = find_lowest_cost_instance(instance_data, required_ram, required_cpu)

    # Calculate and print the cost for the selected instance and storage
    instance_type = lowest_cost_instance['Instance type']
    instance_cost_per_month, storage_cost_per_month = calculate_cost(instance_data, instance_type, required_storage, required_usage)
    
    # Calculate total cost per month
    total_cost_per_month = instance_cost_per_month + storage_cost_per_month   

    if not lowest_cost_instance.empty:
        print(f"\nThe instance with the lowest cost and at least {required_ram:.2f} GB RAM and {required_cpu:.2f} CPU cores: \n")
        print(lowest_cost_instance)
        print(f"Cost of instance per month: ${instance_cost_per_month:.2f}")
        print(f"Cost of storage per month: ${storage_cost_per_month:.2f}")
        print(f"\nTotal cost of all services per month: ${total_cost_per_month:.2f}")
    else:
        print("No instances found that meet the requirements.")


if __name__ == '__main__':
    main()
