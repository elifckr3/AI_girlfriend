from pydantic import BaseModel, model_serializer
from enum import Enum


class RoleTypes(Enum):
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"


class Message(BaseModel):
    role: RoleTypes

    content: str

    @model_serializer
    def serialize_to_gpt3(self):
        return {
            "role": self.role.value,
            "content": self.content,
        }


# NOTE grouping interactions not necessary imo atm
# class Interaction(BaseModel):
#     user_message: str

#     system_prompt: str

#     assistant_response: str

#     @model_serializer
#     def serialize_to_gpt3(self):
#         return {
#             "user_prompt": self.user_prompt,
#             "agent_resp": self.agent_resp,
#         }

# {"role": "system", "content": chatbot}
