package postgres

import (
	"fmt"
	"strconv"
	"time"

	"github.com/gabriel-vasile/mimetype"
	"github.com/google/uuid"
	"github.com/nrf24l01/tg_rss/backend/schemas"
)

type UserGroupMedia struct {
	ID          uuid.UUID `db:"id" json:"id"`
	UserID      int64     `db:"user_id" json:"user_id"`
	GroupID     int64     `db:"group_id" json:"group_id"`
	Media       []byte    `db:"media" json:"media"`
	Description *string   `db:"description" json:"description,omitempty"`
	CreatedAt   time.Time `db:"created_at" json:"created_at"`
	MessageID   int64     `db:"message_id" json:"message_id"`
}

func (UserGroupMedia) TableName() string { return "user_group_media" }

func (u *UserGroupMedia) ToRSSSchema() *schemas.UserGroupMedia {
	mediaType := "application/octet-stream"
	if len(u.Media) > 0 {
		if mt := mimetype.Detect(u.Media); mt != nil {
			mediaType = mt.String()
		}
	}

	return &schemas.UserGroupMedia{
		ID:          u.ID.String(),
		MediaLink:   fmt.Sprintf("/rss/img/%s", u.ID.String()),
		Description: u.Description,
		CreatedAt:   u.CreatedAt.Format(time.RFC3339),
		MediaType:   mediaType,
		MediaSize:   strconv.Itoa(len(u.Media)),
	}
}