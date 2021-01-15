import twitter
import requests
from datetime import datetime
import time
import traceback
from io import BytesIO
import json
import dateutil.parser

version = "v2.1"

pngFile = "current.png" # Location to save current frame
tweetFile = "tweets.html" # Location to save most recent tweets

# Twitter API Keys - fill in with your own OAuth info
CONSUMERKEY=""
CONSUMERSECRET=""
ACCESSKEY=""
ACCESSSECRET=""

'''
Gets an API object and returns it
'''
def getAPI():
    api = twitter.Api(consumer_key=str(CONSUMERKEY),
                  consumer_secret=str(CONSUMERSECRET),
                  access_token_key=str(ACCESSKEY),
                  access_token_secret=str(ACCESSSECRET))
    return api

'''
Download and parse the latest game data file from Constantin
'''
def getJSONData():
    pressxtojson = urllib.request.urlopen("https://screenshake.club/share/tpp")
    jsondata = json.loads(pressxtojson.read())
    pressxtojson.close()
    time = jsondata["LastInputTime"]
    time = dateutil.parser.parse(time)
    chosenInput = jsondata["LastInput"]
    inputCount = jsondata["ChosenInputCount"]
    return time, chosenInput, inputCount

'''
Load the most recent tweets and save them to an html file
'''
def updateTweets(api):
    lastTime, chosenInput, inputCount = getJSONData()

    results = api.GetSearch(
        raw_query="q=%40screenshakes&src=typeahead_click&f=live&count=50")
    tweetstr = ""
    counter = 0
    timesince = (datetime.now(timezone.utc)-lastTime).seconds
    tweetstr += "<b>Time Since Press: </b>" + str(timesince) + "s (" + str(chosenInput) + ", " + str(inputCount) + " votes)<br><br>"
    for result in results:
        if counter > 9:
            break
        status = api.GetStatus(result.id)
        if not status.text.startswith("RT @"):
            text = status.text.replace("@screenshakes", " ")
            author = status.user.name
            tweettime = status.created_at
            tweettime = datetime.strptime(tweettime,'%a %b %d %H:%M:%S +0000 %Y').strftime("%m/%d/%Y, %H:%M:%S")
        
            tweetstr += text
            tweetstr += "<span style=\"color:grey;\"><br>— <b>"
            tweetstr += author + "</b><small> "
            tweetstr += tweettime
            tweetstr += " UTC</small></span><br><br>"

            counter += 1
    timestamp = datetime.now().strftime('%d-%b-%Y %H-%M-%S')
    print(timestamp+" Updating tweets...")
    tweetfile = open(tweetFile, "wb")
    tweetfile.write(tweetstr.encode('utf-8'))
    tweetfile.close()

'''
Load the most recent profile picture and save it to a png file
'''
def updateImage(api):
    pic_url = api.GetUser(screen_name="screenshakes").profile_image_url
    pic_url = pic_url.split("_normal")[0]
    timestamp = datetime.now().strftime('%d-%b-%Y %H-%M-%S')
    print(timestamp+" Updating image...")
    with open(pngFile, "wb") as handle:
        response = requests.get(pic_url+".png", stream=True)
        if not response.ok:
            print(response)

        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)          
    handle.close()

def main():
    print("twitterplays "+version+" by LeifEricson")
    while True: # Endlessly loop
        try:
            # Due to API limitations, pfp is refreshed every 5s and the tweets every 15s
            # A new API object is created in case of random api errors, since script runs unattended
            api = getAPI()
            updateImage(api)
            time.sleep(5)
            updateImage(api)
            time.sleep(5)
            updateImage(api)
            time.sleep(5)
            updateTweets(api)
        except twitter.error.TwitterError as err: # Completely ignore API errors for unattended running
            print(err)
        except Exception as exc: # Print other errors, but ignore them. Again, for unattended running
            print(traceback.format_exc())
            print(exc)

if __name__ == "__main__":
    main()
