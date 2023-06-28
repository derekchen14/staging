from faker import Faker
fake = Faker()

message_list = [{"user": "Hello Smartbot!", "bot": "Hello, Cece :)"}]

def get_chat():
    return message_list

def add_chat(user_message: str):
    long_message = fake.text()
    bot_message = long_message.split("\n")[0]
    if len(bot_message) > 80:
        tokens = bot_message.split()
        # Break at the end of the first sentence which is defined by period and a space.
        break_idx = bot_message.find(". ") + 1
        bot_message = bot_message[:break_idx]
    message_list.append({"user": user_message, "bot": bot_message})
