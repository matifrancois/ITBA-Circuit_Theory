import pyvisa as visa


# Visa Manager: Creates a Visa resource manager and a list of connected instruments.
class VisaManager:
    def __init__(self):
        self.list_of_instruments = []
        self.resource_manager = visa.ResourceManager()
        self.list_of_detailed_instruments = []

    def get_resource_manager(self):
        return self.resource_manager

    def get_list_of_visa_strings(self):
        """
        Returns a list of the visa strings of the connected instruments.
        :return: list.
        """
        self.list_of_instruments = []
        self.list_of_instruments = self.resource_manager.list_resources()
        return self.list_of_instruments

    def get_list_of_detailed_instruments(self):
        """
        Returns a list of Instrument instances fof the connected instruments.
        :return: Instrument instances list. Each element contains its visa string and its respective id string.
        """
        lst_inst = self.get_list_of_visa_strings()
        self.list_of_detailed_instruments = []
        for inst in lst_inst:
            instrument = Instrument(inst, self)
            self.list_of_detailed_instruments.append(instrument)
        return self.list_of_detailed_instruments

    def get_visa_from_idn(self, id_string):
        """
        Finds and returns a visa string from the list of connected instruments associated to an id string.
        :param id_string: Id string from the instrument to obtain the visa string.
        :return: visa string from the instrument searched. None if the element wasn't found.
        """
        found = False
        for inst in self.list_of_detailed_instruments:
            if inst.idnString == id_string:
                found = True
                return inst.visa_string
        if not found:
            return None

# Instrument: Contains the visa string and the id string of a connected instrument.
class Instrument:
    def __init__(self, visa_string, visa_manager):
        self.visa_string = visa_string
        rm = visa_manager.get_resource_manager()
        inst = rm.open_resource(visa_string)
        self.idnString = inst.query('*IDN?')
