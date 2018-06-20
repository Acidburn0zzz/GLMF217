package kubeless

import (
	"fmt"
	"io/ioutil"

	"github.com/dghubble/go-twitter/twitter"
	"github.com/dghubble/oauth1"
	"github.com/kubeless/kubeless/pkg/functions"
)

func Twitter(event functions.Event, context functions.Context) (string, error) {
	consumerKey, _ := ioutil.ReadFile("/twitter-secrets/consumerKey")
	consumerSecret, _ := ioutil.ReadFile("/twitter-secrets/consumerSecret")
	accessToken, _ := ioutil.ReadFile("/twitter-secrets/accessToken")
	accessSecret, _ := ioutil.ReadFile("/twitter-secrets/accessSecret")
	config := oauth1.NewConfig(string(consumerKey), string(consumerSecret))
	token := oauth1.NewToken(string(accessToken), string(accessSecret))
	httpClient := config.Client(oauth1.NoContext, token)

	client := twitter.NewClient(httpClient)

	tweet, resp, err := client.Statuses.Update(event.Data, nil)
	return fmt.Sprintf("tweet:\n%+v\nresponse:\n%+v\nerror:\n%+v\n", tweet, resp, err), nil

}
