package handlers

import (
	"github.com/nrf24l01/tg_rss/backend/core"
	"gorm.io/gorm"
)

type Handler struct {
	Config *core.Config
	DB     *gorm.DB
}
