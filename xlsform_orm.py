"""Lightweight library supporting XLSForm-as-code."""
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import pandas as pd
import yaml
from pydantic import BaseModel, Field, root_validator, validator


class LogicTypes(Enum):
    """Valid logic types."""

    trigger = "trigger"
    skip = "skip"
    relevant = "relevant"
    constraint = "constraint"


class Logic(BaseModel):
    """
    Logic for flow control and constraints.

    Notes
    -----
    Logic can be applied at the Question or QuestionGroup level.

    The type field determines the type of logic:

    - `trigger`: Show or hide a question group
    - `skip`: Skip a question or group
    - `relevant`: Show or hide a question or group
    - `constraint`: Add a validation constraint to a question

    For `constraint` logic:

      * `message`: The error message to display if the constraint fails. Required.

    Examples
    --------
    .. code-block:: python

        # Trigger logic
        Logic(
            type="trigger",
            expression="${q1} = 'yes'",  # Trigger when q1 is 'yes'
        )

        # Skip logic
        Logic(
            type="skip",
            expression="${q2} = 2"  # Skip when q2 is 2
        )

        # Relevant logic
        Logic(
            type="relevant",
            expression="${q3} = 'x'"  # Make relevant when q3 is 'x'
        )

        # Constraint logic
        Logic(
            type="constraint",
            expression="${q4} < 18",   # Add constraint q4 < 18
            message="Must be over 18!"  # Error message
        )

    .. code-block:: python

        # Trigger (on a QuestionGroup based on a previous Question):

        q1 = Question(type='text', name="q1", label="Question 1")
        q2 = q3 = q1

        group1 = QuestionGroup(
            name="group1",
            label="Group 1",
            items=[q2, q3],
            logics=[
                Logic(  # Trigger group1 when q1 is 'yes'
                    type="trigger",
                    expression="${q1} = 'yes'"
                )
            ]
        )

        # Skip (on a Question based on a previous Question in the same group):

        group1 = QuestionGroup(
            name="group1",
            label="Group 1",
            items=[
                Question(name="q1", label="Question 1", type='text'),
                Question(name="q2", label="Question 2", type='integer'),
                Question(  # Skip q3 when q2 is 2
                    type='text',
                    name="q3",
                    label="Question 3",
                    logics=[
                        Logic(
                            type="skip",
                            expression="${q2} = 2"
                        )
                    ]
                )
            ]
        )

        # Relevant (show a QuestionGroup based on a previous Question):

        q1 = Question(name="q1", label="Question 1", type='text')

        group1 = QuestionGroup(
            name="group1",
            label="Group 1",
            items=[q2, q3],
            logics=[
                Logic(  # Make group1 relevant when q1 is 'x'
                    type="relevant",
                    expression="${q1} = 'x'"
                )
            ]
        )

        # Constraint (on a Question):

        q1 = Question(
            name="q1",
            label="Question 1",
            type='text',
            logics=[
                Logic(  # Add constraint to q1
                    type="constraint",
                    expression="${q1} != 'yes'",
                    message="q1 must be 'yes'!"
                )
            ]
        )

    """

    type: Union[LogicTypes, str] = Field(..., description="logic type")
    expression: str = Field(..., description="logic expression")
    message: Optional[str] = Field(None, description="constraint message")

    class Config:
        """pydantic configuration."""

        use_enum_values = True

    @validator("message")
    def validate_message(cls, v, values):
        """Set message to None unless type == 'constraint'."""
        if values["type"] != "constraint":
            v = None
        return v


class Choice(BaseModel):
    """An individual choice for a rank or multiple choice question."""

    value: str = Field(..., description="The value of the choice")
    label: str = Field(..., description="The label of the choice")


class Range(BaseModel):
    """A value range for a range question."""

    start: Union[int, float] = Field(
        ...,
        description="the value at which the range begins",
    )
    end: Union[int, float] = Field(..., description="the value at which the range ends")
    step: Union[int, float] = Field(
        ...,
        description="the size of each division in the range",
    )


class GroupTypes(Enum):
    """Valid group types."""

    group = "group"
    repeat = "repeat"


class QuestionTypes(Enum):
    """Valid question types."""

    text = "text"
    integer = "integer"
    decimal = "decimal"
    date = "date"
    time = "time"
    dateTime = "dateTime"
    select_one = "select_one"
    select_multiple = "select_multiple"
    select_one_from_file = "select_one_from_file"
    select_multiple_from_file = "select_multiple_from_file"
    rank = "rank"
    range = "range"
    note = "note"
    geopoint = "geopoint"
    geotrace = "geotrace"
    geoshape = "geoshape"
    image = "image"
    audio = "audio"
    file = "file"
    barcode = "barcode"
    begin = "begin"
    end = "end"
    # one `end` for groups, one for metadata
    calculate = "calculate"
    hidden = "hidden"
    username = "username"
    email = "email"
    start = "start"
    # end = "end"
    # one `end` for groups, one for metadata
    deviceid = "deviceid"

    # not supported by s123:

    # end = "end"
    # background_audio = "background-audio"
    # video = "video"
    # acknowledge = "acknowledge"
    # xml_external = "xml-external"


class AppearanceAttributes(Enum):
    """Valid appearance attributes."""

    multiline = "multiline"
    minimal = "minimal"
    quick = "quick"
    no_calendar = "no-calendar"
    month_year = "month-year"
    year = "year"
    horizontal_compact = "horizontal-compact"
    horizontal = "horizontal"
    likert = "likert"
    compact = "compact"
    quickcompact = "quickcompact"
    field_list = "field-list"
    label = "label"
    list_nolabel = "list-nolabel"
    table_list = "table-list"
    signature = "signature"
    draw = "draw"
    map = "map"
    quick_map = "quick map"

    # only available in s123:

    minimal_compact = "minimal compact"
    image_map = "image-map"
    autocomplete = "autocomplete"
    predictivetext = "predictivetext"
    nopredictivetext = "nopredictivetext"
    week_number = "week-number"
    distress = "distress"
    spinner = "spinner"
    numbers = "numbers"
    calculator = "calculator"
    thousands_sep = "thousands-sep"
    no_ticks = "no-ticks"
    annotate = "annotate"
    new_rear = "new-rear"
    new_front = "new-front"
    hidden = "hidden"
    geocode = "geocode"
    hide_input = "hide-input"
    press_to_locate = "press-to-locate"
    spike = "spike"
    spike_full_measure = "spike-full-measure"
    spike_point_to_point = "spike-point-to-point"


