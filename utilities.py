import random as rd
import constants as c


class Ticker(object):
    """Simple timer for roguelike games."""

    def __init__(self):
        self.ticks = 0  # current ticks--sys.maxint is 2147483647
        self.schedule = {}  # this is the dict of things to do {ticks: [obj1, obj2, ...], ticks+1: [...], ...}
        self.ticks_to_advance = 0

    def schedule_turn(self, interval, obj):
        self.schedule.setdefault(self.ticks + interval, []).append(obj)

    def _advance_ticks(self, interval):
        for i in range(interval):
            things_to_do = self.schedule.pop(self.ticks, [])
            for obj in things_to_do:
                if obj is not None:
                    obj.take_turn()
            self.ticks += 1

    def advance_ticks(self):
        if self.ticks_to_advance > 0:
            self._advance_ticks(self.ticks_to_advance)
            self.ticks_to_advance = 0

    def unregister(self, obj):
        if obj is not None:
            for key in self.schedule.keys():
                while obj in self.schedule[key]:
                    # copy = self.schedule[key][:]
                    # copy.remove(obj)
                    # self.schedule[key] = copy[:]
                    self.schedule[key].remove(obj)


class Publisher(object):
    """
    Dispatch messages
    Messages have two categories (defined in constants):
    * Main: like log, fight, exploration, inventory
    * Sub: precises the main, optional.
    Messgae content is a dictionary
    """

    def __init__(self):
        self._specialized_list = {}  # Subscribe to main and a list of sub_category
        self.in_publish = False
        self.delayed_unregister = []

    def register(self,
                 object_to_register,
                 main_category=c.P_ALL,
                 sub_category=c.P_ALL,
                 function_to_call=None):
        """
        Register an object so that we
        :param object_to_register: the object that will be notified.
        Note that the same object may be registered multiple time, with different functions to be called or
        different category of interest, so that we are effectively saving the method only
        :param main_category: one or multiple (in list) categories to register.
        :param sub_category: one or multiple (in list) specialized sub categories to register
        :param function_to_call: the method to be called.
        :return:
        """
        if function_to_call is None:
            assert hasattr(object_to_register, "notify"), \
                "Object {} has no notify method and has not precised the " \
                "function to be called".format(object_to_register)
            function_to_call = getattr(object_to_register, "notify")
        if type(sub_category) is not (list or tuple):
            sub_category = [sub_category]
        if type(main_category) is not (list or tuple):
            main_category = [main_category]
        for category in main_category:
            for sub in sub_category:
                key = "{}#{}".format(category, sub)
                if key not in self._specialized_list.keys():
                    self._specialized_list[key] = [function_to_call]
                elif function_to_call not in self._specialized_list[key]:
                    self._specialized_list[key].append(function_to_call)

    def unregister_all(self, object_to_unregister):
        # We need to parse all the lists..
        # and the same object may have been registered with different functions
        if self.in_publish:
            self.delayed_unregister.append(object_to_unregister)
        else:
            for key in self._specialized_list.keys():
                list_to_remove = []
                list_to_parse = self._specialized_list[key]
                for function in list_to_parse:
                    if function.__self__ == object_to_unregister:
                        list_to_remove.append(function)
                for function in list_to_remove:
                    self._specialized_list[key].remove(function)

    def handle_delayed_unregister_all(self):
        for object_to_unregister in self.delayed_unregister:
            self.unregister_all(object_to_unregister)

    def publish(self, source, message, main_category=c.P_ALL, sub_category=c.P_ALL):
        self.in_publish = True
        assert type(message) is dict, "Message {} is not a dict".format(message)
        message["SOURCE"] = source
        broadcasted_list = []
        message["MAIN_CATEGORY"] = main_category
        message["SUB_CATEGORY"] = sub_category
        if type(sub_category) is not (list or tuple):
            sub_category = [sub_category]
        if type(main_category) is not (list or tuple):
            main_category = [main_category]

        # By default, we always broadcast to "ALL"
        if c.P_ALL not in main_category:
            main_category.append(c.P_ALL)
        if c.P_ALL not in sub_category:
            sub_category.append(c.P_ALL)

        for category in main_category:
            for sub in sub_category:
                message["BROADCAST_MAIN_CATEGORY"] = category
                message["BROADCAST_SUB_CATEGORY"] = category
                key = "{}#{}".format(category, sub)
                if key in self._specialized_list:
                    for function in self._specialized_list[key]:
                        if function not in broadcasted_list:  # Need to be sure not to send two times the message
                            function(message)
                            broadcasted_list.append(function)
        self.in_publish = False
        self.handle_delayed_unregister_all()

"""
Utilities Functions.
"""


