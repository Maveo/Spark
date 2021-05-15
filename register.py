import requests
from settings import APPLICATION_ID, TOKEN


url = "https://discord.com/api/v8/applications/{}/commands".format(APPLICATION_ID)
command_url = url + '/{}'

json = {
    # "name": "blep",
    # "description": "Send a random adorable animal photo",
    # "options": [
    #     {
    #         "name": "animal",
    #         "description": "The type of animal",
    #         "type": 3,
    #         "required": True,
    #         "choices": [
    #             {
    #                 "name": "Dog",
    #                 "value": "animal_dog"
    #             },
    #             {
    #                 "name": "Cat",
    #                 "value": "animal_cat"
    #             },
    #             {
    #                 "name": "Penguin",
    #                 "value": "animal_penguin"
    #             }
    #         ]
    #     },
    #     {
    #         "name": "only_smol",
    #         "description": "Whether to show only baby animals",
    #         "type": 5,
    #         "required": False
    #     }
    # ]
}

# For authorization, you can use either your bot token
headers = {
    "Authorization": "Bot {}".format(TOKEN)
}

r = requests.get(url, headers=headers)
print(r.text)
# r = requests.delete(command_url.format('843123732003684373'), headers=headers)
# print(r.text)
# r = requests.post(url, headers=headers, json=json)
# print(r.text)
