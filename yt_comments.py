from googleapiclient.discovery import build
import pandas as pd
from googletrans import Translator
import emoji
from dotenv import load_dotenv
import os

# Environment variables
load_dotenv()
video_id = os.getenv("video_id")
api_key = os.getenv("api_key")


comments_list = []

# recursive function to get all replies in a comment thread
def get_replies(comment_id, token):
    replies_response = yt_object.comments().list(part = 'snippet', maxResults = 100, parentId = comment_id, pageToken = token).execute()

    for reply in replies_response['items']:
        all_comments.append(reply['snippet']['textDisplay'])

    if replies_response.get("nextPageToken"):
        return get_replies(comment_id, replies_response['nextPageToken'])
    else:
        return []


# recursive function to get all comments
def get_comments(youtube, video_id, next_view_token):
    global all_comments

    # check for token
    if len(next_view_token.strip()) == 0:
        all_comments = []

    if next_view_token == '':
        # get the initial response
        comment_list = youtube.commentThreads().list(part = 'snippet', maxResults = 100, videoId = video_id, order = 'relevance').execute()
    else:
        # get the next page response
        comment_list = youtube.commentThreads().list(part = 'snippet', maxResults = 100, videoId = video_id, order='relevance', pageToken=next_view_token).execute()
    # loop through all top level comments
    for comment in comment_list['items']:
        # add comment to list
        all_comments.append([comment['snippet']['topLevelComment']['snippet']['textDisplay']])
        # get number of replies
        reply_count = comment['snippet']['totalReplyCount']
        all_replies = []
        # if replies greater than 0
        if reply_count > 0:
            # get first 100 replies
            replies_list = youtube.comments().list(part='snippet', maxResults=100, parentId=comment['id']).execute()
            for reply in replies_list['items']:
                # add reply to list
                all_replies.append(reply['snippet']['textDisplay'])

            # check for more replies
            while "nextPageToken" in replies_list:
                token_reply = replies_list['nextPageToken']
                # get next set of 100 replies
                replies_list = youtube.comments().list(part = 'snippet', maxResults = 100, parentId = comment['id'], pageToken = token_reply).execute()
                for reply in replies_list['items']:
                    # add reply to list
                    all_replies.append(reply['snippet']['textDisplay'])

        # add all replies to the comment
        all_comments[-1].append(all_replies)

    if "nextPageToken" in comment_list:
        return get_comments(youtube, video_id, comment_list['nextPageToken'])
    else:
        return []


all_comments = []

# build a youtube object using our api key
yt_object = build('youtube', 'v3', developerKey=api_key)

#print("Clear 1")

# HTML tag remove function

def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

# get all comments and replies + clean emojis + clean HTML tags
comments = get_comments(yt_object, video_id, '')

for comment, replies in all_comments:

    if len(emoji.emoji_list(comment)) > 0:
        comments_list.append(comment.replace(emoji.emoji_list(comment)[0]['emoji'], "")),
    else: comments_list.append(remove_html_tags(comment))

    if len(replies) > 0:
        for reply in replies:
            if len(emoji.emoji_list(reply)) > 0:
                comments_list.append(reply.replace(emoji.emoji_list(reply)[0]['emoji'], "")),
            else: comments_list.append(remove_html_tags(reply))

#print("Clear 2")

df = pd.Series (comments_list)

#print("Clear 3")

# Translate and emoji cleaner

translator = Translator()

df = df.apply(lambda x: translator.translate(x,  dest='en').text)

# df = df.apply(lambda x: x.replace(emoji.emoji_list(x)[0]['emoji'], ""))

#print("Clear 4")

# List to CSV in folder

df.to_csv('C:/Users/Windows 10/Desktop/PEDRO/CODE/YTcomments2.csv', sep=';', encoding='utf-8', index=False)

#print("Clear 5")


