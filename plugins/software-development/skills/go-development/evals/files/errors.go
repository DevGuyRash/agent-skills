package account

import (
	"errors"
	"fmt"
)

var ErrNotFound = errors.New("account not found")

func loadError() error {
	return fmt.Errorf("load account: %v", ErrNotFound)
}
