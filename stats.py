import pandas
import json

def get_all_results(file_path: str) -> list:
    with open(file_path, "r") as f:
        return [json.loads(line) for line in f]
def create_stats_grouped(results: list, grouping_list: list, save_tp : bool = False) -> dict:
    df = pandas.DataFrame(results)
    # count tp, fp, fn for each group
    grouped_df = df.groupby(grouping_list).size().unstack(fill_value=0).reset_index()
    tp, fp, fn = grouped_df["tp"], grouped_df["fp"], grouped_df["fn"]
    # calculate accuracy, precision, recall, f1_score
    grouped_df["accuracy"] = tp / (tp + fp + fn)
    grouped_df["precision"]= tp / (tp + fp)
    grouped_df["recall"] = tp / (tp + fn)
    grouped_df["f1_score"] = 2 * (grouped_df["precision"] * grouped_df["recall"]) / (grouped_df["precision"] + grouped_df["recall"]) 
    # for generating the sheet for confusion matrix 
    if not save_tp:
        grouped_df = grouped_df.drop(columns=["tp", "fp", "fn"])
    else:
        grouped_df = grouped_df.drop(columns=["accuracy", "precision", "recall", "f1_score"])
    return grouped_df


if __name__ == "__main__":
    files = ["results/results_llama3.json", "results/results_mistral.json", "results/results_gemini.json"]
    results = []
    for file in files:
        results.extend(get_all_results(file))
        
    grouped_by_qtype = create_stats_grouped(results, ["question_type", "result_type"])
    grouped_by_distracted = create_stats_grouped(results, ["is_distracted", "result_type"])
    grouped_by_model = create_stats_grouped(results, ["model", "result_type"])
    grouped_by_distracted_for_confusion = create_stats_grouped(results, ["is_distracted", "result_type"], save_tp=True)
    # save each grouped dataframe to a separate sheet in an excel file
    with pandas.ExcelWriter("results/statistics.xlsx") as writer:
        grouped_by_qtype.to_excel(writer, sheet_name="grouped_by_qtype", index=False)
        grouped_by_distracted.to_excel(writer, sheet_name="grouped_by_distracted", index=False)
        grouped_by_model.to_excel(writer, sheet_name="grouped_by_model", index=False)
        grouped_by_distracted_for_confusion.to_excel(writer, sheet_name="confusion_matrix", index=False)
