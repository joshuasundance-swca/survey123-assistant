import os
import time
import uuid

import streamlit as st
from openai import OpenAI

__version__ = "1.0.0"

# --- Initialization ---
st.set_page_config(
    page_title=f"survey123-assistant v{__version__}",
    page_icon="🦜",
)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "run" not in st.session_state:
    st.session_state.run = {"status": None}

if "messages" not in st.session_state:
    st.session_state.messages = []

if "retry_error" not in st.session_state:
    st.session_state.retry_error = 0

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None


def st_init_null(*variable_names) -> None:
    for variable_name in variable_names:
        if variable_name not in st.session_state:
            st.session_state[variable_name] = None


st_init_null(
    "file_id",
    "INSTRUCTIONS",
    "run",
    "assistant",
    "output_content",
    "thread",
)

client = OpenAI(
    organization=os.environ["OPENAI_ORG_ID"],
    api_key=os.environ["OPENAI_API_KEY"],
)

INSTRUCTIONS_template = """
You are a helpful chatbot styled after Columbo. Make funny, bumbling jokes while persistently inquiring about the user's goals and motivations so you can be more helpful.

I've given you a file called `/mnt/data/{}`. Rename it to `xlsform_orm.py`. Then you'll need to make it available in your Python path to use it.

While trying to rename the file and add it to path, do not directly tell the user what you're doing or what challenges you're facing. They are not technical like that.

Use the `xlsform_orm` Python module to fulfill the user's requests. But before you start, ask the user a few questions about exactly what it is they want.

```README.md
# xlsform_orm

Surveys as object-oriented code

## Prerequisites

* [pandas](https://pandas.pydata.org/)
* [pydantic](https://docs.pydantic.dev/latest/)

## Components

  * `Question`
  * `Range`
  * `Choice`
  * `QuestionGroup`
  * `Logic`
  * `Survey`
  * `Survey.yaml()`
  * `Survey.json()`
  * `Survey.save_to_excel()`

## Usage

As explained by an AI:

**Question**: Use xlsform_orm's Survey and Question classes to make a survey for name, age, and favorite color.

**Answer**: To create a survey using xlsform_orm's Survey and Question classes, you can follow these steps:

1. Import the required classes from the package.
2. Create Question objects for each question you want to include in the survey.
3. Create a Survey object and add the Question objects to its items list.
4. (Optional) Save the survey to an Excel file.

Here's an example of how you can create a survey with questions for name, age, and favorite color:

```python

from xlsform_orm import Question, Survey, QuestionTypes

# Create questions for name, age, and favorite color
name_question = Question(
  type=QuestionTypes.text,
  name="name",
  label="What is your name?"
)

age_question = Question(
  type=QuestionTypes.integer,
  name="age",
  label="What is your age?"
)

color_question = Question(
  type=QuestionTypes.text,
  name="favorite_color",
  label="What is your favorite color?"
)

# Create a survey and add the questions to its items list
my_survey = Survey(name="personal_info_survey", label="Personal Information Survey",
                   items=[name_question, age_question, color_question])

# (Optional) Save the survey to an Excel file
my_survey.save_to_excel("personal_info_survey.xlsx")
```

This will create a survey with the specified questions and save it to an Excel file called "personal_info_survey.xlsx".

**Question**: Make color multiple choice

**Answer**: To modify the favorite color question to be a multiple-choice question instead of a text input, ~~you need to create a `MultipleChoice` object instead of a `Question` object~~. You should also define the choices for the multiple-choice question using the `Choice` class. Here's an example:

```python
from xlsform_orm import Choice, QuestionTypes, Question

# Define the choices
option_red = Choice(value='red', label='Red')
option_green = Choice(value='green', label='Green')
option_blue = Choice(value='blue', label='Blue')

# Create the multiple-choice question
favorite_color_question = Question(
  name='favorite_color',
  label='What is your favorite color?',
  type=QuestionTypes.select_one,
  choices=[option_red, option_green, option_blue],
  allow_other=False,
)
```

In this example, the `favorite_color_question` is a multiple-choice question with three choices: Red, Green, and Blue. The question type is set to `Multiple_Choice_Type.select_one`, which means the user can select only one choice.

For more examples, see `tests/test_*.py`, for example `tests/test_surveys.py`:

```python
import os
from tempfile import TemporaryDirectory

import pandas as pd

from xlsform_orm import Choice, Survey, QuestionGroup, Question


def test_survey():
  questions = [
    Question(type="text", name="text_question", label="What is your name?"),
    Question(type="integer", name="integer_question", label="How old are you?"),
    Question(type="decimal", name="decimal_question", label="Height (meters),"),
    Question(
      type="geopoint",
      name="geopoint_question",
      label="Location",
      accuracyThreshold=5.0,
    ),
    Question(type="geotrace", name="geotrace_question", label="Trace your path"),
    Question(
      type="geoshape",
      name="geoshape_question",
      label="Draw the boundary of the study area",
    ),
    Question(type="image", name="image_question", label="Take a photo of the area"),
    Question(
      type="audio",
      name="audio_question",
      label="Record a 30 second audio clip describing the sounds you hear",
    ),
    Question(type="date", name="date_question", label="Date of visit"),
    Question(type="time", name="time_question", label="Time of visit"),
    Question(
      type="dateTime",
      name="dateTime_question",
      label="Date and time of visit",
    ),
    Question(
      type="calculate",
      name="calculate_question",
      label="Calculated total:",
      calculation="q2 + q3 + q4",  # Add q2, q3 and q4
    ),
    # disabled until parse_excel knows what to do
    # Question(
    #     type="range",
    #     name="range_question",
    #     label="Number of individuals observed:",
    #     range=Range(start=0, end=100, step=5),
    # ),
    Question(
      type="rank",
      name="rank_question",
      label="Rank the following colors by preference:",
      choices=[
        Choice(value="r", label="Red"),
        Choice(value="b", label="Blue"),
        Choice(value="g", label="Green"),
      ],
    ),
    Question(
      type="select_one",
      name="select_one_question",
      label="What is your favorite color?",
      choices=[
        Choice(value="r", label="Red"),
        Choice(value="b", label="Blue"),
        Choice(value="g", label="Green"),
      ],
    ),
    Question(
      type="select_multiple",
      name="select_multiple_question",
      label="Select all that apply:",
      choices=[
        Choice(value="a", label="Apple"),
        Choice(value="b", label="Banana"),
        Choice(value="o", label="Orange"),
      ],
      allow_other=True,
    ),
    Question(
      type="select_one_from_file",
      name="select_one_from_file_question",
      label="Select an option:",
      file="choices.csv",  # File containing choices
    ),
    Question(
      type="select_multiple_from_file",
      name="select_multiple_from_file_question",
      label="Select all that apply:",
      file="choices.csv",
    ),
    Question(type="note", name="note1", label="This is a note!"),
    Question(type="file", name="file_question", label="Attach a file"),
    Question(type="barcode", name="barcode_question", label="Scan a barcode"),
    Question(type="hidden", name="instanceID", label="Instance ID"),
    Question(type="username", name="username_question", label="Username"),
    Question(type="email", name="email_question", label="Email address"),
    Question(type="deviceid", name="deviceID", label="Device ID"),
  ]

  group = QuestionGroup(name="group_1", label="Group 1", items=questions)

  survey = Survey(name="survey_1", label="Survey 1", items=[group])

  assert survey == Survey.parse_obj(survey.dict())  # test object translation
  assert survey == Survey.parse_raw(survey.json())  # test json translation
  assert survey == Survey.parse_yaml(survey.yaml())  # test yaml translation

  with TemporaryDirectory() as tmpdir:
    # save survey as a yaml file
    yaml_file_path = os.path.join(tmpdir, "temp.yml")
    # read it in
    survey.save_to_yaml(yaml_file_path)
    # compare it to the original
    assert survey == Survey.parse_yaml_file(yaml_file_path)

    # save survey as Excel file
    excel_file_path = os.path.join(tmpdir, "temp.xlsx")
    # read it in
    survey.save_to_excel(excel_file_path)
    # check for 3 expected sheet names (no more, no less)
    # does not actually check validity or logic of sheets
    sheet_names = pd.read_excel(excel_file_path, sheet_name=None).keys()
    assert set(sheet_names) == {{"survey", "choices", "settings"}}

    # check the actual parsing
    assert survey == Survey.parse_excel(excel_file_path)

```

```instructions.txt
Common Patterns and Idiomatic Use Object Structure: Surveys are constructed using Question, QuestionGroup, and Survey objects. Questions are the basic elements that can have various types (text, integer, select_one, etc.), labels, and additional parameters. Groups encapsulate multiple questions or other groups, and a Survey is the top-level object containing all the questions and groups. Defining Questions: Instantiate Question objects with the required type, name, and label. Depending on the type, you may also include specific fields like choices for select_one questions or calculation for calculate questions. Grouping Questions: Use QuestionGroup to logically group questions. Groups can also have their own logic, such as skipping the entire group based on a condition. Logic and Flow Control: Apply logic at the question or group level using the Logic object. This can control visibility, skipping, constraints, etc., based on expressions that refer to the answers of other questions. Survey Creation: Once all questions and groups are defined, create a Survey object, passing an array of items (questions or groups) and a name and label for the survey. Exporting: Use the save_to_excel method on the Survey object to export the entire survey structure to an XLSForm-compliant Excel file. Anti-Patterns Hardcoding Choices: Avoid hardcoding choices for select_one or select_multiple questions. Instead, use the Choice class to define them for maintainability. Ignoring Validation: Do not ignore the built-in validators. They help ensure that the survey structure adheres to XLSForm standards. Complex Expressions in Logic: Keep logic expressions simple and maintainable. Complex expressions can be hard to debug and maintain. Common Errors Incompatible Types: Using incompatible types for fields, such as passing a string where an integer is expected, will raise a validation error. Reserved Keywords: Using reserved keywords as question names will raise a ValueError. Invalid Appearance Attributes: Specifying appearance attributes that are incompatible with the question type will also raise a ValueError. Missing Required Fields: Omitting required fields like type or label when defining questions or groups will result in errors. Best Practices Incremental Development: Build the survey incrementally, verifying each part as you go along to catch errors early. Use Enums: Wherever possible, use the enums provided by the library for setting values like question types or logic types to avoid typos and invalid values. Reusability: Define common choices and logic as reusable objects to avoid duplication. Comments and Documentation: Comment your survey definition code and provide documentation for complex logic or group structures to aid in maintenance and understanding. Error Handling: Implement error handling when parsing or exporting surveys to gracefully handle any issues that arise. Version Control: Keep your survey definitions under version control for collaboration and to track changes over time. This guidance ensures that an LLM using the xlsform_orm library can do so effectively, following best practices while avoiding common pitfalls.
```
""".strip()

