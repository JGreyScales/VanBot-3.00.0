from datetime import datetime
from urllib import response
from disnake import TextInputStyle
import json, disnake


class utilScripts:
    def __init__(self) -> None:
        pass

    def log(message):
        print(str(datetime.now()) + ":\t" + message)

    def cacheChanges(configJson = "", storageJson = ""):
        if configJson != "": 
            with open("config.json", "w") as CONFIGFILE: json.dump(configJson, CONFIGFILE)
        if storageJson != "":
            with open("vans.json", "w") as STORAGEFILE: json.dump(storageJson, STORAGEFILE)

# Subclassing the modal.
class feedbackForm(disnake.ui.Modal):
    def __init__(self):
        components = [
            disnake.ui.TextInput(
                label="Name",
                placeholder="Username",
                custom_id="name",
                style=TextInputStyle.short,
                max_length=32,
                min_length=1
            ),
            disnake.ui.TextInput(
                label="Description",
                placeholder="Response form",
                custom_id="description",
                style=TextInputStyle.paragraph,
                min_length=5
            ),
        ]
        super().__init__(
            title="Create Tag",
            custom_id="create_tag",
            components=components,
        )
        utilScripts.log("Modal created")

    # The callback received when the user input is completed.
    async def callback(self, inter: disnake.ModalInteraction):
        
        for item in inter.text_values.items(): 
            if item[0] == "name": key = item[1]
            else: value = item[1]
        utilScripts.log("User response gathered")
        with open("userResponseLogs/Responses.txt", "r") as RESPONSEFILE: responses = RESPONSEFILE.read()
        utilScripts.log("Responses read")
        responses += f"{key}:{value}\n"
        with open("userResponseLogs/Responses.txt", "w") as RESPONSEFILE: RESPONSEFILE.write(responses)
        utilScripts.log("Reponse saved")
        await inter.response.send_message("Feedback has been gathered", ephemeral=True)
        utilScripts.log("Response message sent")