from scipy.stats import entropy
import markdownFunctions
import pandas as pd
import json
import os

if __name__ == "__main__":

    currentDirectory = os.path.dirname(os.path.abspath(__file__))
    GOTYDirectory = os.path.join(currentDirectory, "GOTY")
    docsFolder = os.path.join(currentDirectory, "docs")

    mainREADME = "# Game of the Year\n\n## Different years\n\n"

    for file in os.listdir(GOTYDirectory):
        completePath = os.path.join(GOTYDirectory, file)

        # Remove .json
        file = file[: -len(".json")]

        # The file with the winners info
        with open(completePath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Read the CSV from the Google Sheets URL
        guesses = pd.read_csv(f"{data["url"]}export?format=csv")

        # Change the columns that have newline
        guesses.columns = [col.split("\n")[0] for col in guesses.columns]

        # Change Marca temporal to datetime
        guesses["Marca temporal"] = pd.to_datetime(
            guesses["Marca temporal"], dayfirst=True
        )

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

        # Get the ponderated score for each participant
        categories["Ponderation"] = 1 - (categories["CorrectCount"] - 1).clip(
            lower=0
        ) / len(guesses)
        guesses["CorrectPonderated"] = (
            guesses[winners.columns]
            .eq(winners.iloc[0])
            .dot(categories.set_index("Award")["Ponderation"])
            * 10
            / categories["Ponderation"].sum()
        )

        # Load the different premade Markdown parts
        premade = markdownFunctions.loadMarkdownParts()
        mainMarkdown = [premade["beginning"]]

        # Sort and show the Correct for each participant
        guesses = guesses.sort_values(
            by=["Correct", "Marca temporal", "Nombre"], ascending=False
        )
        mainMarkdown.append(premade["guesses"])
        mainMarkdown.append(
            markdownFunctions.markdownTable(
                {
                    "Participant": guesses["Nombre"].tolist(),
                    "Correct Guesses": [
                        f"{x} / {len(winners.columns)}"
                        for x in guesses["Correct"].tolist()
                    ],
                    "Ponderated Score": [
                        f"{x:.2f}" for x in guesses["CorrectPonderated"].tolist()
                    ],
                }
            )
        )

        # Sort and show the PercentageCorrect for each category
        grouped = (
            categories.groupby("PercentageCorrect")["Award"].apply(list).reset_index()
        )
        grouped = grouped.sort_values(by="PercentageCorrect", ascending=True)
        mainMarkdown.append(premade["questionDifficulty"])
        mainMarkdown.append(
            markdownFunctions.markdownTable(
                {
                    "Category": [
                        " ".join([f"`{x}`" for x in cats])
                        for cats in grouped["Award"].tolist()
                    ],
                    "Percentage Correct": [
                        f"{x:.2%}" for x in grouped["PercentageCorrect"].tolist()
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
        with open(os.path.join(docsFolder, f"{file}.md"), "w") as f:
            f.write("\n".join(mainMarkdown))

        mainREADME += f"- ### [{file}](./docs/{file}.md)\n"

    # Save the main README
    with open(os.path.join(currentDirectory, "README.md"), "w") as f:
        f.write(mainREADME)
