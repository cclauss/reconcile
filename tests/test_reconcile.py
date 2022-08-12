import csv

import pytest

from reconcile import __version__
from reconcile.database import Database
from reconcile.main import Reconciler

SQLITE_DB = ":memory:"
# SQLITE_DB = "./tests/ol_test1.db"
IA_PHYSICAL_DIRECT_DUMP = "./tests/seed_ia_physical_direct.tsv"
OL_EDITIONS_DUMP = "./tests/seed_ol_dump_editions.txt"
OL_EDITIONS_DUMP_PARSED = "./tests/ol_dump_editions_parsed.tsv"

reconciler = Reconciler()


def test_version():
    assert __version__ == "0.1.0"


@pytest.fixture()
def setup_db():
    """
    Setup the database table, populate Internet Archive data, and yield a
    Database instance to use.
    """
    db = Database(SQLITE_DB)
    reconciler.create_db(db, IA_PHYSICAL_DIRECT_DUMP)
    yield db  # See the Database class
    db.close()


# @pytest.mark.usefixtures("setup_db")
def test_get_an_ia_db_item(setup_db: Database):
    """
    Get an Internet Archive DB item to make sure inserting from our seed
    data works.
    """
    db = setup_db
    db.execute(
        "SELECT ia_id, ia_ol_edition_id FROM reconcile WHERE ia_ol_edition_id = 'OL1426680M'"
    )
    assert db.fetchall() == [("goldenass0000apul_k5d0", "OL1426680M")]


def test_parse_ol_dump():
    """
    Parse the Open Library editions dump insert an item, and get an item to
    make sure it works.
    """
    reconciler.parse_ol_dump_and_write_ids(OL_EDITIONS_DUMP, OL_EDITIONS_DUMP_PARSED)
    output = []
    with open(OL_EDITIONS_DUMP_PARSED) as file:
        reader = csv.reader(file, delimiter="\t")
        output = [row for row in reader]

    assert len(output) == 7
    assert ["OL1002158M", "organizinggenius0000benn"] in output
    assert ["OL10000149M"] not in output


# @pytest.mark.usefixtures("setup_db")
def test_insert_ol_data(setup_db: Database):
    """
    Insert Open Library data into the database on the basis of the Internet
    Archive data that's already in there and get an item to make sure it's
    there.
    """
    db = setup_db
    reconciler.insert_ol_data_from_tsv(db, OL_EDITIONS_DUMP_PARSED)
    db.execute(
        "SELECT ia_id, ia_ol_edition_id, ol_edition_id FROM reconcile WHERE ia_id = 'goldenass0000apul_k5d0'"
    )
    assert db.fetchall() == [("goldenass0000apul_k5d0", "OL1426680M", "OL1426680M")]


# def test_query_ol_id_differences():