def roll(dice, repeat=1):
    """
    Roll one or multiple dice(s)
    :param dice: the type of dice - 6 for d6, 8 for d8...
    :param repeat: the number of dices of same tye to roll
    :return: the value
    """
    res = 0
    for i in range(repeat):
        res += rd.randint(1, dice)
    return res



NAMES = ["Abaet","Acamen","Adeen","Aghon","Ahburn","Airen","Aldaren","Alkirk","Amitel","Anumil","Asen","Atgur","Auden","Aysen","Abarden","Achard","Aerden","Agnar","Ahdun","Airis","Alderman","Allso","Anfar","Asden","Aslan","Atlin","Ault","Aboloft","Ackmard","Afflon","Ahalfar","Aidan","Albright","Aldren","Amerdan","Anumi","Asdern","Atar","Auchfor","Ayrie",
"Bacohl","Balati","Basden","Bedic","Beson","Bewul","Biston","Boaldelr","Breanon","Bredock","Bristan","Busma","Badeek","Baradeer","Bayde","Beeron","Besur","Biedgar","Bithon","Bolrock","Bredere","Breen","Buchmeid","Buthomar","Baduk","Barkydle","Beck","Bein","Besurlde","Bildon","Boal","Brakdern","Bredin","Brighton","Bue","Bydern",
"Caelholdt","Camchak","Casden","Celorn","Cerdern","Cevelt","Chidak","Ciroc","Connell","Cosdeer","Cydare","Cyton","Cainon","Camilde","Cayold","Celthric","Cespar","Chamon","Cibrock","Codern","Cordale","Cuparun","Cylmar","Calden","Cardon","Celbahr","Cemark","Cether","Chesmarn","Cipyar","Colthan","Cos","Cusmirk","Cythnar",
"Daburn","Dakamon","Dalmarn","Darkkon","Darmor","Dask","Derik","Dessfar","Doceon","Dorn","Drakone","Dritz","Dryn","Duran","Dyfar","Daermod","Dakkone","Dapvhir","Darko","Darpick","Deathmar","Derrin","Dinfar","Dochrohan","Dosoman","Drandon","Drophar","Duba","Durmark","Dyten","Dak","Dalburn","Darkboon","Darkspur","Dasbeck","Defearon","Desil","Dismer","Dokoran","Drakoe","Drit","Dryden","Dukran","Dusaro",
"Eard","Efar","Ekgamut","Elson","Endor","Enro","Eritai","Etar","Ethen","Eythil","Eckard","Egmardern","Eli","Elthin","Enidin","Erikarn","Escariet","Etburn","Etmere","Efamar","Eiridan","Elik","Enbane","Enoon","Erim","Espardo","Etdar","Etran",
"Faoturk","Fenrirr","Ficadon","Firedorn","Folmard","Fydar","Faowind","Fetmar","Fickfylo","Firiro","Fraderk","Fyn","Fearlock","Feturn","Fildon","Floran","Fronar",
"Gafolern","Galiron","Gemardt","Gerirr","Gibolock","Gom","Gothikar","Gryn","Guthale","Gyin","Gai","Gametris","Gemedern","Geth","Gibolt","Gosford","Gresforn","Gundir","Gybol","Galain","Gauthus","Gemedes","Gib","Gith","Gothar","Grimie","Gustov","Gybrush",
"Halmar","Hectar","Hermenze","Hildale","Hydale","Harrenhal","Hecton","Hermuck","Hildar","Hyten","Hasten","Heramon","Hezak","Hileict",
"Iarmod","Ieserk","Illilorn","Ipedorn","Isen","Jackson","Janus","Jesco","Jex","Jin","Jun","Kafar","Keran","Kethren","Kiden","Kildarien","Kip","Kolmorn","Lackus","Lafornon","Ledale","Lephidiles","Letor","Liphanes","Ludokrin","Lurd","Macon","Marderdeen","Markdoon","Mathar","Mellamo","Meridan","Mes'ard","Mezo","Mickal","Miphates","Modric","Mufar","Mythik","Nadeer","Naphates","Nikpal","Niro","Nuthor","Nythil","O’tho","Occhi","Ohethlic","Omarn","Othelen","Padan","Peitar","Pendus","Phairdon","Phoenix","Picumar","Ponith","Prothalon","Qeisan","Quid","Qysan","Radag'mal","Rayth","Reth","Rhithin","Rikar","Ritic","Rogoth","Rydan","Ryodan","Rythern","Sabal","Samon","Scoth","Sed","Senthyril","Seryth","Setlo","Shane","Shillen","Sil'forrin","Soderman","Stenwulf","Suth","Syth","Talberon","Temilfist","Tespar","Thiltran","Tibolt","Tithan","Tolle","Tothale","Tuk","Tyden","Uerthe","Undin","Vaccon","Valynard","Vespar","Vider","Vildar","Virde","Voudim","Wak’dern","Wekmar","William","Wiltmar","Wrathran","Wyder","Xander","Xex","Y’reth","Yesirn","Zak","Zeke","Zidar","Zilocke","Zotar"
"Idon","Ikar","Illium","Irefist","Isil","Jalil","Jayco","Jespar","Jib","Juktar","Justal","Kaldar","Kesad","Kib","Kilbas","Kimdar","Kirder","Kyrad","Lacspor","Lahorn","Leit","Lerin","Lidorn","Loban","Luphildern","Zakarn","Madarlon","Mardin","Marklin","Medarin","Meowol","Merkesh","Mesophan","Michael","Migorn","Mi'talrythin","Modum","Mujarin","Mythil","Nalfar","Neowyld","Nikrolin","Noford","Nuwolf","Zerin","Ocarin","Odaren","Okar","Orin","Oxbaren","Palid","Pelphides","Perder","Phemedes","Picon","Pildoor","Poran","Puthor","Qidan","Quiss","Zigmal","Randar","Reaper","Rethik","Rhysling","Rismak","Rogeir","Rophan","Ryfar","Rysdan","Zio","Sadareen","Samot","Scythe","Sedar","Serin","Sesmidat","Shade","Shard","Silco","Silpal","Sothale","Steven","Sutlin","Sythril","Telpur","Tempist","Tessino","Tholan","Ticharol","Tobale","Tolsar","Tousba","Tuscanar","Zutar","Ugmar","Updar","Vacone","Vectomon","Vethelot","Vigoth","Vinald","Voltain","Vythethi","Walkar","Werymn","Willican","Wishane","Wraythe","Wyeth","Xavier","Xithyl","Yabaro","Yssik",
"Ironmark","Ithric","Jamik","Jaython","Jethil","Jibar","Julthor","Ieli","Kellan","Kesmon","Kibidon","Kilburn","Kinorn","Kodof","Ilgenar","Laderic","Laracal","Lephar","Lesphares","Lin","Lox","Lupin","Zecane","Mafar","Markard","Mashasen","Medin","Merdon","Mesah","Mesoton","Mick","Milo","Mitar","Mudon","Mylo","Ingel","Namorn","Nidale","Niktohal","Nothar","Nydale","Zessfar","Occelot","Odeir","Omaniron","Ospar","Xuio","Papur","Pender","Perol","Phexides","Pictal","Pixdale","Poscidion","Pyder","Quiad","Qupar","Zile","Raysdan","Resboron","Rhithik","Riandur","Riss","Rogist","Rulrindale","Ryfar","Rythen","Zoru","Safilix","Sasic","Secor","Senick","Sermak","Seth","Shadowbane","Shardo","Sildo","Sithik","Staph","Suktor","Syr","Yssith","Temil","Teslanar","Tethran","Tibers","Tilner","Tol’Solie","Toma","Towerlock","Tusdar","Zyten","Uhrd","Uther","Valkeri","Veldahar","Victor","Vilan","Vinkolt","Volux","Yepal","Wanar","Weshin","Wilte","Witfar","Wuthmon","Wyvorn","Xenil"]


