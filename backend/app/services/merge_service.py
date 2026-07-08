class MergeStrategy:
    def merge(self, csv_row, es_data):
        raise NotImplementedError("Merge strategies must implement merge()")


class CsvElasticsearchMergeStrategy(MergeStrategy):
    def merge(self, csv_row, es_data):
        merged_doc = dict(csv_row)

        if es_data is None:
            merged_doc["enrichment_status"] = "not_found"
            return merged_doc

        merged_doc.update(es_data)
        return merged_doc


def get_merge_strategy():
    return CsvElasticsearchMergeStrategy()
