package routes

import (
	"github.com/labstack/echo/v4"
	"github.com/nrf24l01/tg_rss/backend/handlers"
)

func RegisterRoutes(e *echo.Echo, h *handlers.Handler) {
	RegisterPSSRoutes(e, h)
}
