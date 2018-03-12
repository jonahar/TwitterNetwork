import json
import tweepy

ACCESS_TOKEN_FILENAME = "keys/access_token.json"
CONSUMER_TOKEN_FILENAME = "keys/consumer_token.json"

with open(ACCESS_TOKEN_FILENAME) as a, open(CONSUMER_TOKEN_FILENAME) as c:
    consumer = json.load(c)
    access = json.load(a)
    consumer_secret = consumer["consumer_secret"]
    consumer_token = consumer["consumer_token"]
    access_token = access["access_token"]
    access_token_secret = access["access_token_secret"]

auth = tweepy.OAuthHandler(consumer_token, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# posting new status
status = api.update_status("This status was created using twitter API #Cool")
# commenting to the previous posted status
comment = api.update_status("This is a comment #comment_and_chill", in_reply_to_status_id=status.id)
# destroy both
status.destroy()
comment.destroy()

# posting status with image
image_filename = "cat.jpg"
status = api.update_with_media(image_filename, "Status with media, posted using #TwitterAPI")

# get the user of Donald Trump
trump = api.get_user("realDonaldTrump")

# iterate over trump's last 100 tweets
cursor = tweepy.Cursor(api.user_timeline, id=trump.id, tweet_mode="extended")
total_statuses_received = 0
for page in cursor.pages():
    total_statuses_received += len(page)
    print("processing", len(page), "statuses")
    if total_statuses_received >= 100:
        break

# iterate over all people being followed by trump
cursor = tweepy.Cursor(api.friends_ids, id=trump.id)
total_following = 0
for page in cursor.pages():
    total_following += len(page)
print("Total number of people being followed by trump:", total_following)

# iterate over all people following trump
outfilename = "trumps_followers.txt"
max_followers_to_process = 200000
with open(outfilename, 'a') as outfile:
    cursor = tweepy.Cursor(api.followers_ids, id=trump.id)
    total_followers_processed = 0
    for page in cursor.pages():
        for follower_id in page:
            outfile.write(str(follower_id))
            outfile.write('\n')
        total_followers_processed += len(page)
        print("total_followers_processed:", total_followers_processed)
        if total_followers_processed >= max_followers_to_process:
            break
