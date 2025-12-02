package schemas

import (
	"time"
)

type UserGroupMedia struct {
	ID          string  `json:"id"`
	MediaLink   string  `json:"media_link"`
	Description *string `json:"description,omitempty"`
	CreatedAt   string  `json:"created_at"`
	MediaType   string  `json:"media_type,omitempty"`
	MediaSize   string  `json:"media_size,omitempty"`
}

func GenRSSFeed(baseURL string, userGroupMedia []UserGroupMedia) *RSS {
	rss := &RSS{
		Version: "2.0",
		Channel: Channel{
			Title:       "User Group Media Feed",
			Link:        baseURL + "/rss",
			Description: "RSS feed for user group media",
			Items:       []Item{},
		},
	}

	for _, media := range userGroupMedia {
		link := media.MediaLink
		// ensure absolute URL
		if len(link) > 0 && link[0] == '/' {
			link = baseURL + link
		}

		item := Item{
			Title:       "Media " + media.ID,
			Link:        link,
			GUID:        media.ID,
			Description: "",
			Enclosure: &Enclosure{
				URL:  link,
				Type: media.MediaType,
				Length: media.MediaSize,
			},
		}
		if media.Description != nil {
			item.Description = *media.Description
		}
		
		if media.CreatedAt != "" {
			if t, err := time.Parse(time.RFC3339, media.CreatedAt); err == nil {
				item.PubDate = t.Format(time.RFC1123Z)
			}
		}

		rss.Channel.Items = append(rss.Channel.Items, item)
	}

	if len(rss.Channel.Items) > 0 {
		rss.Channel.LastBuildDate = rss.Channel.Items[0].PubDate
		rss.Channel.PubDate = rss.Channel.Items[0].PubDate
	} else {
		rss.Channel.LastBuildDate = time.Now().Format(time.RFC1123Z)
		rss.Channel.PubDate = rss.Channel.LastBuildDate
	}

	return rss
}