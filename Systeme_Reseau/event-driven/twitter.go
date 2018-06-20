package kubeless

import (
	"fmt"

	"github.com/dghubble/go-twitter/twitter"
	"github.com/dghubble/oauth1"
	"github.com/kubeless/kubeless/pkg/functions"
)

func Twitter(event functions.Event, context functions.Context) (string, error) {
	config := oauth1.NewConfig("consumerKey", "consumerSecret")
	token := oauth1.NewToken("accessToken", "accessSecret")
	httpClient := config.Client(oauth1.NoContext, token)

	client := twitter.NewClient(httpClient)

	tweet, resp, err := client.Statuses.Update(event.Data, nil)
	return fmt.Sprintf("tweet:\n%+v\nresponse:\n%+v\nerror:\n%+v\n", tweet, resp, err), nil

}
