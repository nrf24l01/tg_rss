package schemas

type UserGroupMedia struct {
	ID          string  `json:"id"`
	MediaLink   string  `json:"media_link"`
	Description *string `json:"description,omitempty"`
	CreatedAt   string  `json:"created_at"`
}

func GenRSSFeed(userGroupMedia []UserGroupMedia) *RSS {
	rss := &RSS{
		Version: "2.0",
		Channel: Channel{
			Title:       "User Group Media Feed",
			Link:        "http://example.com/rss",
			Description: "RSS feed for user group media",
			Items:       []Item{},
		},
	}

	for _, media := range userGroupMedia {
		item := Item{
			Title:       "Media " + media.ID,
			Link:        media.MediaLink,
			GUID:        media.ID,
			Description: "",
		}
		if media.Description != nil {
			item.Description = *media.Description
		}
		rss.Channel.Items = append(rss.Channel.Items, item)
	}

	return rss
}