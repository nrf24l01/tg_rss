package handlers

import (
	"log"
	"net/http"

	"github.com/labstack/echo/v4"
	"github.com/nrf24l01/tg_rss/backend/postgres"
	"github.com/nrf24l01/tg_rss/backend/schemas"
)

func (h *Handler) RssHandler(c echo.Context) error {
	var feeds []postgres.UserGroupMedia
	if err := h.DB.Select("id, description, created_at").Find(&feeds).Error; err != nil {
		log.Printf("Failed to fetch feeds: %v", err)
		return echo.NewHTTPError(http.StatusInternalServerError, "Pupupu...")
	}
	
	var rssChemas []schemas.UserGroupMedia

	for _, feed := range feeds {
		rssItem := feed.ToRSSSchema()
		rssChemas = append(rssChemas, *rssItem)
	}

	rss := schemas.GenRSSFeed(rssChemas)

	return c.XML(http.StatusOK, rss)
}

func (h *Handler) DownloadFileHandler(c echo.Context) error {
	uuid := c.Param("uuid")

	var media postgres.UserGroupMedia
	if err := h.DB.First(&media, "id = ?", uuid).Error; err != nil {
		return echo.NewHTTPError(http.StatusNotFound, "Media not found")
	}

	return c.Blob(http.StatusOK, "application/octet-stream", media.Media)
}