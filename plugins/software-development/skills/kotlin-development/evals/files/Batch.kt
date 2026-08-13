data class Batch(val items: MutableList<String>)

fun isolatedCopy(batch: Batch): Batch = batch.copy()