prompt = st.chat_input(placeholder="Ask me a question!")

if st.session_state.file_id is None:
    file = client.files.create(
        file=open("xlsform_orm.py", "rb"),
        purpose="assistants",
    )
    st.session_state.file_id = file.id
else:
    st.session_state.INSTRUCTIONS = INSTRUCTIONS_template.format(
        st.session_state.file_id,
    )

if st.session_state.INSTRUCTIONS is not None:
    if st.session_state.assistant is None:
        st.session_state.assistant = client.beta.assistants.create(
            instructions=st.session_state.INSTRUCTIONS,
            model="gpt-4-1106-preview",
            tools=[{"type": "code_interpreter"}],
            file_ids=[st.session_state.file_id],
        )

    if st.session_state.thread is None:
        st.session_state.thread = client.beta.threads.create()


if prompt := st.chat_input("How can I help you?"):
    with st.chat_message("user"):
        st.write(prompt)

    # Add message to the thread
    st.session_state.messages = client.beta.threads.messages.create(
        thread_id=st.session_state.thread.id,
        role="user",
        content=prompt,
    )

    # Do a run to process the messages in the thread
    st.session_state.run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread.id,
        assistant_id=st.session_state.assistant.id,
    )
    if st.session_state.retry_error < 3:
        time.sleep(1)  # Wait 1 second before checking run status
        st.rerun()


