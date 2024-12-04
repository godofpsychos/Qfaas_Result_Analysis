import os
import json
import csv

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

def format_experiment_name(experiment_name):
    is_gpu = 'gpu' in experiment_name.lower()
    print(f"Is GPU: {is_gpu} for {experiment_name}")

    
    if 'dynamic' in experiment_name.lower():
        if experiment_name.startswith('d'):  
            parts = experiment_name.split('-')
            depth = parts[0][1:]  
            suffix = '_offload_gpu' if is_gpu else '_offload'
            formatted_name = f"depth-{depth}{suffix}"
        elif experiment_name.startswith('t'):  
            parts = experiment_name.split('-')
            depth = parts[0][1:]  
            suffix = '_offload_gpu' if is_gpu else '_offload'
            formatted_name = f"trotter_depth-{depth}{suffix}"

    
    elif 'static' in experiment_name.lower():
        
        if '1|1' in experiment_name or '1|2' in experiment_name or '1|3' in experiment_name:
            
            if experiment_name.startswith('d'):  
                parts = experiment_name.split('-')
                depth = parts[0][1:]  
                suffix = '_offload_gpu' if is_gpu else '_offload'  
                suffix += f'_{experiment_name.split("_")[-1]}'  
                formatted_name = f"depth-{depth}{suffix}"
            elif experiment_name.startswith('t'):  
                parts = experiment_name.split('-')
                depth = parts[0][1:]  
                suffix = '_offload_gpu' if is_gpu else '_offload'  
                suffix += f'_{experiment_name.split("_")[-1]}'  
                formatted_name = f"trotter_depth-{depth}{suffix}"
        else:
            
            if experiment_name.startswith('d'):  
                parts = experiment_name.split('-')
                depth = parts[0][1:]  
                suffix = '_offload_gpu' if is_gpu else '_offload'
                formatted_name = f"depth-{depth}{suffix}"
            elif experiment_name.startswith('t'):  
                parts = experiment_name.split('-')
                depth = parts[0][1:]  
                suffix = '_offload_gpu' if is_gpu else '_offload'
                formatted_name = f"trotter_depth-{depth}{suffix}"

    else:
        
        formatted_name = experiment_name

    return formatted_name



def process_results(root_dir, dags_dir):
    
    dynamic_ms_file = open('dynamic_ms.csv', mode='w', newline='')
    dynamic_s_file = open('dynamic_s.csv', mode='w', newline='')
    static_ms_file = open('static_ms.csv', mode='w', newline='')
    static_s_file = open('static_s.csv', mode='w', newline='')

    dynamic_ms_writer = csv.writer(dynamic_ms_file)
    dynamic_s_writer = csv.writer(dynamic_s_file)
    static_ms_writer = csv.writer(static_ms_file)
    static_s_writer = csv.writer(static_s_file)
    
    
    dynamic_ms_header_written = False
    dynamic_s_header_written = False
    static_ms_header_written = False
    static_s_header_written = False
    
    
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            if file == 'results.json':
                experiment_name = os.path.basename(subdir)
                formatted_experiment_name = format_experiment_name(experiment_name)
                print(f"Processing {formatted_experiment_name}...")

                
                if 'dynamic' in experiment_name.lower():
                    dag_file = os.path.join(dags_dir, 'dynamic.json')
                else:
                    dag_file = os.path.join(dags_dir, 'static.json')
            

                
                with open(dag_file, 'r') as dag_f:
                    dag_data = json.load(dag_f)

                
                dag_nodes = dag_data['Nodes']
                node_names = [node['NodeName'] for node in dag_nodes]

                
                file_path = os.path.join(subdir, file)
                with open(file_path, 'r') as f:
                    try:
                        results_json = json.load(f)
                        function_times = get_function_times(results_json, dag_nodes)

                        
                        row_sec = [formatted_experiment_name] + [function_times.get(node, '') for node in node_names]
                        row_sec.append(sum(function_times.values()))  

                        row_ms = [formatted_experiment_name] + [round(function_times.get(node, 0) * 1000, 3) for node in node_names]
                        row_ms.append(sum(function_times.values()) * 1000)  

                        
                        if 'dynamic' in experiment_name.lower():
                            if not dynamic_ms_header_written:  
                                dynamic_ms_writer.writerow(['experiment_name'] + node_names + ['total_time'])
                                dynamic_ms_header_written = True
                            dynamic_ms_writer.writerow(row_ms)
                            
                            if not dynamic_s_header_written:  
                                dynamic_s_writer.writerow(['experiment_name'] + node_names + ['total_time'])
                                dynamic_s_header_written = True
                            dynamic_s_writer.writerow(row_sec)

                        else:
                            if not static_ms_header_written:  
                                static_ms_writer.writerow(['experiment_name'] + node_names + ['total_time'])
                                static_ms_header_written = True
                            static_ms_writer.writerow(row_ms)
                            
                            if not static_s_header_written:  
                                static_s_writer.writerow(['experiment_name'] + node_names + ['total_time'])
                                static_s_header_written = True
                            static_s_writer.writerow(row_sec)

                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

    
    dynamic_ms_file.close()
    dynamic_s_file.close()
    static_ms_file.close()
    static_s_file.close()

    print(f"Processing complete. The results are saved in the CSV files.")


root_directory = '/home/tarunpal/Downloads/output-sorted/output-dynamic'

dags_directory = 'dags'


process_results(root_directory, dags_directory)
