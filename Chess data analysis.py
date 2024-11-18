import csv
import matplotlib.pyplot as plt
import os
import math
# Function to read data from CSV file and structure it
def read_data_from_file(file_path):
    data = []
    print(f"Reading data from {file_path}...")
    
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Convert relevant columns to float and store in the data structure
            data.append({
                "Position": int(row["Position Number"]),
                "Variance": float(row[" Variance"]),
                "IQR": float(row[" IQR"]),
                "SD": float(row[" Standard Deviation"]),
                "MAD": float(row[" MAD"])
            })
    
    print(f"Finished reading {len(data)} rows from {file_path}.")
    return data

def euclidean_distance_2d(P1, P2):
    pos1, val1 = P1
    pos2, val2 = P2
    return math.sqrt((pos2 - pos1) ** 2 + (val2 - val1) ** 2)

# Function to find critical points for a given metric series
def find_critical_points(metric_data):
    critical_points = []
    
    for i in range(len(metric_data) - 2):  # Ensure there's space to check next two points
        P_i = (i + 1, metric_data[i])        # Position i+1 and its corresponding value
        P_i1 = (i + 2, metric_data[i + 1])   # Position i+2 and its corresponding value
        P_i2 = (i + 3, metric_data[i + 2])   # Position i+3 and its corresponding value
        
        # Condition 1: P_{i+1} < P_i and P_{i+2} < P_{i+1}
        if P_i1[1] < P_i[1] and P_i2[1] < P_i1[1]:
            
            # Condition 2: Euclidean distance check
            dist_1_to_3 = euclidean_distance_2d(P_i, P_i2)
            dist_sum = euclidean_distance_2d(P_i, P_i1) + euclidean_distance_2d(P_i1, P_i2)
            
            if dist_1_to_3 < dist_sum:
                critical_points.append((i, P_i[1], P_i1[1], P_i2[1]))
    
    return critical_points

# Function to save results to a text file
def save_results_to_file(critical_points, metric, output_dir):
    output_file = os.path.join(output_dir, f"{metric}_critical_points.txt")
    
    with open(output_file, 'w') as f:
        f.write(f"Critical points for {metric}:\n")
        for idx, P_i, P_i1, P_i2 in critical_points:
            f.write(f"Position {idx+1}: {P_i} -> {P_i1} -> {P_i2}\n")
    
    print(f"Results saved to {output_file}")

# Function to generate and save a graph of the metric and its critical points
def plot_metric_with_critical_points(metric_data, critical_points, metric, output_dir):
    positions = list(range(1, len(metric_data) + 1))
    
    plt.figure(figsize=(10, 6))
    plt.plot(positions, metric_data, marker='o', label=f'{metric} values')
    
    # Highlight the critical points
    for idx, P_i, P_i1, P_i2 in critical_points:
        plt.scatter([idx+1, idx+2, idx+3], [P_i, P_i1, P_i2], color='red', s=100, zorder=5, label='Critical Point' if idx == 0 else None)

    plt.title(f'{metric} and Critical Points')
    plt.xlabel('Position')
    plt.ylabel(f'{metric}')
    plt.legend()
    plt.grid(True)
    
    # Save the plot
    output_file = os.path.join(output_dir, f"{metric}_graph.png")
    plt.savefig(output_file)
    plt.close()
    
    print(f"Graph saved to {output_file}")

# Main function to process a batch of files
def analyze_metrics_from_folder(input_folder_path, output_folder_path):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    
    # Get a list of TXT files in the folder
    files = [f for f in os.listdir(input_folder_path) if f.endswith('.txt')]
    
    print(f"Found {len(files)} TXT files in {input_folder_path}.")
    
    for file_name in files:
        file_path = os.path.join(input_folder_path, file_name)
        
        # Read data from the file
        data = read_data_from_file(file_path)
        
        # Create a subfolder to store the results for this file
        file_base_name = os.path.splitext(file_name)[0]
        output_dir = os.path.join(output_folder_path, f'analysis_results_{file_base_name}')
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Iterate over each metric (Variance, IQR, SD, MAD) and analyze them independently
        metrics = ["Variance", "IQR", "SD", "MAD"]
        
        for metric in metrics:
            print(f"\nAnalyzing {metric} for {file_name}...")
            metric_values = [entry[metric] for entry in data]  # Extract values for the specific metric
            
            critical_points = find_critical_points(metric_values)
            print(f"Found {len(critical_points)} critical points for {metric}.")
            
            # Save the results to a text file
            save_results_to_file(critical_points, metric, output_dir)
            
            # Generate and save a plot for this metric
            plot_metric_with_critical_points(metric_values, critical_points, metric, output_dir)
    
    print("\nBatch analysis complete.")

# Specify the input folder containing the TXT files
input_folder_path = r'C:\Users\kakaz\Documents\chess coding\Chess Gmases output'
# Specify the output folder where results will be saved
output_folder_path = r'C:\Users\kakaz\Documents\chess coding\Chess Gmases output\analysis_results'

# Run the analysis on the batch of files
analyze_metrics_from_folder(input_folder_path, output_folder_path)
