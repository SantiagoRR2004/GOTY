from scipy.stats import entropy
import markdownFunctions
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

    # Create a category dataframe
    categories = winners.melt(var_name="Award", value_name="Winner")
    categories["CorrectCount"] = categories.apply(
        lambda row: (guesses[row["Award"]] == row["Winner"]).sum(), axis=1
    )
    categories["PercentageCorrect"] = categories["CorrectCount"] / len(guesses)
    categories["Entropy"] = categories.apply(
        lambda row: entropy(guesses[row["Award"]].value_counts(normalize=True)),
        axis=1,
    )

    # Get the amount that each Nombre guessed correctly
    guesses["Correct"] = guesses[winners.columns].eq(winners.iloc[0]).sum(axis=1)

    # Load the different premade Markdown parts
    premade = markdownFunctions.loadMarkdownParts()
    mainMarkdown = [premade["beginning"]]

    # Sort and show the Correct for each participant
    guesses = guesses.sort_values(by="Correct", ascending=False)
    mainMarkdown.append(premade["guesses"])
    mainMarkdown.append(
        markdownFunctions.markdownTable(
            {
                "Participant": guesses["Nombre"].tolist(),
                "Correct Guesses": [
                    f"{x} / {len(winners.columns)}" for x in guesses["Correct"].tolist()
                ],
            }
        )
    )

    # Sort and show the PercentageCorrect for each category
    categories = categories.sort_values(
        by=["PercentageCorrect", "Award"], ascending=True
    )
    mainMarkdown.append(premade["questionDifficulty"])
    mainMarkdown.append(
        markdownFunctions.markdownTable(
            {
                "Category": categories["Award"].tolist(),
                "Percentage Correct": [
                    f"{x:.2%}" for x in categories["PercentageCorrect"].tolist()
                ],
            }
        )
    )

    # Sort and show the Entropy for each category
    categories = categories.sort_values(by=["Entropy", "Award"], ascending=False)
    mainMarkdown.append(premade["controversial"])
    mainMarkdown.append(
        markdownFunctions.markdownTable(
            {
                "Category": categories["Award"].tolist(),
                "Entropy": [f"{x:.4f}" for x in categories["Entropy"].tolist()],
            }
        )
    )

    # Save the Markdown to a file
    with open("README.md", "w") as f:
        f.write("\n".join(mainMarkdown))
