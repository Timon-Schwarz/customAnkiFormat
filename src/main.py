import os
from pathlib import Path
import pandas as pd
import genanki
import DeckGenerator


if __name__ == '__main__':
    directory = "/home/timon/Documents/notes/networking/new_flashcards"
    extension = "xlsx"
    for file in Path(directory).rglob(f'*.{extension}'):
        file_name = file.name
        file_path = file.absolute()

        try:
            df_task = pd.read_excel(file_path, sheet_name="Tasks")
        except ValueError:
            print(f"No sheet with the name \"Tasks\" was found in file: \"{file_path}\"")
            continue
        try:
            deck_identifier, deck_name = os.path.splitext(file_name)[0].split('-')
            deck_identifier = int(deck_identifier)
            if deck_identifier > 9999999999:
                print("The given deckID is larger than the maximum of 9_999_999_999")
            if deck_identifier == 1:
                print("The deckID 1 can not be used because it is reserved for the \"Default\" Deck")
        except IndexError:
            print("The input file was not in the required format: \"deckID_deckName.xlsx\"")
            print("Example: \"10001_debian.xlsx\"")
            continue
        except ValueError:
            print("The deckID specified must be an integer")
            continue
        deck_name = f'{os.path.relpath(os.path.dirname(file_path), directory).replace("/", "::")}::{deck_name}'
        print(deck_identifier)
        print(deck_name)
        deck = genanki.Deck(deck_identifier, deck_name)
        for row_index, row in df_task.iterrows():
            identifier = row['Identifier']
            if pd.isna(identifier):
                raise Exception(f"No identifier was specified in row {row_index}")

            task = row['Task']
            if pd.isna(task):
                raise Exception(f"No task was specified in row {row_index}")

            additional_information = row['Additional information']
            if pd.isna(additional_information):
                additional_information = None

            summarized_steps = row['Summarized steps']
            summarized_step_list = []
            if pd.notna(summarized_steps):
                for summarized_step in summarized_steps.split('\n'):
                    summarized_step_list.append(summarized_step)

            step_list = []
            for i in range(1, 51):
                step = row[f'Step {i}']
                if pd.isna(step):
                    break
                step_list.append(step)
            if not step_list:
                print("At least one step must always be specified but no steps where")

            deck = DeckGenerator.add_task_note(deck=deck, identifier=identifier, task=row['Task'],
                                               additional_information=additional_information,
                                               summary_steps=summarized_step_list, steps=step_list)
        genanki.Package(deck).write_to_file(os.path.join(directory, deck_name.replace("::", "-") + '.apkg'))
