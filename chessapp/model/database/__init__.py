from chessapp.model.database.datamaster import Datamaster


s_datamaster_instance: Datamaster = None


def get_datamaster() -> Datamaster:
    global s_datamaster_instance
    if s_datamaster_instance is None:
        s_datamaster_instance = Datamaster()
        s_datamaster_instance.open()
    return s_datamaster_instance