class Question(BaseModel):
    """
    A question of any type supported by XLSForm.

    Notes
    -----
    The type field determines what additional keyword arguments can be used.

    For `calculate` questions:
        * `calculation`: The calculation expression. Required.
    For `range` questions:
        * `range`: The range parameters, either as a Range object or dict. Required.
    For `geopoint`, `geotrace` and `geoshape` questions:
        * `accuracyThreshold`: The accuracy threshold for the question. Optional.
    For `select_one`, `select_multiple` and `rank` questions:
        * `choices`: The list of choices. Required.
        * `allow_other`: Whether to allow "other" as a choice. Optional.
    For `select_one_from_file` and `select_multiple_from_file` questions:
        * `file`: The name of the file containing choices. Required.

    The parameters field can be used to pass additional type-specific parameters.

    The `appearance_attributes` field sets the appearance for the question.
    It is validated to ensure compatibility with the question type.

    Question name is validated by making sure it is a reserved keyword.

    Examples
    --------
    .. code-block:: python

        Question(
            type="text",
            name="text_question",
            label="What is your name?"
        )

        Question(
            type="integer",
            name="integer_question",
            label="How old are you?"
        )

        Question(
            type="decimal",
            name="decimal_question",
            label="Height (meters),"
        )

        Question(
            type="geopoint",
            name="geopoint_question",
            label="Location"
            accuracyThreshold=5.0,
        )

        Question(
            type="geotrace",
            name="geotrace_question",
            label="Trace your path"
        )

        Question(
            type="geoshape",
            name="geoshape_question",
            label="Draw the boundary of the study area"
        )

        Question(
            type="image",
            name="image_question",
            label="Take a photo of the area"
        )

        Question(
            type="audio",
            name="audio_question",
            label="Record a 30 second audio clip describing the sounds you hear"
        )

        Question(
            type="date",
            name="date_question",
            label="Date of visit"
        )

        Question(
            type="time",
            name="time_question",
            label="Time of visit"
        )

        Question(
            type="dateTime",
            name="dateTime_question",
            label="Date and time of visit"
        )

        Question(
            type="calculate",
            name="calculate_question",
            label="Calculated total:",
            calculation="q2 + q3 + q4"  # Add q2, q3 and q4
        )

        Question(
            type="range",
            name="range_question",
            label="Number of individuals observed:",
            range=Range(start=0, end=100, step=5),
        )

        Question(
            type="rank",
            name="rank_question",
            label="Rank the following colors by preference:",
            choices=[
                Choice(value="r", label="Red"),
                Choice(value="b", label="Blue"),
                Choice(value="g", label="Green"),
            ]
        )

        Question(
            type="select_one",
            name="select_one_question",
            label="What is your favorite color?",
            choices=[
                Choice(value="r", label="Red"),
                Choice(value="b", label="Blue"),
                Choice(value="g", label="Green"),
            ]
        )

        Question(
            type="select_multiple",
            name="select_multiple_question",
            label="Select all that apply:",
            choices=[
                Choice(value="a", label="Apple"),
                Choice(value="b", label="Banana"),
                Choice(value="o", label="Orange"),
            ],
            allow_other=True
        )

        Question(
            type="select_one_from_file",
            name="select_one_from_file_question",
            label="Select an option:",
            file="choices.csv"  # File containing choices
        )

        Question(
            type="select_multiple_from_file",
            name="select_multiple_from_file_question",
            label="Select all that apply:",
            file="choices.csv"
        )

        Question(
            type="note",
            name="note1",
            label="This is a note!"
        )

        Question(
            type="file",
            name="file_question",
            label="Attach a file"
        )

        Question(
            type="barcode",
            name="barcode_question",
            label="Scan a barcode"
        )

        Question(
            type="hidden",
            name="instanceID",
            label="Instance ID"
        )

        Question(
            type="username",
            name="username_question",
            label="Username"
        )

        Question(
            type="email",
            name="email_question",
            label="Email address"
        )

        Question(
            type="deviceid",
            name="deviceID",
            label="Device ID"
        )

    """

    type: Union[QuestionTypes, str] = Field(..., description="xlsform question type")
    name: str = Field(..., description="question name")
    label: str = Field(..., description="question label")
    required: Optional[bool] = Field(
        None,
        description="True if question must be answered",
    )
    default: Optional[str] = Field(None, description="default answer to question")
    hint: Optional[str] = Field(None, description="hint text shown for this question")
    logics: Optional[List[Logic]] = Field(None, description="question-level logic")

    # calculate
    calculation: Optional[str] = Field(
        None,
        description="expression used in calculation",
    )

    # range
    range: Optional[Union[Range, Dict[str, Union[int, float]]]] = Field(
        None,
        description="parameters for range questions",
    )

    # geopoint, geotrace, geoshape
    accuracyThreshold: Optional[float] = Field(
        None,
        description="accuracy threshold used by geo questions",
    )

    # select_one, select_multiple
    choices: Optional[List[Choice]] = Field(
        None,
        description="choices for multiple choice and rank questions",
    )
    allow_other: Optional[bool] = Field(
        None,
        description="True if Other should be an option for multiple choice questions",
    )
    # select_one_from_file, select_multiple_from_file
    file: Optional[str] = Field(
        None,
        description="file used by questions with choices from file",
    )

    parameters: Optional[dict] = Field(
        None,
        description="parameter dict, specific to different question types",
    )
    appearance_attributes: Optional[AppearanceAttributes] = Field(
        None,
        description="question-level appearance attributes",
    )

    class Config:
        """pydantic configuration."""

        use_enum_values = True

    @validator("name")
    def validate_name(cls, v, values):
        """Raise ValueError if question name is a reserved keyword."""
        if v in RESERVED_NAMES:
            raise ValueError(f"{v} cannot be used as a question name")
        return v

    @root_validator(pre=False)
    def validate_by_type(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a number of validations based on value of `type` field."""
        type = values["type"]

        if not hasattr(QuestionTypes, type):
            raise ValueError("Invalid question type")

        def check_associated(
            q_type: Union[str, Tuple[str, ...]],
            associated_field: str,
            required: bool = True,
        ):
            """Check for None if required; set None if unnecessary."""
            q_type = (q_type,) if isinstance(q_type, str) else q_type
            if type in q_type:
                if required and values[associated_field] is None:
                    raise ValueError(
                        f"{associated_field} required for type '{type}'",
                    )
            else:
                values[associated_field] = None

        check_associated("calculate", "calculation")
        check_associated(("rank", "select_one", "select_multiple"), "choices")
        check_associated(
            ("rank", "select_one", "select_multiple"),
            "allow_other",
            required=False,
        )
        check_associated(
            ("geopoint", "geotrace", "geoshape"),
            "accuracyThreshold",
            required=False,
        )
        check_associated(("select_one_from_file", "select_multiple_from_file"), "file")

        if type == "range":
            range_params = values["range"]
            if range_params is None:
                raise ValueError("range cannot be None when type == 'range'")
            parameters = values["parameters"] or {}
            parameters["start"] = range_params.start
            parameters["end"] = range_params.end
            parameters["step"] = range_params.step
            values["parameters"] = parameters

        return values

    @validator("appearance_attributes", pre=False)
    def check_appearance_attributes(cls, appearance_attributes, values):
        """
        Validate the appearance attributes for the question.

        Raises
        ------
        ValueError: If appearance is incompatible with question type.
        """
        if appearance_attributes is None:
            return appearance_attributes
        appearance_attributes = appearance_attributes
        type = values.get("type")
        if not check_appearance_question_combo(appearance_attributes, type):
            raise ValueError
        return appearance_attributes


class QuestionGroup(BaseModel):
    """
    A group of questions or subgroups.

    Examples
    --------
    .. code-block:: python

        # A standard question group
        group1 = QuestionGroup(
            name="group1",
            label="Group 1",
            items=[q2, q3, q4]  # Add 3 questions
            logics=[
                Logic(
                    type="skip",
                    expression="${q1} = 2"  # Skip when q1 is 2
                ),
            ],
        )

        # A repeat group
        repeat_group = QuestionGroup(
            name="repeat_group",
            label="Repeating group",
            type="repeat",
            repeat_count=3,  # Repeat 3 times
            items=[q1, q2]   # Add 2 questions
        )

    """

    type: str = Field(GroupTypes.group, description="xlsform entry type")
    name: str = Field(..., description="name of the group")
    label: str = Field(..., description="label of the group")
    items: List[Union[Question, "QuestionGroup"]] = Field(
        [],
        description="group items",
    )
    logics: Optional[List[Logic]] = Field(None, description="group-level logic")
    repeat_count: Optional[Union[int, str]] = Field(
        None,
        description="number of repeats",
    )

    class Config:
        """pydantic configuration."""

        use_enum_values = True

    @root_validator(pre=False)
    def validate_repeat(cls, values):
        """Set type to repeat_count or raise ValueError."""
        group_type = values["type"]

        if not hasattr(GroupTypes, group_type):
            raise ValueError("Invalid question type")

        repeat_count = values["repeat_count"]
        if group_type == "repeat":
            if repeat_count is None:
                raise ValueError("repeat_count cannot be None when type == 'repeat'")
        else:
            if repeat_count is not None:
                values["type"] = GroupTypes.repeat
        return values


base_appearance_combos = (
    # ('hidden', 'All question types'),
    ("minimal", "select_one"),
    ("minimal", "select_multiple"),
    ("minimal", "barcode"),
    ("minimal", "begin"),
    ("minimal_compact", "begin"),
    ("compact", "select_one"),
    ("compact", "select_multiple"),
    ("compact", "begin"),
    ("horizontal", "select_one"),
    ("horizontal", "select_multiple"),
    ("horizontal_compact", "select_one"),
    ("horizontal_compact", "select_multiple"),
    ("image_map", "select_one"),
    ("image_map", "select_multiple"),
    ("autocomplete", "select_one"),
    ("likert", "select_one"),
    ("multiline", "text"),
    ("multiline", "image"),
    ("multiline", "file"),
    ("predictivetext", "text"),
    ("nopredictivetext", "text"),
    ("year", "date"),
    ("month_year", "date"),
    ("week_number", "date"),
    ("distress", "integer"),
    ("spinner", "integer"),
    ("spinner", "decimal"),
    ("numbers", "integer"),
    ("numbers", "decimal"),
    ("calculator", "integer"),
    ("calculator", "decimal"),
    ("thousands_sep", "decimal"),
    ("no_ticks", "range"),
    ("draw", "image"),
    ("annotate", "image"),
    ("signature", "image"),
    ("new_rear", "image"),
    ("new_front", "image"),
    ("field_list", "begin"),
    ("table_list", "begin"),
    ("geocode", "text"),
    ("hide_input", "geopoint"),
    ("press_to_locate", "geopoint"),
    ("press_to_locate", "geotrace"),
    ("press_to_locate", "geoshape"),
    ("spike", "image"),
    ("spike_full_measure", "image"),
    ("spike_point_to_point", "image"),
)
hidden_appearance_combos = tuple(("hidden", type.value) for type in QuestionTypes)
Appearance_Question_Combos = base_appearance_combos + hidden_appearance_combos


def check_appearance_question_combo(
    appearance_attribute: str,
    type: str,
) -> bool:
    """
    Check validity of appearance attribute for question type.

    Parameters
    ----------
    appearance_attribute : str
        The appearance attribute to check.
    type : str
        The question type to check.

    Returns
    -------
    True if the combination is valid, False otherwise.
    """
    return (appearance_attribute, type) in Appearance_Question_Combos


RESERVED_NAMES = [
    "A",
    "ABS",
    "ABSENT",
    "ACCESS",
    "ACCORDING",
    "ACCOUNT",
    "ACTIVATE",
    "ADA",
    "ADD",
    "ADMIN",
    "ADVISE",
    "AFTER",
    "ALL",
    "ALL_ROWS",
    "ALLOCATE",
    "ALLOW",
    "ALTER",
    "ANALYSE",
    "ANALYZE",
    "AND",
    "ANY",
    "ARCHIVE",
    "ARCHIVELOG",
    "ARE",
    "AREA",
    "ARRAY",
    "ARRAY_AGG",
    "ARRAY_MAX_CARDINALITY",
    "AS",
    "ASC",
    "ASENSITIVE",
    "ASSOCIATE",
    "ASUTIME",
    "ASYMMETRIC",
    "AT",
    "ATOMIC",
    "ATTRIBUTES",
    "AUDIT",
    "AUTHENTICATED",
    "AUTHORIZATION",
    "AUTOEXTEND",
    "AUTOMATIC",
    "AUX",
    "AUXILIARY",
    "AVG",
    "BACKUP",
    "BASE64",
    "BECOME",
    "BEFORE",
    "BEGIN",
    "BEGIN_FRAME",
    "BEGIN_PARTITION",
    "BERNOULLI",
    "BETWEEN",
    "BFILE",
    "BINARY",
    "BIT_LENGTH",
    "BITMAP",
    "BLOB",
    "BLOCK",
    "BLOCKED",
    "BODY",
    "BOM",
    "BOTH",
    "BREADTH",
    "BREAK",
    "BROWSE",
    "BUFFERPOOL",
    "BULK",
    "BY",
    "C",
    "CACHE",
    "CACHE_INSTANCES",
    "CALL",
    "CANCEL",
    "CAPTURE",
    "CARDINALITY",
    "CASCADE",
    "CASCADED",
    "CASE",
    "CAST",
    "CATALOG_NAME",
    "CCSID",
    "CEIL",
    "CEILING",
    "CFILE",
    "CHAINED",
    "CHANGE",
    "CHAR",
    "CHAR_CS",
    "CHAR_LENGTH",
    "CHARACTER",
    "CHARACTER_LENGTH",
    "CHARACTER_SET_CATALOG",
    "CHARACTER_SET_NAME",
    "CHARACTER_SET_SCHEMA",
    "CHARACTERS",
    "CHECK",
    "CHECKPOINT",
    "CHOOSE",
    "CHUNK",
    "CLASS_ORIGIN",
    "CLEAR",
    "CLOB",
    "CLONE",
    "CLOSE",
    "CLOSE_CACHED_OPEN_CURSORS",
    "CLUSTER",
    "CLUSTERED",
    "COALESCE",
    "COBOL",
    "COLLATE",
    "COLLATION",
    "COLLATION_CATALOG",
    "COLLATION_NAME",
    "COLLATION_SCHEMA",
    "COLLECT",
    "COLLECTION",
    "COLLID",
    "COLUMN",
    "COLUMN_NAME",
    "COLUMNS",
    "COMMAND_FUNCTION",
    "COMMAND_FUNCTION_CODE",
    "COMMENT",
    "COMMIT",
    "COMMITTED",
    "COMPATIBILITY",
    "COMPILE",
    "COMPLETE",
    "COMPOSITE_LIMIT",
    "COMPRESS",
    "COMPUTE",
    "CONCAT",
    "CONCURRENTLY",
    "CONDITION",
    "CONDITION_NUMBER",
    "CONNECT",
    "CONNECT_TIME",
    "CONNECTION",
    "CONNECTION_NAME",
    "CONSTRAINT",
    "CONSTRAINT_CATALOG",
    "CONSTRAINT_NAME",
    "CONSTRAINT_SCHEMA",
    "CONSTRAINTS",
    "CONSTRUCTOR",
    "CONTAINS",
    "CONTAINSTABLE",
    "CONTENT",
    "CONTENTS",
    "CONTINUE",
    "CONTROL",
    "CONTROLFILE",
    "CONVERT",
    "CORR",
    "CORRESPONDING",
    "COST",
    "COUNT",
    "COVAR_POP",
    "COVAR_SAMP",
    "CPU_PER_CALL",
    "CPU_PER_SESSION",
    "CREATE",
    "CREATIONDATE",
    "CREATOR",
    "CROSS",
    "CUBE",
    "CUME_DIST",
    "CURREN_USER",
    "CURRENT",
    "CURRENT_CATALOG",
    "CURRENT_CONNECTION",
    "CURRENT_DATE",
    "CURRENT_DEFAULT_TRANSFORM_GROUP",
    "CURRENT_LC_CTYPE",
    "CURRENT_PATH",
    "CURRENT_ROLE",
    "CURRENT_ROW",
    "CURRENT_SCHEMA",
    "CURRENT_TIME",
    "CURRENT_TIMESTAMP",
    "CURRENT_TRANSFORM_GROUP_FOR_TYPE",
    "CURRENT_USER",
    "CURRENT_UTCDATE",
    "CURRENT_UTCTIME",
    "CURRENT_UTCTIMESTAMP",
    "CURRVAL",
    "CURSOR",
    "CURSOR_NAME",
    "CYCLE",
    "DANGLING",
    "DATA",
    "DATABASE",
    "DATAFILE",
    "DATAFILES",
    "DATALINK",
    "DATAOBJNO",
    "DATE",
    "DATETIME_INTERVAL_CODE",
    "DATETIME_INTERVAL_PRECISION",
    "DAY",
    "DAYS",
    "DB",
    "DBA",
    "DBCC",
    "DBHIGH",
    "DBINFO",
    "DBLOW",
    "DBMAC",
    "DEALLOCATE",
    "DEBUG",
    "DEC",
    "DECIMAL",
    "DECLARE",
    "DEFAULT",
    "DEFERRABLE",
    "DEFERRED",
    "DEFINED",
    "DEGREE",
    "DELETE",
    "DENSE_RANK",
    "DENY",
    "DEPTH",
    "DEREF",
    "DERIVED",
    "DESC",
    "DESCRIBE",
    "DESCRIPTOR",
    "DETERMINISTIC",
    "DIAGNOSTICS",
    "DIRECTORY",
    "DISABLE",
    "DISALLOW",
    "DISCONNECT",
    "DISK",
    "DISMOUNT",
    "DISPATCH",
    "DISTINCT",
    "DISTRIBUTED",
    "DLNEWCOPY",
    "DLPREVIOUSCOPY",
    "DLURLCOMPLETE",
    "DLURLCOMPLETEONLY",
    "DLURLCOMPLETEWRITE",
    "DLURLPATH",
    "DLURLPATHONLY",
    "DLURLPATHWRITE",
    "DLURLSCHEME",
    "DLURLSERVER",
    "DLVALUE",
    "DML",
    "DO",
    "DOCUMENT",
    "DOUBLE",
    "DROP",
    "DSSIZE",
    "DUMP",
    "DYNAMIC",
    "DYNAMIC_FUNCTION",
    "DYNAMIC_FUNCTION_CODE",
    "EACH",
    "EDITDATE",
    "EDITOR",
    "EDITPROC",
    "ELEMENT",
    "ELSE",
    "ELSEIF",
    "ELSIF",
    "EMAXX",
    "EMAXY",
    "EMAXZ",
    "EMINX",
    "EMINY",
    "EMINZ",
    "EMPTY",
    "ENABLE",
    "ENCODING",
    "ENCRYPTION",
    "END",
    "END_FRAME",
    "END_PARTITION",
    "END-EXEC",
    "ENDING",
    "ENFORCE",
    "ENFORCED",
    "ENTITY",
    "ENTRY",
    "EQUALS",
    "ERASE",
    "ERRLVL",
    "ESCAPE",
    "EVERY",
    "EXCEPT",
    "EXCEPTION",
    "EXCEPTIONS",
    "EXCHANGE",
    "EXCLUDING",
    "EXCLUSIVE",
    "EXEC",
    "EXECUTE",
    "EXISTS",
    "EXIT",
    "EXP",
    "EXPIRE",
    "EXPLAIN",
    "EXPRESSION",
    "EXTENT",
    "EXTENTS",
    "EXTERNAL",
    "EXTERNALLY",
    "FAILED_LOGIN_ATTEMPTS",
    "FALSE",
    "FAST",
    "FENCED",
    "FETCH",
    "FID",
    "FIELDPROC",
    "FILE",
    "FILLFACTOR",
    "FILTER",
    "FINAL",
    "FIRST",
    "FIRST_ROWS",
    "FIRST_VALUE",
    "FLAG",
    "FLAGGER",
    "FLOAT",
    "FLOB",
    "FLOOR",
    "FLUSH",
    "FOR",
    "FORCE",
    "FOREIGN",
    "FORTRAN",
    "FOUND",
    "FRAME_ROW",
    "FREE",
    "FREELIST",
    "FREELISTS",
    "FREETEXT",
    "FREETEXTTABLE",
    "FREEZE",
    "FROM",
    "FS",
    "FULL",
    "FUNCTION",
    "FUSION",
    "G",
    "GENERAL",
    "GENERATED",
    "GET",
    "GLOBAL",
    "GLOBAL_NAME",
    "GLOBALID",
    "GLOBALLY",
    "GO",
    "GOTO",
    "GRANT",
    "GROUP",
    "GROUPING",
    "GROUPS",
    "HANDLER",
    "HASH",
    "HASHKEYS",
    "HAVING",
    "HEADER",
    "HEAP",
    "HEX",
    "HIERARCHY",
    "HOLD",
    "HOLDLOCK",
    "HOUR",
    "HOURS",
    "ID",
    "IDENTIFIED",
    "IDENTITY",
    "IDENTITY_INSERT",
    "IDENTITYCOL",
    "IDGENERATORS",
    "IDLE_TIME",
    "IF",
    "IGNORE",
    "ILIKE",
    "IMMEDIATE",
    "IMMEDIATELY",
    "IMPLEMENTATION",
    "IMPORT",
    "IN",
    "INCLUDING",
    "INCLUSIVE",
    "INCREMENT",
    "IND_PARTITION",
    "INDENT",
    "INDEX",
    "INDEXED",
    "INDEXES",
    "INDICATOR",
    "INHERIT",
    "INITIAL",
    "INITIALLY",
    "INITRANS",
    "INNER",
    "INOUT",
    "INSENSITIVE",
    "INSERT",
    "INSTANCE",
    "INSTANCES",
    "INSTANTIABLE",
    "INSTEAD",
    "INT",
    "INTEGER",
    "INTEGRITY",
    "INTERMEDIATE",
    "INTERSECT",
    "INTERSECTION",
    "INTO",
    "IS",
    "ISNULL",
    "ISOBID",
    "ISOLATION",
    "ISOLATION_LEVEL",
    "ITERATE",
    "JAR",
    "JOIN",
    "K",
    "KEEP",
    "KEY",
    "KEY_MEMBER",
    "KEY_TYPE",
    "KILL",
    "LABEL",
    "LAG",
    "LANGUAGE",
    "LAST",
    "LAST_VALUE",
    "LATERAL",
    "LAYER",
    "LC_CTYPE",
    "LEAD",
    "LEADING",
    "LEAVE",
    "LEFT",
    "LEN",
    "LENGTH",
    "LESS",
    "LEVEL",
    "LIBRARY",
    "LIKE",
    "LIKE_REGEX",
    "LIMIT",
    "LINENO",
    "LINK",
    "LIST",
    "LN",
    "LOAD",
    "LOB",
    "LOCAL",
    "LOCALE",
    "LOCALTIME",
    "LOCALTIMESTAMP",
    "LOCATOR",
    "LOCATORS",
    "LOCK",
    "LOCKED",
    "LOCKMAX",
    "LOCKSIZE",
    "LOG",
    "LOGFILE",
    "LOGGING",
    "LOGICAL_READS_PER_CALL",
    "LOGICAL_READS_PER_SESSION",
    "LONG",
    "LOOP",
    "LOWER",
    "M",
    "MAINTAINED",
    "MANAGE",
    "MAP",
    "MASTER",
    "MATCHED",
    "MATERIALIZED",
    "MAX",
    "MAX_CARDINALITY",
    "MAX_MEASURE",
    "MAXARCHLOGS",
    "MAXDATAFILES",
    "MAXEXTENTS",
    "MAXINSTANCES",
    "MAXLOGFILES",
    "MAXLOGHISTORY",
    "MAXLOGMEMBERS",
    "MAXSIZE",
    "MAXTRANS",
    "MAXVALUE",
    "MEMBER",
    "MERGE",
    "MESSAGE_LENGTH",
    "MESSAGE_OCTET_LENGTH",
    "MESSAGE_TEXT",
    "METHOD",
    "MICROSECOND",
    "MICROSECONDS",
    "MIN",
    "MIN_MEASURE",
    "MINEXTENTS",
    "MINIMUM",
    "MINUS",
    "MINUTE",
    "MINUTES",
    "MINVALUE",
    "MLS_LABEL_FORMAT",
    "MLSLABEL",
    "MOD",
    "MODE",
    "MODIFIES",
    "MODIFY",
    "MODULE",
    "MONTH",
    "MONTHS",
    "MORE",
    "MOUNT",
    "MOVE",
    "MTS_DISPATCHERS",
    "MULTISET",
    "MUMPS",
    "NAMESPACE",
    "NATIONAL",
    "NATURAL",
    "NCHAR",
    "NCHAR_CS",
    "NCLOB",
    "NEEDED",
    "NESTED",
    "NESTING",
    "NETWORK",
    "NEW",
    "NEXT",
    "NEXTVAL",
    "NFC",
    "NFD",
    "NFKC",
    "NFKD",
    "NIL",
    "NO",
    "NOARCHIVELOG",
    "NOAUDIT",
    "NOCACHE",
    "NOCHECK",
    "NOCOMPRESS",
    "NOCYCLE",
    "NOFORCE",
    "NOLOGGING",
    "NOMAXVALUE",
    "NOMINVALUE",
    "NONCLUSTERED",
    "NONE",
    "NOORDER",
    "NOOVERRIDE",
    "NOPARALLEL",
    "NOREVERSE",
    "NORMAL",
    "NORMALIZE",
    "NORMALIZED",
    "NOSORT",
    "NOT",
    "NOTHING",
    "NOTNULL",
    "NOWAIT",
    "NTH_VALUE",
    "NTILE",
    "NULL",
    "NULLABLE",
    "NULLIF",
    "NULLS",
    "NUMBER",
    "NUMERIC",
    "NUMOFPTS",
    "NUMPARTS",
    "NVARCHAR2",
    "OBID",
    "OBJECT",
    "OBJECTID",
    "OBJNO",
    "OBJNO_REUSE",
    "OCCURRENCES_REGEX",
    "OCTET_LENGTH",
    "OCTETS",
    "OF",
    "OFF",
    "OFFLINE",
    "OFFSET",
    "OFFSETS",
    "OID",
    "OIDINDEX",
    "OLD",
    "ON",
    "ONLINE",
    "ONLY",
    "OPCODE",
    "OPEN",
    "OPENDATASOURCE",
    "OPENQUERY",
    "OPENROWSET",
    "OPENXML",
    "OPTIMAL",
    "OPTIMIZATION",
    "OPTIMIZE",
    "OPTIMIZER_GOAL",
    "OPTION",
    "OR",
    "ORDER",
    "ORDERING",
    "ORDINALITY",
    "ORGANIZATION",
    "OSLABEL",
    "OTHERS",
    "OUT",
    "OUTER",
    "OUTPUT",
    "OVER",
    "OVERFLOW",
    "OVERLAPS",
    "OVERRIDING",
    "OWN",
    "P",
    "PACKAGE",
    "PAD",
    "PADDED",
    "PARALLEL",
    "PARAMETER",
    "PARAMETER_MODE",
    "PARAMETER_NAME",
    "PARAMETER_ORDINAL_POSITION",
    "PARAMETER_SPECIFIC_CATALOG",
    "PARAMETER_SPECIFIC_NAME",
    "PARAMETER_SPECIFIC_SCHEMA",
    "PART",
    "PARTITION",
    "PARTITIONED",
    "PARTITIONING",
    "PASCAL",
    "PASSTHROUGH",
    "PASSWORD",
    "PASSWORD_GRACE_TIME",
    "PASSWORD_LIFE_TIME",
    "PASSWORD_LOCK_TIME",
    "PASSWORD_REUSE_MAX",
    "PASSWORD_REUSE_TIME",
    "PASSWORD_VERIFY_FUNCTION",
    "PATH",
    "PCTFREE",
    "PCTINCREASE",
    "PCTTHRESHOLD",
    "PCTUSED",
    "PCTVERSION",
    "PERCENT",
    "PERCENT_RANK",
    "PERCENTILE_CONT",
    "PERCENTILE_DISC",
    "PERIOD",
    "PERMANENT",
    "PERMISSION",
    "PIECESIZE",
    "PIVOT",
    "PLACING",
    "PLAN",
    "PLI",
    "PLSQL_DEBUG",
    "POINTS",
    "PORTION",
    "POSITION_REGEX",
    "POST_TRANSACTION",
    "POWER",
    "PRECEDES",
    "PRECISION",
    "PREPARE",
    "PRESERVE",
    "PREVVAL",
    "PRIMARY",
    "PRINT",
    "PRIOR",
    "PRIQTY",
    "PRIVATE",
    "PRIVATE_SGA",
    "PRIVILEGE",
    "PRIVILEGES",
    "PROC",
    "PROCEDURE",
    "PROFILE",
    "PROGRAM",
    "PSID",
    "PUBLIC",
    "PURGE",
    "QUERY",
    "QUERYNO",
    "QUEUE",
    "QUOTA",
    "RAISERROR",
    "RANGE",
    "RANK",
    "RAW",
    "RBA",
    "READ",
    "READS",
    "READTEXT",
    "READUP",
    "REAL",
    "REBUILD",
    "RECONFIGURE",
    "RECOVER",
    "RECOVERABLE",
    "RECOVERY",
    "REF",
    "REFERENCES",
    "REFERENCING",
    "REFRESH",
    "REGR_AVGX",
    "REGR_AVGY",
    "REGR_COUNT",
    "REGR_INTERCEPT",
    "REGR_R2",
    "REGR_SLOPE",
    "REGR_SXX",
    "REGR_SXY",
    "REGR_SYY",
    "RELEASE",
    "RENAME",
    "REPEAT",
    "REPLACE",
    "REPLICATION",
    "REQUIRING",
    "RESET",
    "RESETLOGS",
    "RESIGNAL",
    "RESIZE",
    "RESOURCE",
    "RESPECT",
    "RESTORE",
    "RESTRICT",
    "RESTRICTED",
    "RESULT",
    "RESULT_SET_LOCATOR",
    "RETURN",
    "RETURNED_CARDINALITY",
    "RETURNED_LENGTH",
    "RETURNED_OCTET_LENGTH",
    "RETURNED_SQLSTATE",
    "RETURNING",
    "RETURNS",
    "REUSE",
    "REVERSE",
    "REVERT",
    "REVOKE",
    "RIGHT",
    "ROLE",
    "ROLES",
    "ROLLBACK",
    "ROLLUP",
    "ROUND_CEILING",
    "ROUND_DOWN",
    "ROUND_FLOOR",
    "ROUND_HALF_DOWN",
    "ROUND_HALF_EVEN",
    "ROUND_HALF_UP",
    "ROUND_UP",
    "ROUTINE",
    "ROUTINE_CATALOG",
    "ROUTINE_NAME",
    "ROUTINE_SCHEMA",
    "ROW",
    "ROW_COUNT",
    "ROW_NUMBER",
    "ROWCOUNT",
    "ROWGUIDCOL",
    "ROWID",
    "ROWNUM",
    "ROWS",
    "ROWSET",
    "RULE",
    "RUN",
    "SAMPLE",
    "SAVE",
    "SAVEPOINT",
    "SB4",
    "SCALE",
    "SCAN_INSTANCES",
    "SCHEMA",
    "SCHEMA_NAME",
    "SCN",
    "SCOPE",
    "SCOPE_CATALOG",
    "SCOPE_NAME",
    "SCOPE_SCHEMA",
    "SCRATCHPAD",
    "SD_ALL",
    "SD_INHIBIT",
    "SD_SHOW",
    "SECOND",
    "SECONDS",
    "SECQTY",
    "SECTION",
    "SECURITY",
    "SECURITYAUDIT",
    "SEG_BLOCK",
    "SEG_FILE",
    "SEGMENT",
    "SELECT",
    "SELECTIVE",
    "SELF",
    "SEMANTICKEYPHRASETABLE",
    "SEMANTICSIMILARITYDETAILSTABLE",
    "SEMANTICSIMILARITYTABLE",
    "SENSITIVE",
    "SEQUENCE",
    "SERIALIZABLE",
    "SERVER_NAME",
    "SESSION",
    "SESSION_CACHED_CURSORS",
    "SESSION_USER",
    "SESSIONS_PER_USER",
    "SET",
    "SETS",
    "SETUSER",
    "SHAPE",
    "SHARE",
    "SHARED",
    "SHARED_POOL",
    "SHRINK",
    "SHUTDOWN",
    "SIGNAL",
    "SIMILAR",
    "SIMPLE",
    "SIZE",
    "SKIP",
    "SKIP_UNUSABLE_INDEXES",
    "SMALLINT",
    "SNAPSHOT",
    "SOME",
    "SORT",
    "SOURCE",
    "SPACE",
    "SPECIFIC",
    "SPECIFIC_NAME",
    "SPECIFICATION",
    "SPECIFICTYPE",
    "SPLIT",
    "SQL",
    "SQL_TRACE",
    "SQLCODE",
    "SQLERROR",
    "SQLEXCEPTION",
    "SQLSTATE",
    "SQLWARNING",
    "SQRT",
    "STANDARD",
    "STANDBY",
    "START",
    "STATE",
    "STATEMENT",
    "STATEMENT_ID",
    "STATIC",
    "STATISTICS",
    "STAY",
    "STDDEV_POP",
    "STDDEV_SAMP",
    "STOGROUP",
    "STOP",
    "STORAGE",
    "STORE",
    "STORES",
    "STRUCTURE",
    "STYLE",
    "SUBCLASS_ORIGIN",
    "SUBMULTISET",
    "SUBSTRING_REGEX",
    "SUCCEEDS",
    "SUCCESSFUL",
    "SUM",
    "SUMMARY",
    "SWITCH",
    "SYMMETRIC",
    "SYNONYM",
    "SYS_OP_ENFORCE_NOT_NULL$",
    "SYS_OP_NTCIMG$",
    "SYSDATE",
    "SYSDBA",
    "SYSOPER",
    "SYSTEM",
    "SYSTEM_TIME",
    "SYSTEM_USER",
    "SYSTIME",
    "SYSTIMESTAMP",
    "SYSUUID",
    "T",
    "TABLE",
    "TABLE_NAME",
    "TABLES",
    "TABLESAMPLE",
    "TABLESPACE",
    "TABLESPACE_NO",
    "TABNO",
    "TEMPORARY",
    "TEXTSIZE",
    "THAN",
    "THE",
    "THEN",
    "THREAD",
    "TIES",
    "TIME",
    "TIMESTAMP",
    "TIMEZONE_HOUR",
    "TIMEZONE_MINUTE",
    "TO",
    "TOKEN",
    "TOP",
    "TOP_LEVEL_COUNT",
    "TOPLEVEL",
    "TRACE",
    "TRACING",
    "TRAILING",
    "TRAN",
    "TRANSACTION",
    "TRANSACTION_ACTIVE",
    "TRANSACTIONS_COMMITTED",
    "TRANSACTIONS_ROLLED_BACK",
    "TRANSFORM",
    "TRANSFORMS",
    "TRANSITIONAL",
    "TRANSLATE",
    "TRANSLATE_REGEX",
    "TRANSLATION",
    "TRIGGER",
    "TRIGGER_CATALOG",
    "TRIGGER_NAME",
    "TRIGGER_SCHEMA",
    "TRIGGERS",
    "TRIM_ARRAY",
    "TRUE",
    "TRUNCATE",
    "TRY_CONVERT",
    "TSEQUAL",
    "TX",
    "TYPE",
    "UB2",
    "UBA",
    "UESCAPE",
    "UID",
    "UNARCHIVED",
    "UNDER",
    "UNDO",
    "UNION",
    "UNIQUE",
    "UNLIMITED",
    "UNLINK",
    "UNLOCK",
    "UNNAMED",
    "UNNEST",
    "UNPIVOT",
    "UNRECOVERABLE",
    "UNTIL",
    "UNTYPED",
    "UNUSABLE",
    "UNUSED",
    "UPDATABLE",
    "UPDATE",
    "UPDATETEXT",
    "UPPER",
    "URI",
    "USAGE",
    "USE",
    "USER",
    "USER_DEFINED_TYPE_CATALOG",
    "USER_DEFINED_TYPE_CODE",
    "USER_DEFINED_TYPE_NAME",
    "USER_DEFINED_TYPE_SCHEMA",
    "USING",
    "UTCDATE",
    "UTCTIME",
    "UTCTIMESTAMP",
    "VALIDATE",
    "VALIDATION",
    "VALIDPROC",
    "VALUE",
    "VALUE_OF",
    "VALUES",
    "VAR_POP",
    "VAR_SAMP",
    "VARBINARY",
    "VARCHAR",
    "VARCHAR2",
    "VARIABLE",
    "VARIADIC",
    "VARIANT",
    "VARYING",
    "VCAT",
    "VERBOSE",
    "VERSIONING",
    "VIEW",
    "VOLATILE",
    "VOLUMES",
    "WAITFOR",
    "WHEN",
    "WHENEVER",
    "WHERE",
    "WHILE",
    "WIDTH_BUCKET",
    "WINDOW",
    "WITH",
    "WITHIN",
    "WITHIN GROUP",
    "WITHOUT",
    "WLM",
    "WORK",
    "WRITE",
    "WRITEDOWN",
    "WRITETEXT",
    "WRITEUP",
    "XID",
    "XMLAGG",
    "XMLBINARY",
    "XMLCAST",
    "XMLCOMMENT",
    "XMLDECLARATION",
    "XMLDOCUMENT",
    "XMLEXISTS",
    "XMLITERATE",
    "XMLNAMESPACES",
    "XMLQUERY",
    "XMLSCHEMA",
    "XMLTABLE",
    "XMLTEXT",
    "XMLVALIDATE",
    "YEAR",
    "YEARS",
    "ZONE",
]


def items_to_dfs(
    items: List[Union[QuestionGroup, Question]],
) -> Dict[str, pd.DataFrame]:
    """
    Convert a list of Questions and QuestionGroups into two DataFrames.

    One DataFrame will contain the survey structure information,
    while the other will contain information on
    the choices available for multiple choice questions.

    Parameters
    ----------
    items : List[Union[group_classes + question_classes]]
        A list of Questions and/or QuestionGroups,
        or their derivatives such as MultipleChoiceQuestions and RepeatGroups,
        to be converted to DataFrames.

    Returns
    -------
    A dictionary containing a survey df and a choices df.
    """
    survey_rows = []
    choices_rows = []
    if items is None:
        raise ValueError("items_to_df found no items")
    for item in items:
        item_dict = item.dict()
        type = item_dict["type"]

        if type in ("repeat", "group"):
            del item_dict["items"]
            item_dict.update({"type": f"begin {type}"})
            survey_rows.append(item_dict)
            _dfs = items_to_dfs(item.items)
            survey_rows += _dfs["survey"].to_dict("records")
            choices_rows += _dfs["choices"].to_dict("records")
            item_dict.update({"type": f"end {type}"})
            survey_rows.append(item_dict)

        elif type in ("rank", "select_one", "select_multiple"):
            list_name = item.name
            del item_dict["choices"]
            item_dict.update({"type": f"{type} {list_name}"})
            survey_rows.append(item_dict)
            if item.choices is not None:
                choices_rows += [
                    {
                        "list_name": list_name,
                        "name": choice.value,
                        "label": choice.label,
                    }
                    for choice in item.choices
                ]

        else:
            survey_rows.append(item_dict)

    survey_df = pd.DataFrame(survey_rows)
    choices_df = pd.DataFrame(choices_rows)

    return {"survey": survey_df, "choices": choices_df}


def prep_for_excel(df: pd.DataFrame) -> pd.DataFrame:
    """Perform transformations on data as needed for XLSForm parsing."""
    return (
        df.fillna("")
        .astype(str)
        .replace({"[]": "", "{}": ""}, regex=False)
        .replace({"": None, True: "yes", False: "no"}, regex=False)
        .dropna(axis=1, how="all")
    )


def get_survey_args(excel_filepath: str) -> dict:
    """Return Survey-parseable dict from Excel file."""

    def link_choices(survey_row: dict, choice_dict: Dict[str, List[Choice]]) -> dict:
        """Link choices to questions."""
        type = survey_row["type"]
        type_with_choices = any(
            type.startswith(s)
            for s in (
                "rank",
                "select_one",
                "select_multiple",
            )
        )
        not_from_file = "from_file" not in type
        if type_with_choices and not_from_file:
            type_root, group_name = type.split()
            survey_row["type"] = type_root
            survey_row["choices"] = choice_dict.get(group_name, [])
        return survey_row

    def group_items(rows: Iterable[dict]):
        """Group items as appropriate, or not."""
        groups = []
        current_group = None
        for row in rows:
            type = row["type"]
            if type.startswith("begin"):
                group_type = type[6:]
                group_name = row["name"]
                current_group = QuestionGroup(
                    name=group_name,
                    type=group_type,
                    label=row.get("label", None),
                    items=[],
                )
                groups.append(current_group)
            elif type.startswith("end") and current_group is not None:
                current_group = None
            else:
                if current_group is not None:
                    current_group.items.append(Question.parse_obj(row))
                else:
                    groups.append(Question.parse_obj(row))
        return groups

    def drop_nan_dict(df: pd.DataFrame) -> List[dict]:
        """Return list of dicts with no nans."""
        return [
            {
                k: v
                for k, v in _dict.items()
                if not (isinstance(v, float) and pd.isna(v))
            }
            for _dict in (
                df.dropna(axis=0, how="all")
                .dropna(axis=1, how="all")
                .to_dict("records")
            )
        ]

    def get_choice_dict(choices_df: pd.DataFrame) -> Dict[str, List[Choice]]:
        """Return list_name: List[Choice] dict from choices_df."""
        return {
            list_name: [
                Choice.parse_obj(d)
                for d in drop_nan_dict(df.drop(columns=["list_name"]))
            ]
            for list_name, df in (
                choices_df.rename(columns={"name": "value"}).groupby(
                    "list_name",
                    as_index=False,
                )
            )
        }

    with pd.ExcelFile(excel_filepath) as xls:
        survey_df, choices_df, settings_df = (
            pd.read_excel(xls, sheet_name=sheet_name)
            for sheet_name in ("survey", "choices", "settings")
        )

    choice_dict: Dict[str, List[Choice]] = get_choice_dict(choices_df)
    items_grouped = group_items(
        link_choices(d, choice_dict) for d in drop_nan_dict(survey_df)
    )

    settings_dict = settings_df.iloc[0].to_dict()
    settings_dict.update(
        {
            "name": settings_dict["form_id"],
            "label": settings_dict["form_title"],
            "items": items_grouped,
        },
    )

    return settings_dict


class Survey(BaseModel):
    """
    A Pydantic model representing an XLSForm survey.

    Notes
    -----
    The `name` and `label` fields set the name and label of the survey.

    The `items` field contains the questions and question groups that make up
    the survey.

    Examples
    --------
    .. code-block:: python

        survey = Survey(
            name="example_survey",
            label="Example Survey",
            items=[
                # Add a question group
                QuestionGroup(
                    name="group1",
                    label="Question Group 1",
                    items=[
                        # Add a text question
                        Question(
                            name="q1",
                            label="What is your name?",
                            type="text"
                        )
                    ]
                )
            ]
        )

        # Export to Excel
        survey.save_to_excel("my_survey.xls")

    """

    name: str = Field(..., description="name of the survey")
    label: str = Field(..., description="label of the survey")
    items: List[Union[Question, QuestionGroup]] = Field(
        [],
        description="the survey's items",
    )

    def get_dfs(self) -> Dict[str, pd.DataFrame]:
        """Return sheet_name: df dict for survey data."""
        settings_df = pd.DataFrame([{"form_id": self.name, "form_title": self.label}])
        df_dict = items_to_dfs(self.items)
        df_dict.update({"settings": settings_df})
        df_dict = {sheet_name: prep_for_excel(df) for sheet_name, df in df_dict.items()}
        return df_dict

    def save_to_excel(self, excel_filepath: str) -> None:
        """
        Save the survey data to an Excel file at the specified file path.

        Parameters
        ----------
        excel_filepath : str
            The path of the Excel file to save the survey data to.

        Returns
        -------
        None
        """
        with pd.ExcelWriter(excel_filepath) as writer:
            for sheet_name, df in self.get_dfs().items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

    @classmethod
    def parse_excel(cls, excel_filepath: str) -> "Survey":
        """
        Return Survey object based on Excel file.

        Parameters
        ----------
        excel_filepath : str
            The path of the Excel file to read the survey data from.

        Returns
        -------
        A Survey object.
        """
        survey_args = get_survey_args(excel_filepath)
        return cls.parse_obj(survey_args)

    def yaml(self) -> str:
        """Return yaml representation of self as str. Similar to Survey.json."""
        return yaml.dump(
            self.dict(exclude_none=True),
            default_flow_style=False,
            sort_keys=False,
        )

    @classmethod
    def parse_yaml(cls, yaml_str: str) -> "Survey":
        """Return Survey object given yaml str. Similar to Survey.parse_raw."""
        return cls(**yaml.safe_load(yaml_str))

    def save_to_yaml(self, yaml_filepath: str) -> None:
        """Save yaml representation of self to file."""
        with open(yaml_filepath, "w") as out_file:
            out_file.write(self.yaml())

    @classmethod
    def parse_yaml_file(cls, yaml_filepath: str) -> "Survey":
        """Return Survey object given yaml filepath."""
        with open(yaml_filepath) as in_file:
            yaml_str = in_file.read()
        return cls.parse_yaml(yaml_str)
