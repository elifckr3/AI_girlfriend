from src.agent.capability import Capability
import logging
from datetime import datetime

class CalendarCapability(Capability):
    user_history: list[str] = [] # By specifying list[str] as the type for user_history, you provide Pydantic with concrete information about the expected structure
    
    @classmethod
    def register_capability(cls):
        return cls(unique_name="calendar", hotwords=["open calendar"])
    

    def get_current_date(self):
        formatted_date = datetime.now().strftime("%B %d, %Y")
        return f"Current date is {formatted_date}"

    def get_current_month(self):
        month = datetime.now().strftime("%B") 
        return f"Current month is {month}"
    
    def get_current_day(self):
        day = datetime.now().strftime("%A") 
        return f"Current day is {day}"
    
    def get_current_year(self):
        year = datetime.now().strftime("%Y") 
        return f"Current year is {year}"
    
    def get_history(self):
        return self.user_history

    def call(self, agent):
        initial_message = "Opened Calendar! To exit calendar simply say 'exit' or 'get history' to check capability history,\
              What would you like to inquire about calendar ?"
        agent.speak(response=initial_message)

        while True:
            user_inquiry = agent.listen()
            logging.info(user_inquiry)
            
            if "current date" in user_inquiry:
                answer = self.get_current_date()

            elif "current day" in user_inquiry:
                answer = self.get_current_day()

            elif "current month" in user_inquiry:
                answer = self.get_current_month()

            elif "current year" in user_inquiry:
                answer = self.get_current_year()
            
            elif "get history" in user_inquiry:
                history = self.get_history()
                answer = "Getting history of capability: "
                answer += "\n".join(history) if history else "No conversation history available."
                
            elif "exit" in user_inquiry:
                break
            else:
                answer = "Sorry I couldn't understand"

            # Store user inquiry and response in history
            self.user_history.append("Question: %s"%user_inquiry)
            self.user_history.append("Answer: %s"%answer)

            logging.info(answer)
            answer += ", anything else ?"
            agent.speak(response=answer)


        message = "Exiting Calendar"
        logging.debug(message)
        return message