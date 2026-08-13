#include <stddef.h>
#include <stdlib.h>

struct item { unsigned value; };

struct item *allocate_items(size_t count) {
    return malloc(count * sizeof(struct item));
}
