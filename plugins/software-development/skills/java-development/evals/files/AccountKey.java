import java.util.Objects;

record AccountKey(String id) {
    @Override
    public boolean equals(Object other) {
        return other instanceof AccountKey key && id.equalsIgnoreCase(key.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}
