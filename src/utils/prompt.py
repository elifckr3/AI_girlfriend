import typing
import enum
from abc import ABC, abstractmethod
from typing import Any, TypeVar, cast

import numpy as np
import questionary
import typer
from prompt_toolkit.input import Input
from prompt_toolkit.output import DummyOutput
from pydantic import BaseModel, ConfigDict
from pydantic.fields import FieldInfo

from prompt_toolkit.validation import ValidationError, Validator

ModelT = TypeVar("ModelT", bound=BaseModel)

CUSTOM_STYLE = questionary.Style(
    [
        ("qmark", "fg:#673ab7 bold"),  # token in front of the question
        ("question", "bold"),  # question text
        ("answer", "fg:#f44336 bold"),  # submitted answer text behind the question
        ("pointer", "fg:#673ab7 bold"),  # pointer used in select and checkbox prompts
        (
            "highlighted",
            "fg:#673ab7 bold",
        ),  # pointed-at choice in select and checkbox prompts
        ("selected", "fg:#cc5454"),  # style for a selected item of a checkbox
        ("separator", "fg:#cc5454"),  # separator in lists
        ("instruction", ""),  # user instructions for select, rawselect, checkbox
        ("text", ""),  # plain text
        (
            "disabled",
            "fg:#858585 italic",
        ),  # disabled choices for select and checkbox prompts
    ],
)


class QTypes(enum.Enum):
    CONFIRM = "confirm"

    SELECT = "select"

    CHECK = "checkbox"

    AUTOCOMP = "autocomplete"

    TEXT = "text"

    PASSWORD = "password"
    # Internally handled as text with filters back to numeric
    FLOAT = "float"

    INT = "int"