###############################################################################
# Markov Name model
# A random name generator, by Peter Corbett
# http://www.pick.ucam.org/~ptc24/mchain.html
# This script is hereby entered into the public domain
###############################################################################
class Mdict:
    def __init__(self):
        self.d = {}

    def __getitem__(self, key):
        if key in self.d:
            return self.d[key]
        else:
            raise KeyError(key)

    def add_key(self, prefix, suffix):
        if prefix in self.d:
            self.d[prefix].append(suffix)
        else:
            self.d[prefix] = [suffix]

    def get_suffix(self, prefix):
        l = self[prefix]
        return rd.choice(l)


class MName:
    """
    A name from a Markov chain
    """

    def __init__(self, chainlen=3):
        """
        Building the dictionary
        """
        assert 1 < chainlen < 10, "Chain length must be between 1 and 10, inclusive"
        self.mcd = Mdict()
        oldnames = []
        self.chainlen = chainlen

        for l in NAMES:
            l = l.strip()
            oldnames.append(l)
            s = " " * chainlen + l
            for n in range(0, len(l)):
                self.mcd.add_key(s[n:n + chainlen], s[n + chainlen])
            self.mcd.add_key(s[len(l):len(l) + chainlen], "\n")

    def getName(self):
        """
        New name from the Markov chain
        """
        prefix = " " * self.chainlen
        name = ""
        suffix = ""
        while True:
            suffix = self.mcd.get_suffix(prefix)
            if suffix == "\n" or len(name) > 9:
                break
            else:
                name = name + suffix
                prefix = prefix[1:] + suffix
        return name.capitalize()

    @staticmethod
    def name():
        return MName().getName()