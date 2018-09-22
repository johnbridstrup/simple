import copy
import importlib as port
import os
from collections import MutableMapping
import numpy as np
import numpy.random as npr
import pandas as pd
import statevector as sv

# noinspection Pylint
utils = port.import_module('utils.utes')


# noinspection PyBroadException,Pylint
class Data(MutableMapping):
    """
    some docs
    """
    def __init__(self, keys=['data'], data=None):
        if data is None:
            try:
                self._storage = {key: [] for key in keys}
            except:
                self._storage = {keys: []}
        else:
            try:
                assert (all(isinstance(x, dict) for x in data))
                self._storage = {}
                for key, item in zip(keys, data):
                    item.pop('name')
                    self._storage[key] = item
            except:
                try:
                    assert (all(isinstance(x, dict) for x in data))
                    self.storage = {}
                    for item in data:
                        name = item.pop('name')
                        self._storage[name] = item
                except:
                    try:
                        self._storage = {key: [dat] for key, dat in zip(keys, data)}
                    except:
                        try:
                            self._storage = {key: dat for key, dat in zip(keys, data)}
                        except:
                            if len(data) != len(keys):
                                print("data and key lists must be the same length")
                                raise ValueError

    def __setitem__(self, key, val):
        try:
            self._storage[key] = val
        except:
            try:
                if type(val) == list:
                    self._storage[key] = val
                else:
                    self._storage[key] = [val]
            except:
                raise TypeError
        self._storage[key] = val

    def __getitem__(self, key):
        return self._storage[key]

    def __delitem__(self, key, index=None):
        if index is None:
            del self._storage[key]
        else:
            del self._storage[key][index]

    def __iter__(self):
        return iter(self._storage)

    def __len__(self):
        return len(self._storage)

    def __str__(self):
        '''returns simple dict representation of the mapping'''
        return str(self._storage)

    def __repr__(self):
        """
            echoes class, id, & reproducible representation in the REPL
        """
        return '{}, Data({})'.format(super(Data, self).__repr__(),
                                     self._storage)

    def save(self, path=None):
        if path is None:
            try:
                os.makedirs(utils.wd() + '/results', mode=0o777, exist_ok=False)
            except:
                print("idk dude")
        df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in self._storage.items()]))
        # print(df)
        df.to_json(path)


class KMC:
    def __init__(self, statevec):
        self.stop_criteria = False
        self.steps = 0
        assert (type(statevec) == sv.StateVector)

    def reaction_propensities(self):
        pass

    def random_numbers(self):
        pass

    def generate_time_step(self):
        pass

    def determine_reaction(self):
        pass

    def update(self):
        pass

    def calculate_cumulative_function(self):
        pass

    def normalize_probability_function(self):
        pass

    def generate(self):
        pass


class Model:
    def __init__(self, state, nc):
        self.t_step = None
        self.nc = nc
        self.propensities = []
        self.operations = []
        self.frequencies = []
        self.mechanisms = None
        self.state = state
        self.P = []
        self.summed_P_vector = []
        self.indices = []
        self.data_list = ['polymers', 't_steps', 't']
        self.data = Data(keys=self.data_list)
        # self.data={}
        # self.data["mass"]=[]
        # self.data["number"]=[]
        # self.data["polymers"]=[]
        # self.data["skew"]=[]
        # self.data["kurtosis"]=[]
        # self.data["histogram"]=[]
        # self.data["t_steps"]=[]
        # self.data["t"]=[]
        # self.data["state"]=[]

    # @property
    # def nc(self):
    #     return self.nc
    # TODO these two need to be merged together, they are coupled way too strongly
    def add_propensity(self, props):
        try:
            for key, val in props.items:
                self.propensities.append(val)
        except:
            try:
                [self.propensities.append(item) for label, item in props.items()]
            except:
                try:
                    self.propensities.append(props)
                except:
                    # print('propensity adding is broked')
                    raise

    def add_mechanisms(self, mechs):
        self.mechanisms = mechs
        # print(self.mechanisms)

    def __repr__(self):
        return repr(self.data)

    def __str__(self):
        return str(dict(self.data))

    def calculate_probability(self):
        self.P = []
        self.summed_P_vector = []
        for i in self.propensities:
            # print(i(self.state.state))
            # print(i)
            self.P.append(i(self.state.state))
        for i in self.P:
            try:
                self.summed_P_vector.append(sum(i))
            except:
                self.summed_P_vector.append(i)

        norm = sum(self.summed_P_vector)
        # print(norm)
        self.norm_probability = [i / norm for i in self.summed_P_vector]
        # print(self.norm_probability)

    def ready(self):
        self.P = []
        self.indices = []
        # print(self.propensities)
        for ind, i in enumerate(self.propensities):
            # print(i)
            self.P.append([])
            prop_func = i[0]
            ar = i[1]
            try:
                if ar["Range_stop"] is True:
                    ar["range_stop"] = len(self.state.state)
            except:
                try:
                    if ar["Range"] is True:
                        ar["range"] = len(self.state.state)
                except:
                    try:
                        if ar["Reactant_range"] is True:
                            ar["reactant_range"] = len(self.state.state)
                    except:
                        pass
            num = len(self.state.state) - 1
            # print("FUCK",len(self.state.state)-1)
            try:
                outp = list(prop_func(self.state.state, self.state[0], polymer_number=num, **ar))
            except:
                outp = prop_func(self.state, self.state[0], polymer_number=num, **ar)

            self.P[ind].append(outp)

    def choose(self):
        self.choice = npr.choice(range(len(self.summed_P_vector)), p=self.norm_probability)
        # print(self.choice)

    def time_step(self):
        self.t_step = (1 / sum(self.summed_P_vector)) * np.log10(1 / npr.random())
        # print(self.t_step,"Time Step")

    def saveData(self, fn):

        self.df = pd.DataFrame(self.data)
        self.df.to_pickle("results")

    def advance(self):
        # print("CHOICE",self.choice)
        if self.choice == 0:
            self.mechanisms.run("add")
            # print("adding")
        if self.choice == 1:
            # print("subbing")
            self.mechanisms.run("subtract")
        if self.choice == 2:
            # print("nucleating")
            self.mechanisms.run("nucleate")
        if self.choice == 3:
            # print("break")
            self.mechanisms.run("break")
        # print("SUM",sum(self.state.state))
        if self.choice == 4:
            # print("merge")
            self.mechanisms.run("merge")

        self.data["polymers"].append(copy.deepcopy(self.state.state[:]))

        self.data["t_steps"].append(self.t_step)

    def save(self, path=None):

        for i, dt in enumerate(self.data['t_steps']):
            try:
                self.data['t'].append(self.data['t'][i - 1] + dt)
            except:
                self.data['t'] = [dt]
        if path is not None:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.data.save(path)
        else:
            path = utils.wd() + '/results'
            os.makedirs(path, exist_ok=True)
            self.data.save(path=path + '/default_')

    def stash(self):
        return self.data


if __name__ == '__main__':
    print("we in it")
