# twitter example

import os
import sys

import twitter

def test():
    consumer_key = "9WHR2Z6xipO2i68onTl5dA"
    consumer_secret = "VtGCTwmnyDxsxGoxzdJZd1KfAzagGJMPzcFeIV3o44"
    access_key = "15001676-iwbnYbe8zcTIt8JV5EQkNSKKqnCTaFASPLUQ3EaWe"
    access_secret = "lLYdf7JsIlVzXbz2i48GmkIAVhlLg5PxvROCqSKnsGWrc"
    
    api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=access_key, access_token_secret=access_secret)
    
    #status = api.PostUpdate('[test from python]')
    #print status
    
    statuses = api.GetUserTimeline("augustlights")
    print len(statuses)
    
    for s in statuses:
        print s.created_at, s.text
    
    users = api.GetFriends()
    for u in users: 
        print u.name 
        
test()    
                          