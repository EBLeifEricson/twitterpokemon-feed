import twitter
import requests
from datetime import datetime
import time

api = twitter.Api(consumer_key="consumer_key_here",
                  consumer_secret="consumer_secret_here",
                  access_token_key="access_token_key_here",
                  access_token_secret="access_token_secret_here")

output_image = "current.png"
update_time = 5
pic_url = api.GetUser(screen_name="screenshakes").profile_image_url
pic_url = pic_url.split("_normal")[0]
timestamp = datetime.now().strftime('%d-%b-%Y %H-%M-%S')

print(timestamp+" Updating image...")

with open(output_image, "wb") as handle:
    response = requests.get(pic_url+".png", stream=True)
    if not response.ok:
        print(response)

    for block in response.iter_content(1024):
        if not block:
            break

        handle.write(block)
handle.close()
time.sleep(update_time)
