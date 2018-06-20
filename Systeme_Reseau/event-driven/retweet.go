package kubeless

import (
	"fmt"

	"github.com/dghubble/go-twitter/twitter"
	"github.com/dghubble/oauth1"
	"github.com/kubeless/kubeless/pkg/functions"
)

func Retweet(event functions.Event, context functions.Context) (string, error) {
	config := oauth1.NewConfig("consumerKey", "consumerSecret")
	token := oauth1.NewToken("accessToken", "accessSecret")
	httpClient := config.Client(oauth1.NoContext, token)

	client := twitter.NewClient(httpClient)

	searchParams := &twitter.SearchTweetParams{
		Query:      "#GLMF",
		Count:      1,
		ResultType: "recent",
	}

	searchResult, _, _ := client.Search.Tweets(searchParams)

	// Retweet
	for _, tweet := range searchResult.Statuses {
		tweet_id := tweet.ID
		client.Statuses.Retweet(tweet_id, &twitter.StatusRetweetParams{})

		fmt.Printf("RETWEETED: %+v\n", tweet.Text)
	}

	return "", nil

}
