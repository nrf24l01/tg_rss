package routes

import (
	"github.com/labstack/echo/v4"
	echokitMw "github.com/nrf24l01/go-web-utils/echokit/middleware"
	"github.com/nrf24l01/tg_rss/backend/handlers"
)

func RegisterPSSRoutes(e *echo.Echo, h *handlers.Handler) {
	group := e.Group("/rss")

	group.GET("", h.RssHandler)
	group.GET("/img/:uuid", h.DownloadFileHandler, echokitMw.PathUuidV4Middleware("uuid"))
}
