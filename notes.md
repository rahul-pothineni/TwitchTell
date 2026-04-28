04/28/26 12:18 AM - 1:08 AM

Currently I am only able to take in 1 streamer at a time --> Trying to take in up to 10
I am thinking about splitting the data by key, where the key is the target_channel.
    This would also require more consumer groups?
    Probably more partinions too (too keep up with the raised load)
Problem --> Twitch EventSub API only allows 3 connections per account
    Could create more accounts, but this would not be user friendly in a production app
    We subscribe to all channels using one login token.
Problem --> How to load in multiple variables from an env variable.
    comma seperate the variable in the env file
        load the variable in with .split by comma
Problem --> consumer is only consuming from the last element in the TARGET_CHANNEL env variable   
    Problem --> Maybe the consummer is only subscribing to the first channel it takes in?
        Maybe Producer is having the same problem, because we are sending all on the same topic anyways, so the consumer should data from all channels in right?
    I was right it is only consuming from the last element in the target channel env. 
    Had to use an aync generator, but still not working. 
    Tried wrapping the listen_channel_chat_message chall in a for loop looping around targets (maybe we were landing on the last target and sticking with that?)
        CORRECT!!
Problem --> injestion is slow (only 1 message per batch)
    reduce batch size to 1 kb 
    change linger.ms to 2000ms
        throughput dsrastically increased