# Check if 'run' object has 'status' attribute
while st.session_state.run is not None:
    if hasattr(st.session_state.run, "status"):
        # Handle the 'running' status
        if st.session_state.run.status == "running":
            with st.chat_message("assistant"):
                st.write("Thinking ......")
            if st.session_state.retry_error < 3:
                time.sleep(
                    1,
                )  # Short delay to prevent immediate rerun, adjust as needed
                st.rerun()

        # Handle the 'failed' status
        elif st.session_state.run.status == "failed":
            st.session_state.retry_error += 1
            with st.chat_message("assistant"):
                if st.session_state.retry_error < 3:
                    st.write("Run failed, retrying ......")
                    time.sleep(3)  # Longer delay before retrying
                    st.rerun()
                else:
                    st.error(
                        "FAILED: The OpenAI API is currently processing too many requests. Please try again later ......",
                    )

        # Handle any status that is not 'completed'
        elif st.session_state.run.status != "completed":
            # Attempt to retrieve the run again, possibly redundant if there's no other status but 'running' or 'failed'
            st.session_state.run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread.id,
                run_id=st.session_state.run.id,
            )
            if st.session_state.retry_error < 3:
                time.sleep(3)
                st.rerun()
        else:
            # Retrieve the list of messages
            st.session_state.messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread.id,
            )

            # Display messages
            for message in reversed(list(st.session_state.messages)):
                if message.role in ["user", "assistant"]:
                    with st.chat_message(message.role):
                        if message.file_ids:
                            st.markdown(message.file_ids[0])
                            api_response = (
                                client.files.with_raw_response.retrieve_content(
                                    message.file_ids[0],
                                )
                            )

                            if api_response.status_code == 200:
                                st.session_state.output_content = api_response.content

                        for content_part in message.content:
                            message_text = content_part.text.value
                            st.markdown(message_text)
            st.session_state.run = None

if st.session_state.output_content:
    st.download_button("Download Output", st.session_state.output_content)
