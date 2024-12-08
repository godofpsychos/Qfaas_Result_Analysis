import os,json,csv,requests
import pandas as pd

dag_path = '/home/tarunpal/Desktop/temp/Qfaas_Result_Analysis/dags'
output_path = '/home/tarunpal/Desktop/temp/Qfaas_Result_Analysis/output-sorted'

sub_dir_dag = [file for dirc, _, files in os.walk(dag_path) for file in files if file.endswith('.json')]
sub_dir_out =[sub_dir for dirc, sub_dirc, _ in os.walk(output_path) for sub_dir in sub_dirc if dirc == output_path]

# print(sub_dir_dag)
# print(sub_dir_out)

def convert_to_csv(data, file_path, column_order=None):
    """
    Converts a list of dictionaries (JSON-like data) to a CSV file with optional column reordering.
    Missing fields will be replaced by 'NA'.
    
    :param data: List of dictionaries containing the data to be written to the CSV
    :param file_path: Path where the CSV file should be saved
    :param column_order: List of columns in the desired order (optional)
    """
    if not data:
        print("The data list is empty.")
        return
    
    # Get all the keys (columns) in all dictionaries
    all_keys = set()
    for item in data:
        all_keys.update(item.keys())
    
    # Convert the keys into a list and ensure they are ordered
    all_keys = sorted(all_keys)

    # If a column order is provided, use it; otherwise, keep the sorted order
    if column_order:
        # Ensure that all columns in column_order exist in the data
        if set(column_order) != set(all_keys):
            print(f"Warning: The provided column order does not match all keys in the data.")
        all_keys = column_order
    
    # Open the CSV file in write mode
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=all_keys)
        
        # Write the header (column names)
        writer.writeheader()
        
        # Write the rows, replacing missing keys with 'NA'
        for item in data:
            for key in all_keys:
                if key not in item:
                    item[key] = 'NA'
            writer.writerow(item)
    
    print(f"CSV file has been created at {file_path}")

def get_function_times(results_json, dag_nodes):
    
    times = {}
    for func in results_json['metadata']['functions']:
        for func_id, func_data in func.items():
            
            for node in dag_nodes:
                if str(node['NodeId']) == str(func_id):  
                    node_name = node['NodeName']
                    duration_sec = round((func_data['end_delta'] - func_data['start_delta']) / 1000, 3)  
                    times[node_name] = duration_sec
                    break  
    return times

overall_results = []
for dir in sub_dir_out:
    sub_sub_dir = os.listdir(f"{output_path}/{dir}")
    # print(sub_sub_dir)
    for json_res_file in sub_sub_dir:
        split_str = json_res_file.split('-')
        # experiment_name = split_str[1:]
        experiment_name = '-'.join(split_str[1:])
        experiment_name = experiment_name.replace('.json','')
        # print("experiment name:", experiment_name)
        subex_name = split_str[0]
        for file in sub_dir_dag:
            filename = file.replace('.json','')
            if filename in json_res_file:
                dag_json_path = f"{dag_path}/{file}" 
        out_json_path = f"{output_path}/{dir}/{json_res_file}"
        with open(dag_json_path, 'r') as dag_f:
            dag_data = json.load(dag_f)
        dag_nodes = dag_data['Nodes']
        node_names = [node['NodeName'] for node in dag_nodes]
        # print("RES file",json_res_file)
        with open(out_json_path, 'r') as f:
            results_json = json.load(f)
        # print('::'*50)
        # print(results_json)
        # print('::'*50)
        try:
            if 'url' in results_json:
                response = requests.get(results_json['url'])
                if response.status_code == 200:
                    results_json =  json.loads(response.json()['output'])
                    # print(results_json['_metadata'])
                    # print('--'*50)
                    results_json['metadata'] = results_json.pop('_metadata')
                else:
                    Exception("Unable to fetch data")
                    exit()
            function_times = get_function_times(results_json, dag_nodes)
            function_times["total_time"] = sum(value for value in function_times.values() if isinstance(value, float))
            function_times["Experiment"] = experiment_name
            function_times["Sub-experiment"] = subex_name
            overall_results.append(function_times)
        except Exception as e:
            print(f"Error processing {out_json_path}: {e}")
            exit()

# print(overall_results)
# file_path = '/home/tarunpal/Desktop/temp/Qfaas_Result_Analysis/func_res.json'
file_path = '/home/tarunpal/Desktop/temp/Qfaas_Result_Analysis/func_res2.csv'

# # Open the file in write mode and use json.dump() to write the data
# with open(file_path, 'w') as file:
#     json.dump(overall_results, file, indent=4)
desired_column_order = ['Experiment', 'Sub-experiment', 'Splitter', 'Transpiler', 'Transpiler1','Transpiler2', 'Submitter','Submitter1',  'Submitter2', 'Merger', 'Poller', 'Reconstructor',"total_time" ]
convert_to_csv(overall_results,file_path,desired_column_order)
print(f"Processing complete. The results are saved in the CSV files.")
