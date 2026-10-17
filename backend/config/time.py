from datetime import datetime, timezone


def utc_now() -> datetime:
    """
    Retorna o instante atual em UTC como datetime *naive*.

    O SQLite (e outros drivers) devolve datetimes sem timezone, o que torna
    comparações com datetimes aware impossíveis (`TypeError`). Centralizar aqui
    garante que leitura e escrita usem a mesma convenção.

    Returns:
        O instante atual, em UTC, sem informação de timezone.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
