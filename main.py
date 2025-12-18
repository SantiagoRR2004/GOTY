import pandas as pd
import json
import os


if __name__ == "__main__":

    currentDirectory = os.path.dirname(os.path.abspath(__file__))

    # The file with the winners info
    with open(
        os.path.join(currentDirectory, "GOTY", "2025.json"), "r", encoding="utf-8"
    ) as f:
        data = json.load(f)

    # Read the CSV from the Google Sheets URL
    guesses = pd.read_csv(f"{data["url"]}export?format=csv")

    # Change the columns that have newline
    guesses.columns = [col.split("\n")[0] for col in guesses.columns]

    # Create dataframe with winners
    winners = pd.DataFrame(data["awards"], index=[0])

    # Get the amount that each Nombre guessed correctly
    guesses["Correct"] = guesses[winners.columns].eq(winners.iloc[0]).sum(axis=1)

    # Sort and show the Correct for each participant
    guesses = guesses.sort_values(by="Correct", ascending=False)
    for index, row in guesses.iterrows():
        print(f"{row['Nombre']}: {row['Correct']}")
