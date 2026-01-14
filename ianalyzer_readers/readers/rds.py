from typing import Iterable, Dict

import pyreadr
import pandas

from .core import Reader


class RDSReader(Reader):
    '''
    A base class for Readers that extract data from RDS files (containing serialised
    R dataframes).

    RDS files are parsed using the `pyreadr` library.

    Only file sources are supported. Row values can be extracted with the CSV extractor.
    '''

    def data_from_file(self, path) -> Iterable[Dict]:
        result = pyreadr.read_r(path)
        data: pandas.DataFrame = result['data']

        for _, row in data.iterrows():
            yield {index: value for index, value in row.items()}

    def iterate_data(self, data: Iterable[Dict], metadata):
        for row in data:
            yield {'rows': [row]} # format is for compatability with the CSV extractor
