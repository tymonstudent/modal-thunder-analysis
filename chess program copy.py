import chess
import chess.engine
import matplotlib.pyplot as plt
import numpy as np
import os

def get_moves(board, num_moves, depth, stockfish_path=r"C:\Users\kakaz\Documents\chess coding\stockfish\stockfish.exe"):
    moves = []
    engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    engine.configure({"Threads": 6, "Hash": 4096})

    print(f"Analyzing board with depth {depth} for {num_moves} best moves...")
    
    # Analyse the board position
    info_list = engine.analyse(board, chess.engine.Limit(depth=depth), multipv=num_moves)

    # Retrieve moves without evaluations
    for i, info in enumerate(info_list):
        if "pv" in info and info["pv"]:
            move = info["pv"][0]
            moves.append(move)  # Get the top move in the principal variation
            print(f"Move {i + 1}: {move}")

    engine.quit()

    return moves

def evaluate_moves(position, moves, depth):
    evaluations = []
    stockfish_path = r"C:\Users\kakaz\Documents\chess coding\stockfish\stockfish.exe"
    engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    engine.configure({"Threads": 6, "Hash": 4096})

    print(f"Evaluating {len(moves)} moves at depth {depth}...")

    for i, move in enumerate(moves):
        board = position.copy()
        board.push(move)
        result = engine.analyse(board, chess.engine.Limit(depth=depth))

        evaluation = None

        # Check if evaluation score is available
        if "score" in result:
            score = result["score"]
            
            if isinstance(score, chess.engine.PovScore):
                if score.is_mate():
                    mate_value = score.relative.moves
                    if mate_value is not None:
                        if mate_value > 0:
                            evaluation = 15300  # Mate for White
                        elif mate_value < 0:
                            evaluation = -15300  # Mate for Black
                else:
                    evaluation = score.relative.cp
        
        print(f"Move {i + 1}: {move}, Evaluation: {evaluation}")
        evaluations.append((move, evaluation))
    
    engine.quit()
    return evaluations

def format_fens(file_path):
    """Reads FENs from a text file and returns them as a list."""
    with open(file_path, 'r') as f:
        return f.read().strip().split('\n')

def save_results(file_path, results):
    """Saves the calculated results to a text file."""
    print(f"Saving results to {file_path}...")
    with open(file_path, 'w') as f:
        f.write("Position Number, FEN, Variance, Standard Deviation, MAD, IQR\n")
        for result in results:
            pos_num, fen, variance, std_dev, mad, iqr = result
            f.write(f"{pos_num}, {fen}, {variance}, {std_dev}, {mad}, {iqr}\n")
    print("Results saved.")

def plot_statistics(position_variance, position_sd, position_MAD, position_iqr):
    """Plot the Variance, Standard Deviation, MAD, and IQR of the FEN positions."""
    fens, variances = zip(*position_variance)
    _, std_devs = zip(*position_sd)
    _, mads = zip(*position_MAD)
    _, iqrs = zip(*position_iqr)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot Variance
    axes[0, 0].bar(fens, variances)
    axes[0, 0].set_title('Variance')
    axes[0, 0].set_xticklabels(fens, rotation=45)
    
    # Plot Standard Deviation
    axes[0, 1].bar(fens, std_devs)
    axes[0, 1].set_title('Standard Deviation')
    axes[0, 1].set_xticklabels(fens, rotation=45)
    
    # Plot Mean Absolute Deviation
    axes[1, 0].bar(fens, mads)
    axes[1, 0].set_title('Mean Absolute Deviation')
    axes[1, 0].set_xticklabels(fens, rotation=45)
    
    # Plot Interquartile Range
    axes[1, 1].bar(fens, iqrs)
    axes[1, 1].set_title('Interquartile Range')
    axes[1, 1].set_xticklabels(fens, rotation=45)
    
    

def process_fen_file(file_path, output_folder):
    """Processes a single FEN file and saves the results, with position number included."""
    print(f"Processing FEN file: {file_path}")
    fens = format_fens(file_path)
    
    results = []
    position_variance = []
    position_sd = []
    position_MAD = []
    position_iqr = []

    for i, fen in enumerate(fens):
        print(f"Processing position {i + 1}...")
        position = chess.Board(fen)
        best_moves = get_moves(position, num_moves=5, depth=20)
        evaluations = evaluate_moves(position, best_moves, depth=20)

        # Extract evaluation scores for variance calculation
        scores = [evaluation for _, evaluation in evaluations if evaluation is not None]
        if scores:
            spread = max(scores) - min(scores)
            std = np.std(scores)
            median = np.median(scores)
            deviations = np.abs(scores - median)
            MAD = np.median(deviations)
            q3 = np.percentile(scores, 75)
            q1 = np.percentile(scores, 25)
            iqr = q3 - q1
            
            # Store results with position number
            results.append((i + 1, fen, spread, std, MAD, iqr))
            position_variance.append((fen, spread))
            position_sd.append((fen, std))
            position_MAD.append((fen, MAD))
            position_iqr.append((fen, iqr))
    
    # Generate the output file name based on the input file name
    base_name = os.path.basename(file_path)
    output_file = os.path.join(output_folder, f"{os.path.splitext(base_name)[0]}_results.txt")
    
    # Save results to the output file
    save_results(output_file, results)

    # Optionally, plot statistics
    plot_statistics(position_variance, position_sd, position_MAD, position_iqr)

def process_batch_of_files(input_folder, output_folder):
    """Processes all FEN text files in the input folder."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Get all .txt files in the input folder
    fen_files = [f for f in os.listdir(input_folder) if f.endswith('.txt')]
    
    print(f"Found {len(fen_files)} FEN files to process.")
    
    # Process each FEN file
    for fen_file in fen_files:
        input_file_path = os.path.join(input_folder, fen_file)
        process_fen_file(input_file_path, output_folder)

def main():
    # Define the input folder containing FEN files and the output folder for results
    input_folder = "C:/Users/kakaz/Documents/chess coding/Chess games"  # Replace with your folder containing input FEN files
    output_folder = "C:/Users/kakaz/Documents/chess coding/Chess Gmases output"  # Replace with your desired output folder
    
    # Process the batch of FEN files
    process_batch_of_files(input_folder, output_folder)

if __name__ == "__main__":
    main()
 