class Question(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    qtype: QTypes

    # question identifier useful for conditional logic
    name: str

    # question text
    message: str

    # allow multiline text input
    multiline: bool = False

    # default value, if not provided empty return not allowed
    default: str | int | float | bool | enum.EnumMeta | None = None

    # choices for select, checkbox, autocomplete
    choices: list[Any] = []

    # enum struct for select, checkbox, autocomplete
    enum_struct: enum.EnumMeta | None = None

    # conditional logic
    when: typing.Callable | None = None

    style: questionary.Style | None = None

    # most of these are autohandled
    validation: Validator | typing.Callable | None = None

    # adjust the value of the result
    filter_func: typing.Callable | None = None


class Prompt(BaseModel, ABC):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # testing usage
    # from prompt_toolkit.input import create_pipe_input
    # with create_pipe_input() as inp:
    test_input: Input | None = None

    test_output: DummyOutput = DummyOutput()

    def __init__(self, **data):
        super().__init__(**data)

    @abstractmethod
    def run(self) -> Any:
        raise NotImplementedError

    def prompt(
        self,
        qs: list[Question],
    ) -> dict[str, Any]:
        assert len(qs) == len({q.name for q in qs}), "duplicate question names"

        input: list[dict[str, Any]] = []

        for q in qs:
            q_dict: dict[str, Any] = {}

            q_dict["type"] = q.qtype.value

            q_dict["name"] = q.name

            q_dict["message"] = q.message

            empty_allowed = False

            if q.choices != [] and q.qtype in [
                QTypes.SELECT,
                QTypes.CHECK,
                QTypes.AUTOCOMP,
            ]:
                q_dict["choices"] = q.choices

            if q.when is not None:
                q_dict["when"] = q.when

            if q.validation is not None:
                q_dict["validate"] = q.validation

            if q.filter_func is not None:
                q_dict["filter"] = q.filter_func

            if q.enum_struct is not None:
                assert q.qtype in [QTypes.SELECT, QTypes.CHECK, QTypes.AUTOCOMP]

                if q.default is not None:
                    q_dict["default"] = (
                        q.default.value
                        if isinstance(q.default, enum.Enum)
                        else q.default
                    )

                    empty_allowed = True

                q_dict["choices"] = [  # type: ignore
                    str(e.value) for e in q.enum_struct.__members__.values()
                ]

                value_to_enum = {e.value: e for e in q.enum_struct}  # type: ignore

                q_dict["filter"] = lambda val, vte=value_to_enum: (
                    [vte.get(v) for v in val]
                    if isinstance(val, list | tuple)
                    else vte.get(val)
                )

            if q.qtype is QTypes.CONFIRM or q.qtype is QTypes.TEXT:
                if q.default is not None:
                    q_dict["default"] = q.default

                    empty_allowed = True

            if q.qtype is QTypes.TEXT:
                q_dict["validate"] = StringValidator(empty_allowed=empty_allowed)
                if q.multiline is not False:
                    q_dict["multiline"] = q.multiline
                    q_dict["instruction"] = "  (press [Esc] [Enter] to submit)  \n"

            if q.qtype is QTypes.FLOAT or q.qtype is QTypes.INT:
                q_dict["type"] = "text"
                if q.default is not None:
                    q_dict["default"] = str(q.default)

                    empty_allowed = True

                if q.choices != []:
                    q_dict["type"] = "autocomplete"

                    q_dict["choices"] = [str(e) for e in q.choices]

                    q_dict["validate"] = NumberValidator(
                        empty_allowed=empty_allowed,
                        choices=q_dict["choices"],
                    )

                    q_dict["filter"] = (
                        lambda res, q=q, q_dict=q_dict: clean_numeric_result(
                            result=res,
                            dtype="int" if q.qtype is QTypes.INT else "float",
                            choices=q_dict["choices"],
                            default=q.default,
                        )
                    )

                else:
                    q_dict["validate"] = NumberValidator(empty_allowed=empty_allowed)

                    q_dict["filter"] = lambda res, q=q: clean_numeric_result(
                        result=res,
                        dtype="int" if q.qtype is QTypes.INT else "float",
                        default=q.default,
                    )

            q_dict["style"] = q.style if q.style is not None else CUSTOM_STYLE

            input.append(q_dict)

        if self.test_input is not None:
            return questionary.prompt(
                input,
                input=self.test_input,
                output=self.test_output,
            )

        return questionary.prompt(input)

    def prompt_fields(
        self,
        model: type[ModelT] | ModelT,
        skip_attrs: list[str] = [],
        attr_paths: dict[str, typing.Callable] = {},
        set_attrs: dict[str, Any] = {},
        checkboxed_enums: list[str] = [],
        shell_echo: str = "",
    ) -> ModelT:
        if shell_echo != "":
            typer.secho(shell_echo, fg="green")
        # assert all skip_attrs are in model fields
        for a in skip_attrs:
            assert a in model.model_fields.keys()

        # assert all paths are in model fields
        for attr_name, _ in attr_paths.items():
            assert attr_name in model.model_fields.keys()

        # base fields to prompt
        base_fields = {
            f: v for f, v in model.model_fields.items() if f not in skip_attrs
        }

        # prompt base fields
        questions = []
        for field_name, field in base_fields.items():
            qs: dict[str, Any] = {
                "name": field_name,
                "message": field_name,
            }
            if hasattr(field, "default"):
                qs["default"] = field.default

            if field.annotation == bool:
                qs["qtype"] = QTypes.CONFIRM

            elif field.annotation == int or field.annotation == float:
                qs["qtype"] = QTypes.INT if field.annotation == int else QTypes.FLOAT

                bounds = {}
                for meta in field.metadata:
                    for key, value in field.metadata_lookup.items():
                        if value == type(meta):
                            bounds[key] = getattr(meta, key)

                if len(bounds.keys()) > 1:
                    qs["choices"] = create_number_choices(field=field, bounds=bounds)

            elif isinstance(field.annotation, enum.EnumMeta):
                if field_name in checkboxed_enums:
                    qs["qtype"] = QTypes.CHECK
                else:
                    qs["qtype"] = QTypes.SELECT

                qs["enum_struct"] = field.annotation

            elif field.annotation == str:
                qs["qtype"] = QTypes.TEXT

            if field_name in attr_paths:
                qs["when"] = attr_paths[field_name]

            questions.append(Question(**qs))

        results: dict[str, Any] = self.prompt(questions)

        # manually set attrs previous prompt block
        for field_name, field in set_attrs.items():
            results[field_name] = field

        if isinstance(model, BaseModel):
            original_data = model.model_dump()
            original_data.update(results)
            return cast(ModelT, model.__class__(**original_data))

        return model(**results)


def max_decimal_places(*args):
    """Returns the maximum number of decimal places in the provided float arguments."""
    return max(len(str(arg).split(".")[-1]) for arg in args if isinstance(arg, float))


def adjust_float(value, precision, add_value):
    """Adjusts a float value by a small increment or decrement based on precision."""
    adjustment = 1 / (10**precision)
    return value + adjustment if add_value else value - adjustment


def contains_non_numbers(lst: list[str]):
    for item in lst:
        try:
            float(item)

        except ValueError:
            return True

    return False


def clean_max_min(
    choices: list[str],
    default: int | float,
    lt: int | float,
    gt: int | float,
) -> list[str]:
    if isinstance(default, int):
        if lt is not None:
            up = int(choices[-1])
            up -= 1
            choices[-1] = str(up)

        if gt is not None:
            low = int(choices[1])
            low += 1
            choices[1] = str(low)

    elif isinstance(default, float):
        precision = max_decimal_places(default, lt, gt)

        if lt is not None:
            up_f = float(choices[-1])
            up_f = adjust_float(up_f, precision, False)
            choices[-1] = f"{up_f:.{precision}f}"

        if gt is not None:
            low_f = float(choices[1])
            up_f = adjust_float(low_f, precision, True)
            choices[1] = f"{low_f:.{precision}f}"

    choices[1] = "Min: " + choices[1]
    choices[-1] = "Max: " + choices[-1]

    return choices


def generate_number_choices(
    default: int | float,
    lower: int | float,
    upper: int | float,
) -> list[str]:
    choices: list[Any] = []

    if isinstance(default, int):
        step = 1
        diff = abs(upper - lower)

        if diff > 100:
            step = 10

        elif diff > 1000:
            step = 100

        elif diff > 10000:
            step = 1000

        if diff > 100000:
            choices.extend([lower, upper])

        else:
            current = lower

            while current <= upper:
                choices.append(str(current))
                current += step

    elif isinstance(default, float):
        num_choices = 10
        precision = max_decimal_places(default, lower, upper)

        choices = list(np.linspace(lower, upper, num_choices))
        choices = [f"{choice:.{precision}f}" for choice in choices]

    return [str(choice) for choice in choices]


def create_number_choices(
    field: FieldInfo,
    bounds: dict[str, int | float],
) -> list[str]:
    default = field.default
    bounds_avail = list(bounds.keys())
    choices = ["Default: " + str(default)]
    upper = None
    lower = None

    if "lt" in bounds_avail or "le" in bounds_avail:
        upper = bounds["lt"] if "lt" in bounds_avail else bounds["le"]

    if "gt" in bounds_avail or "ge" in bounds_avail:
        lower = bounds["gt"] if "gt" in bounds_avail else bounds["ge"]

    if upper is not None and lower is not None:
        choices.extend(
            generate_number_choices(
                default=default,
                lower=lower,
                upper=upper,
            ),
        )

        if "lt" in bounds_avail and "gt" in bounds_avail:
            choices = clean_max_min(
                choices=choices,
                default=default,
                lt=upper,
                gt=lower,
            )
        else:
            choices[1] = "Min: " + choices[1]
            choices[-1] = "Max: " + choices[-1]

    return choices


def clean_numeric_result(
    result: str,
    dtype: typing.Literal["int", "float"],
    choices: list[str] = [],
    default: int | float | None = None,
) -> int | float:
    output: int | float | str = result

    if result == "Default: " + str(default):
        assert isinstance(default, float | int)
        output = default

    if len(choices) >= 3:
        if result == str(choices[1]):
            output = choices[1][4:]

        elif result == str(choices[-1]):
            output = choices[-1][4:]

    output = int(output) if dtype == "int" else float(output)

    return output


class StringValidator(Validator, BaseModel):
    empty_allowed: bool = False

    def validate(self, document):
        text = document.text

        if len(text) == 0 and self.empty_allowed:
            raise ValidationError(
                message="Please enter a value",
                cursor_position=len(document.text),
            )


class NumberValidator(Validator, BaseModel):
    empty_allowed: bool = False
    choices: list[str] = []

    def validate(self, document):
        text = document.text

        if len(text) == 0 and not self.empty_allowed:
            raise ValidationError(
                message="Please enter a value",
                cursor_position=len(document.text),
            )

        max_val: int | float | None = None
        min_val: int | float | None = None
        if len(self.choices) >= 2:
            try:
                max_val = int(self.choices[-1])
                min_val = int(self.choices[0])
            except ValueError:
                try:
                    max_val = float(self.choices[-1])
                    min_val = float(self.choices[0])
                except ValueError:
                    pass

        range_text_error = f"Input must be between {min_val} and {max_val}"
        if text:
            if "Default: " in text or "Min: " in text or "Max: " in text:
                return
            elif text in self.choices:
                return
            elif text.isdigit():
                if max_val is None and min_val is None:
                    return
                if (
                    max_val is not None
                    and min_val is not None
                    and isinstance(max_val, int)
                    and isinstance(min_val, int)
                ):
                    if int(text) in range(min_val, max_val):
                        return
                    else:
                        raise ValidationError(
                            message=range_text_error,
                            cursor_position=0,
                        )
                else:
                    raise ValidationError(message=range_text_error, cursor_position=0)
            elif "." in text:
                try:
                    val = float(text)
                    if max_val is None and min_val is None:
                        return
                    if (
                        max_val is not None
                        and min_val is not None
                        and isinstance(max_val, float)
                        and isinstance(min_val, float)
                    ):
                        if min_val <= val <= max_val:
                            return
                        else:
                            raise ValidationError(
                                message=range_text_error,
                                cursor_position=0,
                            )
                except ValueError:
                    raise ValidationError(
                        message="Not a float",
                        cursor_position=0,
                    ) from None
            else:
                raise ValidationError(
                    message="This input contains non-numeric characters",
                    cursor_position=0,
                )
        return
