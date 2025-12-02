package handlers

import (
	"encoding/xml"
	"fmt"
	"log"
	"net/http"

	"github.com/gabriel-vasile/mimetype"
	"github.com/labstack/echo/v4"
	"github.com/nrf24l01/tg_rss/backend/postgres"
	"github.com/nrf24l01/tg_rss/backend/schemas"
)

func (h *Handler) RssHandler(c echo.Context) error {
	var feeds []postgres.UserGroupMedia
	if err := h.DB.
        Select("id, description, created_at, media").
        Order("created_at DESC").
        Find(&feeds).Error; err != nil {

        log.Printf("Failed to fetch feeds: %v", err)
        return echo.NewHTTPError(http.StatusInternalServerError, "Pupupu...")
    }
	
	var rssChemas []schemas.UserGroupMedia

	for _, feed := range feeds {
		rssItem := feed.ToRSSSchema()
		rssChemas = append(rssChemas, *rssItem)
	}

	log.Printf("RssHandler: fetched %d feeds from DB", len(rssChemas))

	scheme := "http"
	if c.Request().TLS != nil {
		scheme = "https"
	}
	baseURL := fmt.Sprintf("%s://%s", scheme, c.Request().Host)

	rss := schemas.GenRSSFeed(baseURL, rssChemas)

	b, err := xml.MarshalIndent(rss, "", "  ")
	if err != nil {
		log.Printf("Failed to marshal RSS: %v", err)
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to build rss")
	}

	resp := append([]byte(xml.Header), b...)
	return c.Blob(http.StatusOK, "application/rss+xml; charset=utf-8", resp)
}

func (h *Handler) DownloadFileHandler(c echo.Context) error {
	uuid := c.Param("uuid")

	var media postgres.UserGroupMedia
	if err := h.DB.First(&media, "id = ?", uuid).Error; err != nil {
		return echo.NewHTTPError(http.StatusNotFound, "Media not found")
	}

	// detect media type for proper content-type header
	contentType := "application/octet-stream"
	if len(media.Media) > 0 {
		if mt := mimetype.Detect(media.Media); mt != nil {
			contentType = mt.String()
		}
	}

	return c.Blob(http.StatusOK, contentType, media.Media)
}