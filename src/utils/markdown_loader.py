# from string import Template
from jinja2 import Template
from typing import Any


def prompt_loader(file_path: str, variables: dict[str, Any] = {}) -> str:
    with open(file_path) as file:
        template_content = file.read()

    template = Template(template_content)
    return template.render(**variables)

    # placeholders = set(re.findall(r"\{\{ (\w+) \}\}", template_content))
    # # placeholders = set(re.findall(r"\$\{(\w+)\}", template_content))

    # if placeholders != set(variables.keys()):
    #     missing = placeholders - set(variables.keys())

    #     extra = set(variables.keys()) - placeholders

    #     raise ValueError(
    #         f"File {file_path}'s placeholders dont match variables - Missing: {missing} Extra: {extra}"
    #     )

    # return Template(template_content).substitute(**variables)
