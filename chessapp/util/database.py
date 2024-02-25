from typing import Mapping
from tinydb import where
from tinydb.table import Table


def update_table(table: Table, documents: list[Mapping], id_field: str = "id"):
    """ This method updates the table such that. The id_field is used to identify the
    documents. If a document with the same id_field value exists in the table, it is updated, otherwise it is inserted.
    All documents have to contain the id_field. Otherwise the documents cannot be identified.


    Args:
        table (Table): target table
        documents (list[Mapping]): documents to update or insert
        id_field (str, optional): id_field used to identify identical documents

    Raises:
        ValueError: if a document does not contain the id_field
    """
    if len(documents) == 0:
        return

    # Get the IDs of all documents in the index table
    existing_ids = [doc[id_field] for doc in table.all()]

    # Split documents into existing and new entries
    existing_entries = [
        doc for doc in documents if doc[id_field] in existing_ids]
    new_entries = [
        doc for doc in documents if doc[id_field] not in existing_ids]

    # Update existing entries and insert new entries
    for doc in existing_entries:
        if not id_field in doc:
            raise ValueError("id_field " + id_field +
                             " not found in document " + str(doc))
        table.update(doc, cond=where(id_field) == doc[id_field])
    table.insert_multiple(new_entries)
