import html
import os
import genanki

task_model_template_front = """
{{Identifier}}
<script>
    document.onload = pycmd("ans")
</script>
"""

task_model_template_back = r"""
{{Text}}
<script>
    function incrementalReveal() {
        let remaining = Array.prototype.slice.call(document.getElementsByClassName("hidden"))
        let content = []
        for (let hidden of remaining) {
            content.push(hidden.innerHTML)
            hidden.innerHTML = "[...]"
        }
        remaining[0].classList.add("active")
        document.addEventListener("keydown", (event) => {
            if (event.keyCode == 72) {
                revealNext()
            }
        })
        document.addEventListener("mousedown", (event) => {
            revealNext()
        })
        let revealNext = () => {
            let hidden = remaining.shift()
            hidden.innerHTML = content.shift()
            hidden.classList.remove("active")
            remaining[0].classList.add("active")
        }
    }
    incrementalReveal()
</script>
"""

task_model_css = """
.hidden.active {
    color: blue;
    text-decoration: underline;
}
"""

task_model = genanki.Model(
    1653857280,
    'Task',
    fields=[
        {'name': 'Identifier'},
        {'name': 'Text'},
    ],
    templates=[
        {
            'name': 'Task',
            'qfmt': task_model_template_front,
            'afmt': task_model_template_back,
        },
    ])
task_model.css = task_model_css


def __make_heading(text: str):
    return f"<u><b>{text}</b></u>"


def __make_pre(text: str):
    return f"<pre>{text}</pre>"


def __make_hidden(text: str):
    return f'<span class="hidden">{text}</span>'


def __add_deck_name(deck_name: str, is_first_line=False):
    output = ""
    if not is_first_line:
        output += os.linesep
    output += __make_heading("Deck") + os.linesep
    output += deck_name + os.linesep
    return output


def __add_task(task: str, is_first_line=False):
    output = ""
    if not is_first_line:
        output += os.linesep
    output += __make_heading("Task") + os.linesep
    output += html.escape(task) + os.linesep
    return output


def __add_additional_information(additional_information: str, is_first_line=False):
    output = ""
    if not is_first_line:
        output += os.linesep
    output += __make_heading("Additional information") + os.linesep
    output += html.escape(additional_information) + os.linesep
    return output


def __add_summary_steps(summary_steps: list, is_first_line=False):
    output = ""
    if not is_first_line:
        output += os.linesep
    output += __make_heading("Summarized steps") + os.linesep
    for summary_step in summary_steps:
        output += __make_hidden(html.escape(summary_step)) + os.linesep
    return output


def __add_steps(steps: list, is_first_line=False):
    output = ""
    if not is_first_line:
        output += os.linesep
    counter = 1
    for step in steps:
        if counter != 1:
            output += os.linesep
        output += __make_heading(f"Step {counter}") + os.linesep
        output += __make_hidden(html.escape(step)) + os.linesep
        counter += 1
    return output


# TODO: add tags, deck name and parent decks
def add_task_note(deck: genanki.Deck, identifier: int,  task: str, steps: list,
                  summary_steps=None, additional_information="", tags=None):
    content = __add_deck_name(deck.name, is_first_line=True)
    content += __add_task(task)

    if additional_information:
        content += __add_additional_information(additional_information)

    if not steps:
        raise Exception("A least one step must always be defined")
    if len(steps) == 1:
        if summary_steps:
            print("Not including summary steps because there is only one step defined")
        content += __add_steps(steps)
    else:
        if not summary_steps:
            raise Exception("A step summary must be included when there is more than one step")
        content += __add_summary_steps(summary_steps)
        content += __add_steps(steps)

    content = __make_pre(content)
    full_identifier = format(deck.deck_id, '05d') + format(identifier, '05d')
    note = CustomNote(model=task_model, fields=[full_identifier, content])
    deck.add_note(note)
    return deck


class CustomNote(genanki.Note):
    @property
    def guid(self):
        return genanki.guid_for(self.fields[0])
